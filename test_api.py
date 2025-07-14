#!/usr/bin/env python3
"""
Test script to verify the Recipe API works correctly
"""

import sys
import os
import json

# Add the project root to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from api.index import app
from fastapi.testclient import TestClient

def test_api():
    """Test the Recipe API endpoints"""
    client = TestClient(app)
    
    print("🧪 Testing Recipe API...")
    
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Root endpoint: {data['message']}")
    
    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Health endpoint: {data['status']}")
    
    # Test styles endpoint
    response = client.get("/api/recipes/styles")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Styles endpoint: {len(data['styles'])} styles available")
    
    # Test diets endpoint
    response = client.get("/api/recipes/diets")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Diets endpoint: {len(data['diets'])} diets available")
    
    # Test recipe health endpoint
    response = client.get("/api/recipes/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Recipe health endpoint: {data['status']}")
    
    print("\n🎉 All tests passed! API is ready for deployment.")
    return True

if __name__ == "__main__":
    test_api()
