from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("data Engineer") \
    .master("local[*]") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

# rdd = spark.sparkContext.parallelize()
# scheme = StructType()
# dataframe = spark.createDataFrame(rdd, scheme)

#json = spark.read.json("C:/Users/Laptop/Desktop/JsonFile.json")
#json.show()
#json.printSchema()
