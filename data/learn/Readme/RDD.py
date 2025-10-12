from pyspark import SparkContext, SparkConf

conf = SparkConf().setAppName("Dat dep zai").setMaster("local[*]").set("spark.executor.memory","4g")

sc = SparkContext(conf=conf)