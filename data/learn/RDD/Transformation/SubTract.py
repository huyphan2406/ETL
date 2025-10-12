from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

word = sc.parallelize(["anh yeu em nhat ma"]) \
    .flatMap(lambda w: w.split(" "))

stopword = sc.parallelize(["nhat ma"]) \
    .flatMap(lambda w: w.split(" "))

finalword = word.subtract(stopword)

print(finalword.collect())