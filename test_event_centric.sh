#!/bin/bash

API_URL="https://mk2pdsnszf.execute-api.us-west-2.amazonaws.com/prod"

echo "Testing Event-Centric Registration Endpoints"
echo "============================================="

# Create test event
echo "Creating test event..."
curl -s -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "event-centric-test",
    "title": "Event Centric Test",
    "description": "Testing event-centric endpoints",
    "date": "2025-12-20T10:00:00Z",
    "location": "Test Location",
    "capacity": 5,
    "organizer": "Test Organizer",
    "status": "published",
    "waitlistEnabled": true
  }' > /dev/null

# Create test users
echo "Creating test users..."
curl -s -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"userId": "event-test-user-1", "name": "Event Test User 1"}' > /dev/null

curl -s -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{"userId": "event-test-user-2", "name": "Event Test User 2"}' > /dev/null

echo ""
echo "Test 1: POST /events/{eventId}/registrations"
echo "Expected: 201"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/events/event-centric-test/registrations" \
  -H "Content-Type: application/json" \
  -d '{"userId": "event-test-user-1"}')
echo "$RESPONSE" | head -n -1 | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"

echo ""
echo "Test 2: POST /events/{eventId}/registrations (second user)"
echo "Expected: 201"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/events/event-centric-test/registrations" \
  -H "Content-Type: application/json" \
  -d '{"userId": "event-test-user-2"}')
echo "$RESPONSE" | head -n -1 | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"

echo ""
echo "Test 3: GET /events/{eventId}/registrations"
echo "Expected: 200, 2 registrations"
curl -s "$API_URL/events/event-centric-test/registrations" | python3 -m json.tool
echo ""

echo ""
echo "Test 4: DELETE /events/{eventId}/registrations/{userId}"
echo "Expected: 204"
curl -s -w "Status: %{http_code}\n" -X DELETE "$API_URL/events/event-centric-test/registrations/event-test-user-1"

echo ""
echo "Test 5: GET /events/{eventId}/registrations (after delete)"
echo "Expected: 200, 1 registration"
curl -s "$API_URL/events/event-centric-test/registrations" | python3 -m json.tool

# Cleanup
echo ""
echo "Cleaning up..."
curl -s -X DELETE "$API_URL/events/event-centric-test/registrations/event-test-user-2" > /dev/null
curl -s -X DELETE "$API_URL/events/event-centric-test" > /dev/null

echo "Done!"
