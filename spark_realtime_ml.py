from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator
import os

# Kafka connection (Docker or local)
kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Create Spark session with compatible Kafka connector for PySpark 4.1.0
spark = SparkSession.builder \
    .appName("BitcoinRealtimeML") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.0") \
    .config("spark.sql.streaming.checkpointLocation", "./checkpoint") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print(f"🚀 Starting Bitcoin Real-time ML Pipeline... Connecting to Kafka at {kafka_servers}")

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
    .option("kafka.bootstrap.servers", kafka_servers) \
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
    
    # Train Gradient Boosting Regressor model
    gbt = GBTRegressor(
        labelCol="label",
        featuresCol="features",
        maxDepth=5,                    # Depth of trees
        maxBins=32,                    # Number of bins for feature discretization
        numTrees=20,                   # Number of boosting stages
        stepSize=0.1,                  # Learning rate
        seed=42
    )
    model = gbt.fit(train_data)
    
    # Evaluate on test data
    predictions = model.transform(test_data)
    evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="rmse")
    rmse = evaluator.evaluate(predictions)
    
    # Also calculate MAE for better insight
    mae_evaluator = RegressionEvaluator(labelCol="label", predictionCol="prediction", metricName="mae")
    mae = mae_evaluator.evaluate(predictions)
    
    print(f"✅ Batch {batch_id} - GBT Model trained!")
    print(f"   📈 RMSE: {rmse:.2f}")
    print(f"   📊 MAE: {mae:.2f}")
    print(f"   🌳 Number of trees: {model.numTrees}")
    print(f"   📋 Feature importances: {[f'{v:.4f}' for v in model.featureImportances.toArray()]}")
    
    # Save model (overwrite with latest)
    model_path = "./bitcoin_model"
    try:
        model.write().overwrite().save(model_path)
        print(f"   💾 Model saved to {model_path}")
        
        # Also save metadata
        with open("./model_metrics.txt", "w") as f:
            f.write(f"Model: GradientBoosting Regressor\n")
            f.write(f"RMSE: {rmse}\n")
            f.write(f"MAE: {mae}\n")
            f.write(f"Trees: {model.numTrees}\n")
            f.write(f"Max Depth: 5\n")
            f.write(f"Feature Importances: {model.featureImportances.toArray()}\n")
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
