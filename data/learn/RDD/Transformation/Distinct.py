from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

data = sc.parallelize([1, 2, 3, "one", "two", "three", 2, 3, "two", "three"])

Distinct_RDD = data.distinct()

print(Distinct_RDD.collect())
