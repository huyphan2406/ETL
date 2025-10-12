from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import *
from pyspark.sql.functions import udf, split
from pyspark.sql.functions import col
from pyspark.sql.functions import lit
from pyspark.sql.functions import struct
import re


spark = SparkSession.builder \
    .appName("data Engineer") \
    .master("local[*]") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

schema = StructType([
    StructField("id", StringType()),
    StructField("type", StringType()),
    StructField("actor", StructType([
        StructField("id", IntegerType()),
        StructField("login", StringType()),
        StructField("gravatar_id", StringType()),
        StructField("url", StringType()),
        StructField("avatar_url", StringType())])),
    StructField("repo", StructType([
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("url", StringType()),
    ])),
    StructField("payload", StructType([
        StructField("action", StringType()),
        StructField("issue", StructType([
            StructField("url", StringType()),
            StructField("labels_url", StringType()),
            StructField("comments_url", StringType()),
            StructField("events_url", StringType()),
            StructField("html_url", StringType()),
            StructField("id", IntegerType()),
            StructField("number", IntegerType()),
            StructField("title", StringType()),
            StructField("user", StructType([
                StructField("login", StringType()),
                StructField("id", IntegerType()),
                StructField("avatar_url", StringType()),
                StructField("gravatar", StringType()),
                StructField("url", StringType()),
                StructField("html_url", StringType()),
                StructField("followers_url", StringType()),
                StructField("following_url", StringType()),
                StructField("gists_url", StringType()),
                StructField("starred_url", StringType()),
                StructField("subscriptions_url", StringType()),
                StructField("organizations_url", StringType()),
                StructField("repos_url", StringType()),
                StructField("events_url", StringType()),
                StructField("received_events_url", StringType()),
                StructField("User", StringType()),
                StructField("site_admin", BooleanType()),
            ])),
            StructField("labels", StructType([
                StructField("url", StringType()),
                StructField("name", StringType()),
                StructField("color", StringType()),
            ])),
            StructField("state", StringType()),
            StructField("locked", BooleanType()),
            StructField("assignee", StringType()),
            StructField("milestone", StringType()),
            StructField("comments", IntegerType()),
            StructField("created_at", StringType()),
            StructField("updated_at", StringType()),
            StructField("closed_at", StringType()),
            StructField("body", StringType()),
        ]))
    ])),
    StructField("public", BooleanType()),
    StructField("created_at", StringType())
])

JsonData = spark.read.schema(schema).json("C:/Users/Laptop/Desktop/JsonFile.json")

data = [("11/12/2025",),("27/02.2014",),("2023.01.09",),("28-12-2005",)]
df = spark.createDataFrame(data , ["date"])

def solution(dt):
        date = re.split(r"[-./]", dt)
        day, month, year = date
        if len(date[0]) == 4:
            year, month, day = date
            return {"day": day, "month": month, "year": year}
        return {"day": day, "month": month, "year": year}

solution_udf = udf(solution,
              StructType([
                StructField("day", StringType()),
                StructField("month", StringType()),
                StructField("year", StringType())
              ]))

new_data = df.withColumn("new_data", solution_udf(col("date"))) \
    .select(col("date"), col("new_data.day"), col("new_data.month"), col("new_data.year"))
new_data.show(truncate=False)







