import time
from random import Random
from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

data = ["Huy", "Long", "Pha", "Khoa", "Vinh"]

rdd = sc.parallelize(data, 3)

def partition(iterator):
    rand = Random(int(time.time() * 1000) + Random().randint(0, 1000))
    return [f"{item}:{rand.randint(0, 1000)}" for item in iterator]

result = rdd.mapPartitions(partition)

print(result.collect())