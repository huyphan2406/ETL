from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("data Enginner").setMaster("local[*]").set("spark.executor.memory", "4g")

sc = SparkContext(conf = conf)

FileRDD = sc.textFile(r"C:\Users\Laptop\PycharmProjects\DE\Data\TextFile.txt")

Split_RDD = FileRDD.flatMap(lambda line: line.split(" "))

print(Split_RDD.collect())