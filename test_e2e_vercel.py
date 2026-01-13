#!/usr/bin/env python3
"""
End-to-end test script for Vercel deployment
Tests all API endpoints to verify the deployment is working correctly
"""
import requests
import sys
import time

def test_endpoint(url, endpoint_name, expected_status=200, method="GET", json_data=None):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == expected_status:
            print(f"✅ PASS: {endpoint_name}")
            print(f"Response: {response.text[:200]}")
            return True
        else:
            print(f"❌ FAIL: Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ FAIL: Request timeout after 30 seconds")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ FAIL: Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False

def run_e2e_tests(base_url):
    """Run all end-to-end tests"""
    print("\n" + "="*60)
    print("🚀 Starting End-to-End Tests for Vercel Deployment")
    print(f"Base URL: {base_url}")
    print("="*60)

    results = []

    # Test 1: Health check endpoint
    results.append(test_endpoint(
        f"{base_url}/api/health",
        "Health Check Endpoint",
        expected_status=200
    ))

    time.sleep(1)  # Small delay between requests

    # Test 2: Date endpoint (canary test)
    results.append(test_endpoint(
        f"{base_url}/api/date",
        "Date Endpoint (Canary)",
        expected_status=200
    ))

    time.sleep(1)

    # Test 3: Test health endpoint
    results.append(test_endpoint(
        f"{base_url}/api/test_health",
        "Test Health Endpoint",
        expected_status=200
    ))

    time.sleep(1)

    # Test 4: Generate endpoint (placeholder)
    results.append(test_endpoint(
        f"{base_url}/api/generate",
        "Generate Endpoint",
        expected_status=200
    ))

    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    print("="*60)

    return all(results)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_e2e_vercel.py <VERCEL_URL>")
        print("Example: python test_e2e_vercel.py https://your-app.vercel.app")
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')

    success = run_e2e_tests(base_url)

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
