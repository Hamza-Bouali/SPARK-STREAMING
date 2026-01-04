# Bitcoin Real-time ML Pipeline (Kafka + Spark + Streamlit)

End-to-end demo that streams live BTC-USD prices from Yahoo Finance into Kafka, trains a Gradient Boosting Tree regressor on each micro-batch with Spark Structured Streaming, and visualizes metrics in a Streamlit dashboard.

## Stack
- Kafka + Zookeeper (Confluent images)
- Spark 4.1.0 (Structured Streaming + MLlib GBTRegressor)
- Python 3.12, kafka-python, yfinance, pandas
- Streamlit dashboard for RMSE/MAE + feature importances
- Docker Compose for orchestration

## Components
- Producer: downloads BTC-USD via yfinance and pushes JSON rows to Kafka topic `bitcoin_prices` ([bitcoin_producer.py](bitcoin_producer.py))
- Streaming trainer: consumes Kafka, cleans data, trains GBTRegressor each batch, writes metrics/history and latest model ([spark_realtime_ml.py](spark_realtime_ml.py))
- Dashboard: reads metrics files and shows live KPIs/feature importances ([realtime_dashboard.py](realtime_dashboard.py))
- Compose stack: services + volumes ([docker-compose.yml](docker-compose.yml))

## Prerequisites
- Docker + Docker Compose
- Ports free: 2181, 7077, 8080, 8501, 9092

## Quick Start (Docker)
```bash
# from project root
# 1) Build images (needed after code changes)
docker compose build

# 2) Start all services
docker compose up -d

# 3) Check services
docker compose ps

# 4) Watch streaming logs
docker compose logs -f spark-streaming

# 5) Open dashboard
http://localhost:8501
```

## Environment knobs
- `KAFKA_BOOTSTRAP_SERVERS` (default `kafka:29092` inside compose, `localhost:9092` outside)
- `BITCOIN_PERIOD` (default `2y`) and `BITCOIN_INTERVAL` (default `1h`) for the producer download window
- Volumes mounted to host: `checkpoint/`, `bitcoin_model/`, `model_metrics.txt`, `metrics_history.json`

## What to expect
- Producer sends every row with a short delay to simulate streaming; exits when done.
- Spark trains a GBT model per batch; saves current metrics to `model_metrics.txt` and appends history to `metrics_history.json`.
- Dashboard auto-refreshes and shows RMSE, MAE, trees (20 iterations), feature importances, and batch number.

## Useful commands
- Latest metrics (host): `tail -n 20 model_metrics.txt`
- Total batches recorded: `jq '.|length' metrics_history.json` (or use Python if jq not installed)
- Restart streaming + producer after Kafka is up: `docker compose restart producer spark-streaming`
- Stop everything and remove containers: `docker compose down`

## Troubleshooting
- Dashboard says "Waiting for model metrics": ensure `spark-streaming` is running and `model_metrics.txt` exists (not a directory). `docker compose logs spark-streaming --tail=50`.
- No batches processed: check producer logs (`docker compose logs producer --tail=20`) and Kafka connectivity env.
- Stale volumes: if you need a clean slate, remove `checkpoint/`, `bitcoin_model/`, and reset `metrics_history.json` to `[]` (avoid turning it into a directory when volume-mounted).

## Notes
- Model: `GBTRegressor(maxIter=20, maxDepth=5, stepSize=0.1)` using features `open, high, low, volume`; label `close`.
- Metrics files are simple JSON/text on disk to keep the demo minimal; replace with a datastore for production.
