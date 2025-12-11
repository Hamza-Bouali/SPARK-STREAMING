from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Spark session
spark = SparkSession.builder \
    .appName("BitcoinPreprocessing") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 1️⃣ Read raw data
df = spark.read.csv("coin_Bitcoin.csv", header=True, inferSchema=True)

print("📌 Raw Data:")
df.show(5)

# 2️⃣ Remove missing values
df_clean = df.dropna()

# 3️⃣ Select necessary columns
df_clean = df_clean.select(
    col("Open"),
    col("High"),
    col("Low"),
    col("Close"),
    col("Volume")
)

print("✅ Data After Preprocessing:")
df_clean.show(5)

# 4️⃣ Save the cleaned data
df_clean.write.mode("overwrite").csv("clean_bitcoin", header=True)

print("✅ Clean data has been saved to the 'clean_bitcoin' directory.")
