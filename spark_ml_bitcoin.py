from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

# -----------------------------
# 1️⃣ Start Spark Session
# -----------------------------
spark = SparkSession.builder \
    .appName("Bitcoin_ML_Pipeline") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# -----------------------------
# 2️⃣ Load Cleaned Data
# -----------------------------
df = spark.read.csv("clean_bitcoin", header=True, inferSchema=True)

print("✅ Clean Data:")
df.show(5)

# -----------------------------
# 3️⃣ Select Features & Label
# -----------------------------
# Target variable to predict: close
# Input features: open, high, low, volume

feature_cols = ["open", "high", "low", "volume"]

assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features"
)

data = assembler.transform(df)

final_data = data.select("features", col("close").alias("label"))

print("✅ Features & Label Ready:")
final_data.show(5)

# -----------------------------
# 4️⃣ Train / Test Split
# -----------------------------
train_data, test_data = final_data.randomSplit([0.8, 0.2], seed=42)

print("✅ Train Count:", train_data.count())
print("✅ Test Count:", test_data.count())

# -----------------------------
# 5️⃣ Linear Regression Model
# -----------------------------
lr = LinearRegression(
    featuresCol="features",
    labelCol="label"
)

model = lr.fit(train_data)

# -----------------------------
# 6️⃣ Generate Predictions
# -----------------------------
predictions = model.transform(test_data)

print("✅ Prediction Results:")
predictions.select("label", "prediction").show(10)

# -----------------------------
# 7️⃣ Model Evaluation (RMSE)
# -----------------------------
evaluator = RegressionEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="rmse"
)

rmse = evaluator.evaluate(predictions)

print(f"✅ Model RMSE Error Value: {rmse}")

# -----------------------------
# 8️⃣ Model Coefficients (IMPORTANT)
# -----------------------------
print("✅ Model Coefficients:", model.coefficients)
print("✅ Model Bias (Intercept):", model.intercept)

spark.stop()
