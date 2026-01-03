#!/bin/bash
set -e

echo "🚀 Starting Bitcoin Real-time Analytics Pipeline..."
echo ""

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker compose down

# Build the Docker images
echo "🔨 Building Docker images..."
docker compose build

# Start all services
echo "▶️  Starting all services..."
docker compose up -d

# Wait for services to initialize
echo "⏳ Waiting for services to initialize (30 seconds)..."
sleep 30

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   - Kafka UI:       http://localhost:8080"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - API Health:     http://localhost:8000/health"
echo "   - Spark Master:   http://localhost:8090"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:      docker compose logs -f"
echo "   - View producer:  docker compose logs -f producer"
echo "   - View spark:     docker compose logs -f spark-streaming"
echo "   - View API:       docker compose logs -f api-service"
echo "   - Stop all:       docker compose down"
echo ""
