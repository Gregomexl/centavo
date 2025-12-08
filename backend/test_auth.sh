#!/bin/bash
# Quick test script for authentication API using curl

BASE_URL="http://localhost:8000"

echo "🚀 Testing Centavo Authentication API"
echo "======================================"

# Test health endpoint
echo -e "\n1️⃣  Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'

# Test user registration
echo -e "\n2️⃣  Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "display_name": "Test User"
  }')
echo "$REGISTER_RESPONSE" | jq '.'

# Test login
echo -e "\n3️⃣  Testing login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }')
echo "$LOGIN_RESPONSE" | jq '.'

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
  echo -e "\n4️⃣  Testing protected endpoint /auth/me..."
  curl -s "$BASE_URL/api/v1/auth/me" \
    -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'
  
  echo -e "\n✅ All tests complete!"
else
  echo -e "\n❌ Login failed, cannot test protected endpoint"
fi
