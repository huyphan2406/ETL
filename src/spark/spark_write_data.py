from typing import Dict, Any
from pyspark.sql import DataFrame
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.functions import col
from database.mysql_connect import MySQLConnect
from database.mongodb_connect import MongoDBConnect

# spark functions
class SparkWrite:
    def __init__(self, spark: SparkSession, config: Dict[str, Any]):
        self.spark = spark
        self.config = config

    def spark_write_mysql(self, df: DataFrame, table_name: str, jdbc_url: str, config: Dict[str, Any], mode: str = "append"):
        try:
            config_MySQL = config["mysql"]["config"]
            with MySQLConnect(config_MySQL["host"], config_MySQL["port"], config_MySQL["user"],
                              config_MySQL["password"], config_MySQL["database"]) as mysql:
                connection, cursor = mysql.connection, mysql.cursor
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN spark_temp VARCHAR(100)")
                connection.commit()
        except Exception as e:
            print(f"Failed to connect to MySQL: {e}")

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
        except Exception as e:
            print(f"Failed to write to MySQL: {e}")

    def validate_spark_mysql(self, df_write: DataFrame):
        config_MySQL = self.config["mysql"]
        table_name = config_MySQL["table"]
        jdbc_url = config_MySQL["jdbc_url"]
        mysql_config = self.config["mysql"]["config"]
        
        try:
            df_read = self.spark.read \
                .format("jdbc") \
                .option("dbtable", f"(SELECT * FROM {table_name} WHERE spark_temp = 'spark_write') AS mysql") \
                .option("url", jdbc_url) \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .option("user", mysql_config["user"]) \
                .option("password", mysql_config["password"]) \
                .load()

            result = df_write.exceptAll(df_read)

            if result.isEmpty():
                print("Validation successful")
            else:
                num = result.count()
                print(f"Found {num} missing records, adding them...")

                result.write \
                    .format("jdbc") \
                    .option("dbtable", table_name) \
                    .option("url", jdbc_url) \
                    .option("driver", "com.mysql.cj.jdbc.Driver") \
                    .option("user", mysql_config["user"]) \
                    .option("password", mysql_config["password"]) \
                    .mode("append") \
                    .save()

                print(f"Added {num} missing records to {table_name}")

            # Clean up temporary column
            try:
                with MySQLConnect(mysql_config["host"], mysql_config["port"], mysql_config["user"],
                                  mysql_config["password"], mysql_config["database"]) as mysql:
                    connection, cursor = mysql.connection, mysql.cursor
                    cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN spark_temp")
                    connection.commit()
            except Exception as e:
                print(f"Failed to remove temporary column: {e}")
        except Exception as e:
            print(f"Validation failed: {e}")

    def spark_write_mongodb(self, df: DataFrame, database: str, collection: str, uri: str, mode: str = "append"):
        try:
            df.write\
                .format("mongo")\
                .option("uri", uri) \
                .option("database", database) \
                .option("collection", collection) \
                .mode(mode)\
                .save()
        except Exception as e:
            print(f"Failed to write to MongoDB: {e}")

    def validate_spark_mongodb(self, df_write: DataFrame):
        try:
            df = self.spark.read \
                .format("mongo") \
                .option("uri", self.config["mongodb"]["uri"]) \
                .option("database", self.config["mongodb"]["database"]) \
                .option("collection", "Users") \
                .load()

            df_read = df.select(
                col("user_id"),
                col("login"),
                col("gravatar_id"),
                col("avatar_url"),
                col("url"),
                col("spark_temp")
            )

            result = df_write.exceptAll(df_read)

            if result.isEmpty():
                print("Validation successful")
            else:
                num = result.count()
                print(f"Found {num} missing records, adding them...")

                result.write \
                    .format("mongo") \
                    .option("uri", self.config["mongodb"]["uri"]) \
                    .option("database", self.config["mongodb"]["database"]) \
                    .option("collection", "Users") \
                    .mode("append") \
                    .save()

                print(f"Added {num} missing records to MongoDB")

            # Clean up temporary field
            with MongoDBConnect(self.config["mongodb"]["uri"], self.config["mongodb"]["database"]) as mongo:
                mongo.db["Users"].update_many(
                    {},
                    {"$unset": {"spark_temp": ""}}
                )
        except Exception as e:
            print(f"MongoDB validation failed: {e}")

    def write_all_db(self, df: DataFrame, mode: str = "append"):
        #self.spark_write_mysql(df, self.config["mysql"]["table"], self.config["mysql"]["jdbc_url"], self.config, mode)
        self.spark_write_mongodb(df, self.config["mongodb"]["database"], "Users", self.config["mongodb"]["uri"], mode)

    def validate_all_db(self, df: DataFrame):
        #self.validate_spark_mysql(df)
        self.validate_spark_mongodb(df)
