from pathlib import Path
from config.spark_config import SparkConnect, get_spark_config
from config.database_config import get_database_config
from pyspark.sql.types import *
from src.spark.spark_write_data import SparkWrite
from pyspark.sql.functions import col, lit

# simple etl
def main():
    config = get_database_config()
    spark_config = get_spark_config()

    jars = [config["mysql"].jar_path] if config["mysql"].jar_path else []

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
    ).spark

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

    json_file_path = Path(__file__).resolve().parent.parent.parent / "data" / "sample_data.json"
    df = spark_write_database.read.schema(schema).json(str(json_file_path))

    df_write_table = df.withColumn("spark_temp", lit("spark_write")).select(
        col('actor.id').cast("string").alias('user_id'),
        col('actor.login').alias('login'),
        col('actor.gravatar_id').alias('gravatar_id'),
        col('actor.avatar_url').alias('avatar_url'),
        col('actor.url').alias('url'),
        col("spark_temp").alias("spark_temp")
    )

    # Validate data
    df_validate = SparkWrite(spark_write_database, spark_config)
    df_validate.validate_all_db(df_write_table)

    spark_write_database.stop()

if __name__ == "__main__":
    main()