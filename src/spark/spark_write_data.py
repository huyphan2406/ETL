from typing import Dict, Any
from pyspark.sql import DataFrame
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.functions import col
from database.mysql_connect import MySQLConnect
from database.mongodb_connect import MongoDBConnect
from src.utils.logger import get_logger
from src.utils.exceptions import DatabaseConnectionError, DatabaseOperationError, SparkJobError
from src.utils.constants import SPARK_TEMP_COLUMN, SPARK_TEMP_VALUE, DEFAULT_COLLECTION_NAME, WriteMode


class SparkWrite:
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config
        self.logger = get_logger("SparkWrite")
        # Cache MySQL config to avoid repeated calls
        self._mysql_config = None
        self._mongodb_config = None

    def _get_mysql_config(self) -> Dict[str, Any]:
        """Get and cache MySQL config."""
        if self._mysql_config is None:
            self._mysql_config = self.config["mysql"]["config"]
        return self._mysql_config

    def _check_column_exists(self, connection: Any, cursor: Any, table_name: str, column_name: str) -> bool:
        """Check if column exists in table."""
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE '{column_name}'")
            return cursor.fetchone() is not None
        except Exception as e:
            self.logger.warning(f"Error checking column existence: {e}")
            return False

    def spark_write_mysql(self, df: DataFrame, table_name: str, jdbc_url: str, config: Dict[str, Any], mode: str = WriteMode.APPEND.value) -> None:
        """Write DataFrame to MySQL table."""
        try:
            config_MySQL = config["mysql"]["config"]
            with MySQLConnect(config_MySQL["host"], config_MySQL["port"], config_MySQL["user"],
                              config_MySQL["password"], config_MySQL["database"]) as mysql:
                connection, cursor = mysql.connection, mysql.cursor
                # Check if column exists before adding
                if not self._check_column_exists(connection, cursor, table_name, SPARK_TEMP_COLUMN):
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {SPARK_TEMP_COLUMN} VARCHAR(100)")
                    connection.commit()
                    self.logger.info(f"Added temporary column {SPARK_TEMP_COLUMN} to {table_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MySQL: {e}")
            raise DatabaseConnectionError(f"Failed to connect to MySQL: {e}") from e

        try:
            df.write\
                .format("jdbc")\
                .option("dbtable", table_name)\
                .option("url", jdbc_url)\
                .option("driver", "com.mysql.cj.jdbc.Driver")\
                .option("user", config_MySQL["user"])\
                .option("password", config_MySQL["password"])\
                .mode(mode)\
                .save()
            self.logger.info(f"Successfully wrote {df.count()} records to MySQL table: {table_name}")
        except Exception as e:
            self.logger.error(f"Failed to write to MySQL: {e}")
            raise SparkJobError(f"Failed to write to MySQL: {e}") from e

    def validate_spark_mysql(self, df_write: DataFrame) -> None:
        """Validate data written to MySQL and add missing records."""
        config_MySQL = self.config["mysql"]
        table_name = config_MySQL["table"]
        jdbc_url = config_MySQL["jdbc_url"]
        mysql_config = self._get_mysql_config()
        
        try:
            df_read = self.spark.read \
                .format("jdbc") \
                .option("dbtable", f"(SELECT * FROM {table_name} WHERE {SPARK_TEMP_COLUMN} = '{SPARK_TEMP_VALUE}') AS mysql") \
                .option("url", jdbc_url) \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .option("user", mysql_config["user"]) \
                .option("password", mysql_config["password"]) \
                .load()

            result = df_write.exceptAll(df_read)

            if result.isEmpty():
                record_count = df_write.count()
                self.logger.info(f"Validation successful: {record_count} records match")
            else:
                num = result.count()
                self.logger.warning(f"Found {num} missing records, adding them...")

                result.write \
                    .format("jdbc") \
                    .option("dbtable", table_name) \
                    .option("url", jdbc_url) \
                    .option("driver", "com.mysql.cj.jdbc.Driver") \
                    .option("user", mysql_config["user"]) \
                    .option("password", mysql_config["password"]) \
                    .mode(WriteMode.APPEND.value) \
                    .save()

                self.logger.info(f"Added {num} missing records to {table_name}")

            # Clean up temporary column
            try:
                with MySQLConnect(mysql_config["host"], mysql_config["port"], mysql_config["user"],
                                  mysql_config["password"], mysql_config["database"]) as mysql:
                    connection, cursor = mysql.connection, mysql.cursor
                    if self._check_column_exists(connection, cursor, table_name, SPARK_TEMP_COLUMN):
                        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {SPARK_TEMP_COLUMN}")
                        connection.commit()
                        self.logger.info(f"Removed temporary column {SPARK_TEMP_COLUMN} from {table_name}")
            except Exception as e:
                self.logger.warning(f"Failed to remove temporary column: {e}")
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            raise DatabaseOperationError(f"Validation failed: {e}") from e

    def spark_write_mongodb(self, df: DataFrame, database: str, collection: str, uri: str, mode: str = WriteMode.APPEND.value) -> None:
        """Write DataFrame to MongoDB collection."""
        try:
            df.write\
                .format("mongo")\
                .option("uri", uri) \
                .option("database", database) \
                .option("collection", collection) \
                .mode(mode)\
                .save()
            self.logger.info(f"Successfully wrote {df.count()} records to MongoDB: {database}.{collection}")
        except Exception as e:
            self.logger.error(f"Failed to write to MongoDB: {e}")
            raise SparkJobError(f"Failed to write to MongoDB: {e}") from e

    def validate_spark_mongodb(self, df_write: DataFrame) -> None:
        """Validate data written to MongoDB and add missing records."""
        try:
            df = self.spark.read \
                .format("mongo") \
                .option("uri", self.config["mongodb"]["uri"]) \
                .option("database", self.config["mongodb"]["database"]) \
                .option("collection", DEFAULT_COLLECTION_NAME) \
                .load()

            df_read = df.select(
                col("user_id"),
                col("login"),
                col("gravatar_id"),
                col("avatar_url"),
                col("url"),
                col(SPARK_TEMP_COLUMN)
            )

            result = df_write.exceptAll(df_read)

            if result.isEmpty():
                record_count = df_write.count()
                self.logger.info(f"Validation successful: {record_count} records match")
            else:
                num = result.count()
                self.logger.warning(f"Found {num} missing records, adding them...")

                result.write \
                    .format("mongo") \
                    .option("uri", self.config["mongodb"]["uri"]) \
                    .option("database", self.config["mongodb"]["database"]) \
                    .option("collection", DEFAULT_COLLECTION_NAME) \
                    .mode(WriteMode.APPEND.value) \
                    .save()

                self.logger.info(f"Added {num} missing records to MongoDB")

            # Clean up temporary field
            with MongoDBConnect(self.config["mongodb"]["uri"], self.config["mongodb"]["database"]) as mongo:
                mongo.db[DEFAULT_COLLECTION_NAME].update_many(
                    {},
                    {"$unset": {SPARK_TEMP_COLUMN: ""}}
                )
                self.logger.info(f"Removed temporary field {SPARK_TEMP_COLUMN} from MongoDB")
        except Exception as e:
            self.logger.error(f"MongoDB validation failed: {e}")
            raise DatabaseOperationError(f"MongoDB validation failed: {e}") from e

    def write_all_db(self, df: DataFrame, mode: str = WriteMode.APPEND.value) -> None:
        """Write DataFrame to all configured databases."""
        collection = DEFAULT_COLLECTION_NAME
        # MySQL write can be enabled by uncommenting:
        # self.spark_write_mysql(df, self.config["mysql"]["table"], self.config["mysql"]["jdbc_url"], self.config, mode)
        self.spark_write_mongodb(df, self.config["mongodb"]["database"], collection, self.config["mongodb"]["uri"], mode)

    def validate_all_db(self, df: DataFrame) -> None:
        """Validate data in all configured databases."""
        # MySQL validation can be enabled by uncommenting:
        # self.validate_spark_mysql(df)
        self.validate_spark_mongodb(df)