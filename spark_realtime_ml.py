from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator
import os

# Create Spark session with compatible Kafka connector for PySpark 4.1.0
spark = SparkSession.builder \
    .appName("BitcoinRealtimeML") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.0") \
    .config("spark.sql.streaming.checkpointLocation", "./checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("🚀 Starting Bitcoin Real-time ML Pipeline...")

# JSON Schema (removed marketcap)
schema = StructType([
    StructField("date", StringType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", DoubleType(), True)
])

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "bitcoin_prices") \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON
json_df = df.selectExpr("CAST(value AS STRING) as json_value")
parsed_df = json_df.select(from_json(col("json_value"), schema).alias("data")).select("data.*")

# Clean data - remove nulls
clean_df = parsed_df.dropna()

print("✅ Data cleaning applied")

# Prepare features for ML
feature_cols = ["open", "high", "low", "volume"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Function to train model on each batch
def train_and_save_model(batch_df, batch_id):
    if batch_df.count() == 0:
        print(f"⚠️  Batch {batch_id}: No data")
        return
    
    print(f"\n📊 Processing Batch {batch_id} with {batch_df.count()} records")
    
    # Prepare features
    data = assembler.transform(batch_df)
    final_data = data.select("features", col("close").alias("label"))
    
    # Split data
    train_data, test_data = final_data.randomSplit([0.8, 0.2], seed=42)
    
    if train_data.count() < 2 or test_data.count() < 1:
        print(f"⚠️  Batch {batch_id}: Not enough data for training")
        return
    
    # Train model
    lr = LinearRegression(featuresCol="features", labelCol="label")
    model = lr.fit(train_data)
    
    # Evaluate on test data
    predictions = model.transform(test_data)
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    
    print(f"✅ Batch {batch_id} - Model trained!")
    print(f"   📈 RMSE: {rmse:.2f}")
    print(f"   📊 Coefficients: {model.coefficients}")
    print(f"   🎯 Intercept: {model.intercept:.2f}")
    
    # Save model (overwrite with latest)
    model_path = "./bitcoin_model"
    try:
        model.write().overwrite().save(model_path)
        print(f"   💾 Model saved to {model_path}")
        
        # Also save metadata
        with open("./model_metrics.txt", "w") as f:
            f.write(f"RMSE: {rmse}\n")
            f.write(f"Coefficients: {model.coefficients}\n")
            f.write(f"Intercept: {model.intercept}\n")
            f.write(f"Batch: {batch_id}\n")
    except Exception as e:
        print(f"   ⚠️  Error saving model: {e}")

# Write stream with foreachBatch to train model
query = clean_df.writeStream \
    .foreachBatch(train_and_save_model) \
    .outputMode("update") \
    .start()

print("✅ Streaming pipeline started!")
print("📡 Listening to Kafka topic 'bitcoin_prices'...")
print("🤖 Training model on each batch...")

query.awaitTermination()
