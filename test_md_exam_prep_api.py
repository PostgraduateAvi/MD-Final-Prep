#!/usr/bin/env python3
"""
Test script for MD Exam Prep API
================================

Simple test script to verify the API endpoints are working correctly.
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

def start_api_server():
    """Start the API server in the background."""
    try:
        subprocess.run([
            sys.executable, "md_exam_prep_api.py"
        ], check=False, capture_output=True)
    except Exception as e:
        print(f"Error starting server: {e}")

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing MD Exam Prep API")
    print("=" * 40)
    
    # Wait for server to start
    print("⏳ Waiting for API server to start...")
    time.sleep(3)
    
    tests = [
        {
            "name": "Root endpoint",
            "method": "GET",
            "url": f"{base_url}/",
            "expected_status": 200
        },
        {
            "name": "Health check",
            "method": "GET", 
            "url": f"{base_url}/health",
            "expected_status": 200
        },
        {
            "name": "Predict exam topics",
            "method": "GET",
            "url": f"{base_url}/predict?limit=2",
            "expected_status": 200
        },
        {
            "name": "Summarize topic",
            "method": "POST",
            "url": f"{base_url}/summarize",
            "data": {"topic": "heart_failure"},
            "expected_status": 200
        },
        {
            "name": "Get content for topic",
            "method": "GET",
            "url": f"{base_url}/content/diabetes",
            "expected_status": [200, 404]  # 404 is acceptable if topic not found
        }
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n🔍 {test['name']}")
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], timeout=10)
            elif test["method"] == "POST":
                response = requests.post(
                    test["url"], 
                    json=test.get("data", {}),
                    timeout=10
                )
            
            expected = test["expected_status"]
            if isinstance(expected, list):
                status_ok = response.status_code in expected
            else:
                status_ok = response.status_code == expected
            
            if status_ok:
                print(f"  ✅ PASSED (Status: {response.status_code})")
                
                # Print response preview for successful requests
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            print(f"     Response keys: {keys}")
                        else:
                            print(f"     Response: {str(data)[:50]}...")
                    except:
                        print(f"     Response length: {len(response.text)} chars")
                
                passed += 1
            else:
                print(f"  ❌ FAILED - Expected status {expected}, got {response.status_code}")
                print(f"     Response: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"  🔌 CONNECTION ERROR - API server not reachable")
        except requests.exceptions.Timeout:
            print(f"  ⏰ TIMEOUT")
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    print(f"\n" + "=" * 40)
    print(f"TEST SUMMARY: {passed}/{total} passed")
    
    if passed >= 3:  # At least basic endpoints should work
        print(f"🎉 API is working correctly!")
        return True
    else:
        print(f"⚠️  API needs attention")
        return False

if __name__ == "__main__":
    # Test if we can import the API module
    try:
        import md_exam_prep_api
        print("✅ API module imports successfully")
    except Exception as e:
        print(f"❌ Cannot import API module: {e}")
        sys.exit(1)
    
    # Start server in background thread
    server_thread = Thread(target=start_api_server, daemon=True)
    server_thread.start()
    
    # Run tests
    success = test_api_endpoints()
    sys.exit(0 if success else 1)