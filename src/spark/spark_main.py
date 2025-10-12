from config.spark_config import SparkConnect, get_spark_config
from config.database_config import get_database_config
from pyspark.sql.types import *
from src.spark.spark_write_data import SparkWrite
from pyspark.sql.functions import col, lit


def main():
    config = get_database_config()
    spark_config = get_spark_config()

    jars = [config["mysql"].jar_path]

    spark_conf = {
        "spark.jars.packages": "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
    }

    spark_write_database = SparkConnect(
        app_name="huydz123",
        master_url="local[*]",
        executor_memory='4g',
        executor_cores=2,
        driver_memory='2g',
        num_executor=3,
        jars=jars,
        spark_conf=spark_conf,
        log_level="INFO"
    ).spark #create_spark_session()

    schema = StructType([
        StructField("actor", StructType([
            StructField("id", LongType(), nullable=False),
            StructField("login", StringType(), nullable=True),
            StructField("gravatar_id", StringType(), nullable=True),
            StructField("url", StringType(), nullable=True),
            StructField("avatar_url", StringType(), nullable=True),
        ]), nullable=True),
        StructField("repo", StructType([
            StructField("id", LongType(), nullable=False),
            StructField("name", StringType(), nullable=True),
            StructField("url", StringType(), nullable=True),
        ]), nullable=True),
    ])

    df = spark_write_database.read.schema(schema).json(r"C:/Users/Laptop/PycharmProjects/DE/data/JsonFile.json")

    df_write_table = df.withColumn('spark_temp', lit('spark_write')).select(
        col('actor.id').cast("string").alias('user_id'),
        col('actor.login').alias('login'),
        col('actor.gravatar_id').alias('gravatar_id'),
        col('actor.avatar_url').alias('avatar_url'),
        col('actor.url').alias('url'),
        col('spark_temp').alias('spark_temp')
    )

    # df_write = SparkWrite(spark_write_database, spark_config)
    # df_write.write_all_db(df_write_table, mode = "append")

    df_validate = SparkWrite(spark_write_database, spark_config)
    df_validate.validate_all_db(df_write_table)

    spark_write_database.stop()

if __name__ == "__main__":
    main()