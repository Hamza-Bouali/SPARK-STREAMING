# Bitcoin Real-time ML Pipeline

End-to-end demo: stream BTC-USD prices into Kafka, train a per-batch Gradient Boosting Tree regressor with Spark Structured Streaming, surface metrics to a Streamlit dashboard, and expose an optional FastAPI endpoint for predictions.

## Architecture (Compose)
- Kafka + Zookeeper (Confluent) for ingestion
- Spark 4.1.0 Structured Streaming + MLlib GBTRegressor (20 iterations, maxDepth 5)
- Producer (yfinance → Kafka) simulating live ticks
- Dashboard (Streamlit) reading on-disk metrics/history
- API (FastAPI/uvicorn) loading the latest model from `bitcoin_model/`
- Docker Compose orchestrates all services

## Components
- Producer: [bitcoin_producer.py](bitcoin_producer.py) → topic `bitcoin_prices`
- Streaming trainer: [spark_realtime_ml.py](spark_realtime_ml.py) trains GBT on each micro-batch, writes `model_metrics.txt` (current) and `metrics_history.json` (append-only), saves model to `bitcoin_model/`
- Dashboard: [realtime_dashboard.py](realtime_dashboard.py) shows RMSE/MAE, batch number, feature importances
- API: [api_service.py](api_service.py) served via uvicorn on port 8000 (loads model from `bitcoin_model/`)
- Compose: [docker-compose.yml](docker-compose.yml) wires everything

## Prerequisites
- Docker + Docker Compose
- Free ports: 2181, 7077, 8080, 8501, 8000, 9092

## Quick Start
```bash
# from project root
docker compose build          # needed after code changes
docker compose up -d          # start all services
docker compose ps             # verify containers
docker compose logs -f spark-streaming   # watch training
```

### URLs
- Dashboard: http://localhost:8501
- Kafka UI: http://localhost:8080
- API (if enabled): http://localhost:8000/docs

## Data and Model
- Source: BTC-USD via yfinance, streamed as JSON rows (open, high, low, close, volume)
- Features: open, high, low, volume; Label: close
- Model: `GBTRegressor(maxIter=20, maxDepth=5, stepSize=0.1)`
- Outputs:
	- `model_metrics.txt` (latest RMSE/MAE/feature importances/batch)
	- `metrics_history.json` (all batches)
	- `bitcoin_model/` (latest saved model)

## Useful Commands
- Latest metrics: `tail -n 20 model_metrics.txt`
- Total batches recorded: `jq '.|length' metrics_history.json` (or small Python script if `jq` missing)
- Restart trainer + producer after Kafka is up: `docker compose restart producer spark-streaming`
- Clean slate (removes volumes/containers): `docker compose down -v` then reset `metrics_history.json` to `[]`

## Troubleshooting
- Dashboard shows “Waiting for model metrics”: ensure `spark-streaming` is running and `model_metrics.txt` exists (file, not directory). Check logs: `docker compose logs spark-streaming --tail=50`.
- No batches processing: check producer logs `docker compose logs producer --tail=20`; confirm Kafka env `KAFKA_BOOTSTRAP_SERVERS` matches compose (`kafka:29092`).
- API model load issues: confirm `bitcoin_model/` exists and was produced by the streaming job; restart API with `docker compose restart api`.

## Notes
- Metrics are file-based for simplicity; replace with a datastore for production.
- The API currently loads the model from `bitcoin_model/`; regenerate the model by letting `spark-streaming` run.
