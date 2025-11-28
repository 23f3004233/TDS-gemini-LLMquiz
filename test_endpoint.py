"""
Testing script for LLM Analysis Quiz Solver endpoint
"""
import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:7860")
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("Test 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_json():
    """Test with invalid JSON"""
    print("\n" + "="*60)
    print("Test 2: Invalid JSON")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/solve",
            data="not json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Invalid JSON rejected (400)")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_secret():
    """Test with invalid secret"""
    print("\n" + "="*60)
    print("Test 3: Invalid Secret")
    print("="*60)
    
    try:
        payload = {
            "email": EMAIL,
            "secret": "wrong_secret",
            "url": DEMO_URL
        }
        
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Invalid secret rejected (403)")
            return True
        else:
            print(f"❌ Expected 403, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_valid_request():
    """Test with valid request"""
    print("\n" + "="*60)
    print("Test 4: Valid Request (Demo Quiz)")
    print("="*60)
    
    if not EMAIL or not SECRET:
        print("❌ EMAIL or SECRET not configured in .env")
        return False
    
    try:
        payload = {
            "email": EMAIL,
            "secret": SECRET,
            "url": DEMO_URL
        }
        
        print(f"Sending request to {BASE_URL}/solve")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Valid request accepted (200)")
            print("\n🤖 Check server logs to see agent solving quiz...")
            return True
        else:
            print(f"❌ Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("LLM Analysis Quiz Solver - Endpoint Tests")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Email: {EMAIL}")
    print(f"Secret configured: {'✓' if SECRET else '✗'}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Invalid JSON", test_invalid_json()))
    results.append(("Invalid Secret", test_invalid_secret()))
    results.append(("Valid Request", test_valid_request()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)