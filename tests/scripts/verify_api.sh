#!/bin/bash

# Configuration
BASE_URL="http://localhost:5000"

echo "🔍 Starting API Verification..."

# 1. Health Check
echo -n "Checking Health Result: "
HEALTH=$(curl -s $BASE_URL/api/health | grep -o "healthy")
if [ "$HEALTH" == "healthy" ]; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# 2. Rooms Check (Checking if reachable)
echo -n "Checking Classrooms API: "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/api/classrooms)
if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "401" ]; then
    echo "✅ OK (Status: $HTTP_CODE)"
else
    echo "❌ FAILED (Status: $HTTP_CODE)"
fi

echo "🏁 Verification Complete."
