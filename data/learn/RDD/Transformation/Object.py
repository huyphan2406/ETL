from pyspark import SparkContext

sc = SparkContext("local", "data Engineer")

data = [
    {"id": 1, "name": "Huy"},
    {"id": 2, "name": "Long"},
    {"id": 3, "name": "Pha"}
]

rdd = sc.parallelize(data)

print(rdd.collect())