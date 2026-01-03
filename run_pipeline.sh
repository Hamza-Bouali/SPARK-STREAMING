#!/bin/bash

# Bitcoin Real-time ML Pipeline Runner
# This script orchestrates the complete pipeline

echo "🚀 Bitcoin Real-time ML Pipeline"
echo "================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Function to check if a process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check Docker containers
echo -e "${YELLOW}📦 Checking Docker containers...${NC}"
if ! docker compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Docker containers are not running${NC}"
    echo "Starting containers..."
    docker compose up -d
    sleep 10
fi

echo -e "${GREEN}✅ Docker containers are running${NC}"
echo ""

# Menu
echo "Select an option:"
echo "1. Start Producer (send Bitcoin data to Kafka)"
echo "2. Start Streaming ML Pipeline (process & train model)"
echo "3. Start FastAPI Prediction Service"
echo "4. Run Complete Pipeline (all services)"
echo "5. Test API with sample prediction"
echo "6. Stop all services"
echo ""
read -p "Enter your choice [1-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}🔄 Starting Kafka Producer...${NC}"
        python bitcoin_producer.py
        ;;
    2)
        echo -e "${GREEN}🤖 Starting Streaming ML Pipeline...${NC}"
        python spark_realtime_ml.py
        ;;
    3)
        echo -e "${GREEN}🌐 Starting FastAPI Service...${NC}"
        echo "API will be available at http://localhost:8000"
        echo "API docs at http://localhost:8000/docs"
        python api_service.py
        ;;
    4)
        echo -e "${GREEN}🚀 Starting Complete Pipeline...${NC}"
        echo ""
        echo "Starting services in separate terminals..."
        echo "1. Producer will run in background"
        echo "2. Streaming ML Pipeline will process data"
        echo "3. FastAPI will be available at http://localhost:8000"
        echo ""
        
        # Start producer in background
        python bitcoin_producer.py &
        PRODUCER_PID=$!
        echo "✅ Producer started (PID: $PRODUCER_PID)"
        
        sleep 5
        
        # Start streaming ML in background
        python spark_realtime_ml.py &
        SPARK_PID=$!
        echo "✅ Streaming ML started (PID: $SPARK_PID)"
        
        sleep 10
        
        # Start API (foreground)
        echo "✅ Starting API service..."
        python api_service.py
        ;;
    5)
        echo -e "${GREEN}🧪 Testing API...${NC}"
        echo ""
        
        # Check if API is running
        if ! curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${RED}❌ API is not running${NC}"
            echo "Please start the API first (option 3)"
            exit 1
        fi
        
        echo "Testing /health endpoint:"
        curl -s http://localhost:8000/health | python -m json.tool
        echo ""
        
        echo "Testing /model/info endpoint:"
        curl -s http://localhost:8000/model/info | python -m json.tool
        echo ""
        
        echo "Testing /predict endpoint with sample data:"
        curl -X POST "http://localhost:8000/predict" \
          -H "Content-Type: application/json" \
          -d '{
            "open": 50000.0,
            "high": 51000.0,
            "low": 49500.0,
            "volume": 1000000000.0
          }' | python -m json.tool
        echo ""
        
        echo -e "${GREEN}✅ API tests completed${NC}"
        ;;
    6)
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        
        # Kill Python processes
        pkill -f bitcoin_producer.py
        pkill -f spark_realtime_ml.py
        pkill -f api_service.py
        
        echo -e "${GREEN}✅ All services stopped${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac
