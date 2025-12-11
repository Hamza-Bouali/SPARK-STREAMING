import pandas as pd
import json
import time
from kafka import KafkaProducer

# 1) Read Bitcoin CSV file
df = pd.read_csv("coin_Bitcoin.csv")

# 2) Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

print("📡 Bitcoin Producer started... Sending messages to Kafka.\n")

# 3) Send each CSV row to Kafka
for idx, row in df.iterrows():
    message = {
        "date": str(row["Date"]),
        "open": float(row["Open"]),
        "high": float(row["High"]),
        "low": float(row["Low"]),
        "close": float(row["Close"]),
        "volume": float(row["Volume"]),
        "marketcap": float(row["Marketcap"])
    }

    producer.send("bitcoin_prices", message)
    print(f"➡ Sent: {message}")

    time.sleep(0.3)   # Wait 0.3 sec — simulate streaming

print("\n✔ All data has been sent to Kafka!")
producer.flush()
