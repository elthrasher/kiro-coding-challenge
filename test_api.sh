#!/bin/bash

API_URL="https://mk2pdsnszf.execute-api.us-west-2.amazonaws.com/prod"

echo "========================================="
echo "Test 1: GET /events"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/events"

echo "========================================="
echo "Test 2: GET /events?status=active"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/events?status=active"

echo "========================================="
echo "Test 3: POST /events"
echo "Expected Status: 201"
echo "Expected JSON keys: eventId"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-15",
    "eventId": "api-test-event-456",
    "organizer": "API Test Organizer",
    "description": "Testing API Gateway integration",
    "location": "API Test Location",
    "title": "API Gateway Test Event",
    "capacity": 200,
    "status": "active"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

echo "========================================="
echo "Test 4: GET /events/api-test-event-456"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/events/api-test-event-456"

echo "========================================="
echo "Test 5: PUT /events/api-test-event-456"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" -X PUT "$API_URL/events/api-test-event-456" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated API Gateway Test Event",
    "capacity": 250
  }'

echo "========================================="
echo "Test 6: DELETE /events/api-test-event-456"
echo "Expected Status: 200 or 204"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" -X DELETE "$API_URL/events/api-test-event-456"

echo "========================================="
echo "All tests completed!"
echo "========================================="
