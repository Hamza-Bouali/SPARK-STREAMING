from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyspark.sql import SparkSession
from pyspark.ml.regression import LinearRegressionModel
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors
import os
from typing import List

app = FastAPI(title="Bitcoin Price Prediction API", version="1.0.0")

# Initialize Spark session
spark = None
model = None
model_path = "./bitcoin_model"

def init_spark():
    global spark
    if spark is None:
        spark = SparkSession.builder \
            .appName("BitcoinPredictionAPI") \
            .getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
    return spark

def load_model():
    global model
    try:
        if os.path.exists(model_path):
            spark = init_spark()
            model = LinearRegressionModel.load(model_path)
            print("✅ Model loaded successfully")
            return True
        else:
            print("⚠️  Model not found. Please train the model first.")
            return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

# Request model
class PredictionRequest(BaseModel):
    open: float
    high: float
    low: float
    volume: float

class PredictionResponse(BaseModel):
    predicted_close: float
    input_features: dict
    model_available: bool

class BatchPredictionRequest(BaseModel):
    data: List[PredictionRequest]

class BatchPredictionResponse(BaseModel):
    predictions: List[float]
    count: int

class ModelMetrics(BaseModel):
    rmse: float = None
    coefficients: List[float] = None
    intercept: float = None
    batch: int = None
    available: bool

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    init_spark()
    load_model()

@app.get("/")
async def root():
    return {
        "message": "Bitcoin Price Prediction API",
        "status": "running",
        "model_loaded": model is not None,
        "endpoints": {
            "predict": "/predict",
            "batch_predict": "/batch_predict",
            "model_info": "/model/info",
            "reload_model": "/model/reload",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "spark_session": spark is not None,
        "model_loaded": model is not None
    }

@app.post("/model/reload")
async def reload_model():
    """Reload the model from disk"""
    success = load_model()
    return {
        "success": success,
        "model_loaded": model is not None,
        "message": "Model reloaded successfully" if success else "Failed to reload model"
    }

@app.get("/model/info", response_model=ModelMetrics)
async def get_model_info():
    """Get current model metrics"""
    if model is None:
        return ModelMetrics(available=False)
    
    try:
        # Read metrics file if exists
        metrics_file = "/tmp/model_metrics.txt"
        if os.path.exists(metrics_file):
            with open(metrics_file, "r") as f:
                lines = f.readlines()
                metrics = {}
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metrics[key.strip()] = value.strip()
                
                return ModelMetrics(
                    available=True,
                    rmse=float(metrics.get("RMSE", 0)),
                    coefficients=[float(x) for x in metrics.get("Coefficients", "[]").strip("[]").split(",") if x],
                    intercept=float(metrics.get("Intercept", 0)),
                    batch=int(metrics.get("Batch", 0))
                )
    except Exception as e:
        print(f"Error reading metrics: {e}")
    
    return ModelMetrics(
        available=True,
        coefficients=model.coefficients.toArray().tolist() if model else [],
        intercept=float(model.intercept) if model else 0.0
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make a single prediction"""
    if model is None:
        # Try to load model
        if not load_model():
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please train the model first by running the streaming pipeline."
            )
    
    try:
        # Create feature vector
        features = Vectors.dense([request.open, request.high, request.low, request.volume])
        
        # Create DataFrame for prediction
        data = [(features,)]
        df = spark.createDataFrame(data, ["features"])
        
        # Make prediction
        predictions = model.transform(df)
        predicted_value = predictions.select("prediction").collect()[0][0]
        
        return PredictionResponse(
            predicted_close=float(predicted_value),
            input_features={
                "open": request.open,
                "high": request.high,
                "low": request.low,
                "volume": request.volume
            },
            model_available=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/batch_predict", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest):
    """Make predictions for multiple records"""
    if model is None:
        if not load_model():
            raise HTTPException(
                status_code=503,
                detail="Model not available. Please train the model first."
            )
    
    try:
        # Create feature vectors
        features_list = [
            (Vectors.dense([item.open, item.high, item.low, item.volume]),)
            for item in request.data
        ]
        
        # Create DataFrame
        df = spark.createDataFrame(features_list, ["features"])
        
        # Make predictions
        predictions = model.transform(df)
        predicted_values = [float(row.prediction) for row in predictions.select("prediction").collect()]
        
        return BatchPredictionResponse(
            predictions=predicted_values,
            count=len(predicted_values)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
