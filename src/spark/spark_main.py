from pathlib import Path
from config.spark_config import SparkConnect, get_spark_config
from config.database_config import get_database_config
from pyspark.sql.types import *
from src.spark.spark_write_data import SparkWrite
from pyspark.sql.functions import col, lit
from src.utils.logger import get_logger
from src.utils.constants import SPARK_TEMP_COLUMN, SPARK_TEMP_VALUE, DEFAULT_SPARK_APP_NAME


def main() -> None:
    """Main function for Spark ETL pipeline."""
    logger = get_logger("SparkMain")
    logger.info("Starting Spark ETL pipeline")
    
    config = get_database_config()
    spark_config = get_spark_config()

    jars = [config["mysql"].jar_path] if config["mysql"].jar_path else []

    spark_conf = {
        "spark.jars.packages": "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1",
    }

    spark_write_database = SparkConnect(
        app_name=DEFAULT_SPARK_APP_NAME,
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
    logger.info(f"Reading JSON file: {json_file_path}")
    df = spark_write_database.read.schema(schema).json(str(json_file_path))

    df_write_table = df.withColumn(SPARK_TEMP_COLUMN, lit(SPARK_TEMP_VALUE)).select(
        col('actor.id').cast("string").alias('user_id'),
        col('actor.login').alias('login'),
        col('actor.gravatar_id').alias('gravatar_id'),
        col('actor.avatar_url').alias('avatar_url'),
        col('actor.url').alias('url'),
        col(SPARK_TEMP_COLUMN).alias(SPARK_TEMP_COLUMN)
    )

    logger.info(f"Transformed {df_write_table.count()} records")

    # Write to databases (commented out by default)
    # df_write = SparkWrite(spark_write_database, spark_config)
    # df_write.write_all_db(df_write_table, mode="append")

    # Validate data
    df_validate = SparkWrite(spark_write_database, spark_config)
    df_validate.validate_all_db(df_write_table)

    spark_write_database.stop()
    logger.info("Spark ETL pipeline completed")

if __name__ == "__main__":
    main()