from pyspark.sql import SparkSession
from pyspark.sql.types import *

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
JsonData.show(truncate=False)
JsonData.printSchema()