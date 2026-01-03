import pandas as pd
import json
import time
import os
from kafka import KafkaProducer

# 1) Read Bitcoin CSV file
df = pd.read_csv("coin_Bitcoin.csv")

# 2) Create Kafka Producer (Docker or local)
kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
producer = KafkaProducer(
    bootstrap_servers=kafka_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print(f"📡 Bitcoin Producer started... Connecting to Kafka at {kafka_servers}")


# 3) Send each CSV row to Kafka
for idx, row in df.iterrows():
    message = {
        "date": str(row["Date"]),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": float(row["Volume"])
    }

    producer.send("bitcoin_prices", message)
    print(f"➡ Sent: {message}")

    time.sleep(0.05)   # Wait 0.3 sec — simulate streaming

print("\n✔ All data has been sent to Kafka!")
producer.flush()
