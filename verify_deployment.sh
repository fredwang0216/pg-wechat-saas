#!/bin/bash
# Vercel Deployment Verification Script
# Usage: ./verify_deployment.sh <DEPLOYMENT_URL>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <DEPLOYMENT_URL>"
    echo "Example: $0 https://pg-wechat-saas.vercel.app"
    exit 1
fi

DEPLOYMENT_URL="${1%/}"  # Remove trailing slash if present

echo "=================================="
echo "Vercel Deployment Verification"
echo "=================================="
echo "Testing: $DEPLOYMENT_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

PASS_COUNT=0
FAIL_COUNT=0

test_endpoint() {
    local name=$1
    local path=$2
    local expected_status=${3:-200}

    echo -n "Testing $name... "

    response=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL$path" 2>&1)
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        echo "  Response: $body"
        ((PASS_COUNT++))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected HTTP $expected_status, got $http_code)"
        echo "  Response: $body"
        ((FAIL_COUNT++))
    fi
    echo ""
}

# Test all endpoints
test_endpoint "Health Endpoint" "/api/health" 200
test_endpoint "Generate Endpoint" "/api/generate" 200
test_endpoint "Date Endpoint (Canary)" "/api/date" 200
test_endpoint "Test Health Endpoint" "/api/test_health" 200

# Summary
echo "=================================="
echo "Test Summary"
echo "=================================="
echo "Total: $((PASS_COUNT + FAIL_COUNT))"
echo -e "${GREEN}Passed: $PASS_COUNT${NC}"
echo -e "${RED}Failed: $FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Deployment is working correctly."
    exit 0
else
    echo ""
    echo "❌ Some tests failed. Please check the deployment."
    exit 1
fi
