FROM python:3.12-slim

# Install dependencies and Java
RUN apt-get update && \
    apt-get install -y wget apt-transport-https gnupg && \
    mkdir -p /etc/apt/keyrings && \
    wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | tee /etc/apt/keyrings/adoptium.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/adoptium.asc] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && \
    apt-get install -y temurin-17-jre && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Java environment
ENV JAVA_HOME=/usr/lib/jvm/temurin-17-jre-amd64
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
COPY realtime_dashboard.py .

# Create directories for model and checkpoints
RUN mkdir -p /app/checkpoint /app/bitcoin_model

# Default command (can be overridden)
CMD ["python", "api_service.py"]
