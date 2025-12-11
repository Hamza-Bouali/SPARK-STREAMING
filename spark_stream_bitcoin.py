from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Spark session
spark = SparkSession.builder \
    .appName("BitcoinKafkaStream") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- JSON Schema ---
schema = StructType([
    StructField("date", StringType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("marketcap", DoubleType(), True)
])

# --- Kafka Stream ---
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "bitcoin_prices") \
    .load()

# Convert Kafka message to string
json_df = df.selectExpr("CAST(value AS STRING)")

# Parse JSON -> columns
parsed_df = json_df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Output to console
query = parsed_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()
