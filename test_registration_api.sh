#!/bin/bash

API_URL="https://mk2pdsnszf.execute-api.us-west-2.amazonaws.com/prod"

echo "========================================="
echo "User Registration API Tests"
echo "========================================="
echo ""

# Test 1: Create User
echo "========================================="
echo "Test 1: POST /users (Create User)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-001",
    "name": "Test User One"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 2: Get User
echo "========================================="
echo "Test 2: GET /users/test-user-001"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/users/test-user-001"

# Test 3: Create Duplicate User (should fail)
echo "========================================="
echo "Test 3: POST /users (Duplicate userId)"
echo "Expected Status: 409"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-001",
    "name": "Duplicate User"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 4: Create User with Whitespace Name (should fail)
echo "========================================="
echo "Test 4: POST /users (Whitespace Name)"
echo "Expected Status: 400 or 422"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-002",
    "name": "   "
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 5: Create Second User
echo "========================================="
echo "Test 5: POST /users (Create Second User)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-002",
    "name": "Test User Two"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 6: Create Event with Waitlist
echo "========================================="
echo "Test 6: POST /events (Event with Waitlist)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001",
    "title": "Test Event with Waitlist",
    "description": "Testing registration with waitlist",
    "date": "2025-12-15T10:00:00Z",
    "location": "Test Location",
    "capacity": 2,
    "organizer": "Test Organizer",
    "status": "published",
    "waitlistEnabled": true
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 7: Create Event without Waitlist
echo "========================================="
echo "Test 7: POST /events (Event without Waitlist)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-002",
    "title": "Test Event without Waitlist",
    "description": "Testing registration without waitlist",
    "date": "2025-12-20T14:00:00Z",
    "location": "Test Location 2",
    "capacity": 1,
    "organizer": "Test Organizer",
    "status": "published",
    "waitlistEnabled": false
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 8: Register User for Event
echo "========================================="
echo "Test 8: POST /users/test-user-001/registrations"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-001/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 9: Get User Registrations
echo "========================================="
echo "Test 9: GET /users/test-user-001/registrations"
echo "Expected Status: 200"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/users/test-user-001/registrations"

# Test 10: Register Same User Again (should fail)
echo "========================================="
echo "Test 10: POST /users/test-user-001/registrations (Duplicate)"
echo "Expected Status: 409"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-001/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 11: Register Second User (Fill Capacity)
echo "========================================="
echo "Test 11: POST /users/test-user-002/registrations (Fill Capacity)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-002/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 12: Create Third User for Waitlist
echo "========================================="
echo "Test 12: POST /users (Create Third User)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "test-user-003",
    "name": "Test User Three"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 13: Register Third User (Should go to Waitlist)
echo "========================================="
echo "Test 13: POST /users/test-user-003/registrations (Waitlist)"
echo "Expected Status: 201, status: waitlist"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-003/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 14: Check Event Status
echo "========================================="
echo "Test 14: GET /events/test-event-001 (Check Capacity)"
echo "Expected: registeredCount=2, waitlist=[test-user-003]"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/events/test-event-001"

# Test 15: Unregister First User (Should Promote from Waitlist)
echo "========================================="
echo "Test 15: DELETE /users/test-user-001/registrations/test-event-001"
echo "Expected Status: 204"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" -X DELETE "$API_URL/users/test-user-001/registrations/test-event-001"

# Test 16: Check Event After Promotion
echo "========================================="
echo "Test 16: GET /events/test-event-001 (After Promotion)"
echo "Expected: registeredCount=2, waitlist=[]"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/events/test-event-001"

# Test 17: Check Third User Registration Status
echo "========================================="
echo "Test 17: GET /users/test-user-003/registrations"
echo "Expected: status=confirmed"
echo "========================================="
curl -s -w "\nStatus: %{http_code}\n\n" "$API_URL/users/test-user-003/registrations"

# Test 18: Register for Event without Waitlist
echo "========================================="
echo "Test 18: POST /users/test-user-001/registrations (No Waitlist Event)"
echo "Expected Status: 201"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-001/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-002"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 19: Try to Register When Full (No Waitlist - Should Fail)
echo "========================================="
echo "Test 19: POST /users/test-user-002/registrations (Full, No Waitlist)"
echo "Expected Status: 409"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-002/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-002"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 20: Register for Non-existent Event (Should Fail)
echo "========================================="
echo "Test 20: POST /users/test-user-001/registrations (Non-existent Event)"
echo "Expected Status: 404"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/test-user-001/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "non-existent-event"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Test 21: Non-existent User Registration (Should Fail)
echo "========================================="
echo "Test 21: POST /users/non-existent-user/registrations"
echo "Expected Status: 404"
echo "========================================="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/users/non-existent-user/registrations" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-event-001"
  }')
echo "$RESPONSE" | head -n -1
echo "Status: $(echo "$RESPONSE" | tail -n 1)"
echo ""

# Cleanup
echo "========================================="
echo "Cleanup: Deleting Test Data"
echo "========================================="

# Delete registrations
curl -s -X DELETE "$API_URL/users/test-user-001/registrations/test-event-002" > /dev/null
curl -s -X DELETE "$API_URL/users/test-user-002/registrations/test-event-001" > /dev/null
curl -s -X DELETE "$API_URL/users/test-user-003/registrations/test-event-001" > /dev/null

# Delete events
curl -s -X DELETE "$API_URL/events/test-event-001" > /dev/null
curl -s -X DELETE "$API_URL/events/test-event-002" > /dev/null

echo "Cleanup completed"
echo ""

echo "========================================="
echo "All tests completed!"
echo "========================================="
