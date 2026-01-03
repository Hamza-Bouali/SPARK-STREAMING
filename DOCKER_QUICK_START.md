# Bitcoin Real-time Analytics - Docker Quick Start

## 🚀 One-Command Startup

All services start automatically with Docker Compose:

\`\`\`bash
./start_pipeline.sh
\`\`\`

## 📦 What Gets Started

The following services start automatically in order:

1. **Zookeeper** (port 2181) - Kafka coordination
2. **Kafka** (port 9092) - Message broker
3. **Kafka UI** (port 8080) - Web interface for Kafka monitoring
4. **Bitcoin Producer** - Sends historical data to Kafka (runs once, then exits)
5. **Spark Streaming** - Real-time ML pipeline (runs continuously)
6. **API Service** (port 8000) - REST API for predictions (runs continuously)

## ✅ Verification

Check all services are running:
\`\`\`bash
docker compose ps
\`\`\`

Test the API:
\`\`\`bash
# Health check
curl http://localhost:8000/health

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"open": 50000, "high": 51000, "low": 49000, "volume": 1000000}'
\`\`\`

Access web interfaces:
- **Kafka UI**: http://localhost:8080
- **API Docs**: http://localhost:8000/docs
- **API Swagger**: http://localhost:8000/redoc

## 📋 Useful Commands

\`\`\`bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f spark-streaming
docker compose logs -f api-service
docker compose logs -f producer

# Stop all services
docker compose down

# Restart specific service
docker compose restart spark-streaming

# Rebuild and restart everything
docker compose down
docker compose build
docker compose up -d
\`\`\`

## 🔄 Service Restart Behavior

- **Producer**: Runs once to send data, then exits (restart="no")
- **Spark Streaming**: Runs continuously, auto-restarts on failure
- **API Service**: Runs continuously, auto-restarts on failure
- **Kafka/Zookeeper**: Run continuously, foundational services

## 🛠️ Troubleshooting

If services fail to start:

1. Check logs: `docker compose logs <service-name>`
2. Verify ports are free: `lsof -i :8000` , `lsof -i :9092`
3. Rebuild images: `docker compose build --no-cache`
4. Clean up volumes: `docker compose down -v`

## 🌐 Port Usage

| Port | Service | Description |
|------|---------|-------------|
| 2181 | Zookeeper | Coordination service |
| 8000 | API Service | REST API |
| 8080 | Kafka UI | Web interface |
| 9092 | Kafka | External broker connection |
| 9093 | Kafka | Additional listener |

## Environment Variables

Services use these environment variables (configured in docker-compose.yml):

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection string (kafka:29092 inside Docker)
- `JAVA_HOME`: Java installation path (/usr/lib/jvm/temurin-17-jre-amd64)

No manual configuration needed - everything is pre-configured!
