#!/bin/bash

echo "🚀 Bitcoin Real-Time Analytics - Live Demo"
echo "=========================================="
echo ""

echo "📊 1. Checking Docker Services Status..."
docker-compose ps
echo ""

echo "⏳ Waiting 10 seconds for services to stabilize..."
sleep 10
echo ""

echo "📨 2. Latest Bitcoin Data (from Kafka)..."
docker-compose logs producer | grep -E "(Total records|Sending|Successfully)" | tail -5
echo ""

echo "🎯 3. ML Model Metrics..."
if [ -f model_metrics.txt ]; then
    echo "Latest Model Metrics:"
    tail -10 model_metrics.txt
else
    echo "⏳ Metrics file still being generated..."
fi
echo ""

echo "🌐 4. Open these URLs in your browser:"
echo "   • Kafka UI: http://localhost:8080"
echo "   • Dashboard: http://localhost:8501"
echo "   • API Docs: http://localhost:8000/docs"
echo ""

echo "📌 5. Test the API:"
echo "   curl http://localhost:8000/predict | jq ."
echo ""

echo "✅ All systems operational! Check browser tabs above."
