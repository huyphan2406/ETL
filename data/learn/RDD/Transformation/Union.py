from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

rdd1 = sc.parallelize(["Huy"])
rdd2 = sc.parallelize([1, 3, 5, 7, 9])

rdd3 = rdd1.union(rdd2)

print(rdd3.collect())