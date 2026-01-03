"""
Test script for Bitcoin Price Prediction API
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing Health Endpoint...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_model_info():
    """Test model info endpoint"""
    print("\n📊 Testing Model Info Endpoint...")
    response = requests.get(f"{API_BASE_URL}/model/info")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_single_prediction():
    """Test single prediction"""
    print("\n🎯 Testing Single Prediction...")
    
    data = {
        "open": 89000.0,
        "high": 90000.0,
        "low": 88000.0,
        "volume": 45000000000.0
    }
    
    print(f"Input: {json.dumps(data, indent=2)}")
    
    response = requests.post(
        f"{API_BASE_URL}/predict",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Prediction Result:")
        print(f"   Predicted Close Price: ${result['predicted_close']:,.2f}")
        print(f"   Model Available: {result['model_available']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_batch_prediction():
    """Test batch prediction"""
    print("\n📦 Testing Batch Prediction...")
    
    data = {
        "data": [
            {
                "open": 89000.0,
                "high": 90000.0,
                "low": 88000.0,
                "volume": 45000000000.0
            },
            {
                "open": 90000.0,
                "high": 91000.0,
                "low": 89500.0,
                "volume": 50000000000.0
            },
            {
                "open": 88000.0,
                "high": 89000.0,
                "low": 87000.0,
                "volume": 40000000000.0
            }
        ]
    }
    
    response = requests.post(
        f"{API_BASE_URL}/batch_predict",
        json=data
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Batch Prediction Results:")
        for i, pred in enumerate(result['predictions'], 1):
            print(f"   Record {i}: ${pred:,.2f}")
        print(f"   Total: {result['count']} predictions")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_reload_model():
    """Test model reload"""
    print("\n🔄 Testing Model Reload...")
    response = requests.post(f"{API_BASE_URL}/model/reload")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Bitcoin Price Prediction API - Test Suite")
    print("=" * 60)
    
    # Check if API is running
    try:
        requests.get(f"{API_BASE_URL}/health", timeout=2)
    except requests.exceptions.RequestException:
        print("\n❌ API is not running!")
        print("Please start the API first:")
        print("   python api_service.py")
        return
    
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Single Prediction", test_single_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("Model Reload", test_reload_model)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()
