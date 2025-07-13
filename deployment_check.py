#!/usr/bin/env python3
"""
Deployment verification script for Recipe API
"""

import sys
import os
import json
import traceback

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = ["LLM7_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_services():
    """Check if services can be initialized"""
    print("🔧 Checking service initialization...")
    
    try:
        from src.services.llm7_service import LLM7Service
        llm7_service = LLM7Service()
        print("✅ LLM7 service initialized successfully")
        
        from src.services.recipe_service import RecipeService
        recipe_service = RecipeService()
        print("✅ Recipe service initialized successfully")
        
        return True
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        traceback.print_exc()
        return False

def check_api_endpoints():
    """Check if API endpoints respond correctly"""
    print("🌐 Checking API endpoints...")
    
    try:
        from api.index import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code != 200:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        print("✅ Root endpoint working")
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code != 200:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        print("✅ Health endpoint working")
        
        # Test styles endpoint
        response = client.get("/api/recipes/styles")
        if response.status_code != 200:
            print(f"❌ Styles endpoint failed: {response.status_code}")
            return False
        print("✅ Styles endpoint working")
        
        return True
    except Exception as e:
        print(f"❌ API endpoint check failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Main deployment check"""
    print("🚀 Recipe API Deployment Check")
    print("=" * 40)
    
    checks = [
        check_environment,
        check_services,
        check_api_endpoints
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All deployment checks passed! API is ready for production.")
        sys.exit(0)
    else:
        print("❌ Some deployment checks failed. Please fix the issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
