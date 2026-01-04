import pandas as pd
import json
import time
import os
from kafka import KafkaProducer
import yfinance as yf



# Get period from environment or use default
period = os.getenv("BITCOIN_PERIOD", "2y")  # Default: 7 days
interval = os.getenv("BITCOIN_INTERVAL", "1h")  # Default: 1 hour

print(f"📥 Downloadxing Bitcoin data: period={period}, interval={interval}")
df = yf.download("BTC-USD", period=period, interval=interval)

# Reset index to make 'Date' a column
df = df.reset_index()


# 2) Create Kafka Producer (Docker or local)
kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# Retry logic for Kafka connection
max_retries = 10
retry_count = 0
producer = None
while retry_count < max_retries:
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=10000
        )
        print(f"✅ Successfully connected to Kafka at {kafka_servers}")
        break
    except Exception as e:
        retry_count += 1
        if retry_count < max_retries:
            print(f"⚠️  Kafka connection attempt {retry_count}/{max_retries} failed: {e}")
            print(f"   Retrying in 3 seconds...")
            time.sleep(3)
        else:
            print(f"❌ Failed to connect to Kafka after {max_retries} attempts")
            raise

print(f" Bitcoin Producer started... Connecting to Kafka at {kafka_servers}")
print(f" Total records to send: {len(df)}")

# 3) Send each DataFrame row to Kafka
for idx, row in df.iterrows():
    # Extract datetime and format it
    dt_value = row["Datetime"]
    if isinstance(dt_value, pd.Series):
        dt_value = dt_value.iloc[0]
    date_str = pd.to_datetime(dt_value).strftime('%Y-%m-%d %H:%M:%S')
    
    message = {
        "date": date_str,
        "open": row["Open"].item() if hasattr(row["Open"], 'item') else float(row["Open"]),
        "high": row["High"].item() if hasattr(row["High"], 'item') else float(row["High"]),
        "low": row["Low"].item() if hasattr(row["Low"], 'item') else float(row["Low"]),
        "close": row["Close"].item() if hasattr(row["Close"], 'item') else float(row["Close"]),
        "volume": row["Volume"].item() if hasattr(row["Volume"], 'item') else float(row["Volume"])
    }

    producer.send("bitcoin_prices", message)
    print(f"➡ Sent: {message}")

    time.sleep(0.005)   # simulate streaming

print("\n✔ All data has been sent to Kafka!")
producer.flush()
