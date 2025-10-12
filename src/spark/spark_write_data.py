from pyspark.sql import DataFrame
from pyspark.sql.connect.session import SparkSession
from pyspark.sql.functions import col
from database.mysql_connect import MySQLConnect
from database.mongodb_connect import MongoDBConnect
from config.spark_config import get_spark_config
from typing import Dict


class SparkWrite:
    def __init__(self, spark : SparkSession, config : Dict[str, str]):
        self.spark = spark
        self.config = config

    def spark_write_mysql(self, df : DataFrame, table_name: str, jdbc_url: str, config : Dict[str, str], mode : str = "append"):
        try:
            config_MySQL = config["mysql"]["config"]
            with MySQLConnect(config_MySQL["host"], config_MySQL["port"], config_MySQL["user"],
                              config_MySQL["password"], config_MySQL["database"]) as mysql:
                connection, cursor = mysql.connection, mysql.cursor
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN spark_temp VARCHAR(100)")
                connection.commit()
                mysql.close()
        except Exception as e:
            raise Exception(f"FAILED CONNECT TO MYSQL: {e}") from e

        df.write\
            .format("jdbc")\
            .option("dbtable", table_name)\
            .option("url", jdbc_url)\
            .option("driver", "com.mysql.cj.jdbc.Driver")\
            .option("user", config_MySQL["user"])\
            .option("password", config_MySQL["password"])\
            .mode(mode)\
            .save()

        print(f"SPARK WRITE SUCCESSFULLY: {table_name}")

    def validate_spark_mysql(self, df_write: DataFrame): # table_name: str, jdbc_url: str
        config_MySQL = self.config["mysql"]
        config = get_spark_config()
        table_name = config_MySQL["table"]
        jdbc_url = config_MySQL["jdbc_url"]
        df_read = self.spark.read \
            .format("jdbc") \
            .option("dbtable", f"(SELECT * FROM {table_name} WHERE spark_temp = 'spark_write') AS mysql") \
            .option("url", jdbc_url) \
            .option("driver", "com.mysql.cj.jdbc.Driver") \
            .option("user", config_MySQL["config"]["user"]) \
            .option("password", config_MySQL["config"]["password"]) \
            .load()

        result = df_write.exceptAll(df_read)

        if result.isEmpty():
            print(f"OK! {df_write.count()} RECORDS")
        else:
            num = result.count()

            result.write \
                .format("jdbc") \
                .option("dbtable", table_name) \
                .option("url", jdbc_url) \
                .option("driver", "com.mysql.cj.jdbc.Driver") \
                .option("user", config_MySQL["config"]["user"]) \
                .option("password", config_MySQL["config"]["password"]) \
                .mode("append") \
                .save()

            print("MISSING RECORDS")
            print(f"ADDED {num} RECORDS")

        try:
            config_MySQL = config["mysql"]["config"]
            with MySQLConnect(config_MySQL["host"], config_MySQL["port"], config_MySQL["user"],
                              config_MySQL["password"], config_MySQL["database"]) as mysql:
                connection, cursor = mysql.connection, mysql.cursor
                cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN spark_temp")
                connection.commit()
                mysql.close()
        except Exception as e:
            raise Exception(f"FAILED CONNECT TO MYSQL: {e}") from e

    def spark_write_mongodb(self, df : DataFrame, database : str, collection : str, uri : str, mode : str = "append" ):
        df.write\
            .format("mongo")\
            .option("uri", uri) \
            .option("database", database) \
            .option("collection", collection) \
            .mode(mode)\
            .save()

        print(f"SPARK WRITE SUCCESSFULLY: {database}.{collection}")

    def validate_spark_mongodb(self, df_write: DataFrame):
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
        result.show()

        if result.isEmpty():
            print(f"OK! {df_write.count()} RECORDS")
        else:
            num = result.count()

            result.write \
                .format("mongo") \
                .option("uri", self.config["mongodb"]["uri"]) \
                .option("database", self.config["mongodb"]["database"]) \
                .option("collection", "Users") \
                .mode("append") \
                .save()

            print("MISSING RECORDS")
            print(f"ADDED {num} RECORDS")

        with MongoDBConnect(self.config["mongodb"]["uri"], self.config["mongodb"]["database"]) as mongo:

            mongo.db.Users.update_many(
                {},
                {"$unset": {"spark_temp": ""}}
            )

    def write_all_db(self, df: DataFrame, mode: str = "append"):
        collection = "Users"
        #self.spark_write_mysql(df, self.config["mysql"]["table"], self.config["mysql"]["jdbc_url"], self.config)
        self.spark_write_mongodb(df, self.config["mongodb"]["database"], collection, self.config["mongodb"]["uri"], mode)

    def validate_all_db(self, df: DataFrame):
        #self.validate_spark_mysql(df)
        self.validate_spark_mongodb(df)