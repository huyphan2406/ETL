from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

FileRDD = sc.textFile(r"C:\Users\Laptop\PycharmProjects\DE\Data\TextFile.txt")

Upper_RDD = FileRDD.map(lambda line: line.upper())

print(Upper_RDD.collect())