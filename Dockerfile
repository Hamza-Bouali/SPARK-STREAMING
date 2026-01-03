FROM python:3.12-slim

# Install Java (required for PySpark)
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY bitcoin_producer.py .
COPY spark_realtime_ml.py .
COPY api_service.py .
COPY coin_Bitcoin.csv .

# Create directories for model and checkpoints
RUN mkdir -p /app/checkpoint /app/bitcoin_model

# Default command (can be overridden)
CMD ["python", "api_service.py"]
