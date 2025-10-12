from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

data = [i for i in range(1, 11)]

rdd = sc.parallelize(data)

square_rdd = rdd.map(lambda x: x * x)
filter_rdd = rdd.filter(lambda x: x > 3)
flatmap_rdd = rdd.flatMap(lambda x: [x, x*2])

print(square_rdd.collect())
print(filter_rdd.collect())
print(flatmap_rdd.collect())

