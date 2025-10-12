from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

data = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

s= []

def sum(x1: int, x2: int) -> int:
    return x1 + x2

print(data.reduce(sum))