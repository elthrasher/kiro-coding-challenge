"""
Example requests for testing the Events API
Run this after deploying to test all CRUD operations
"""

import requests
import json
from datetime import datetime, timedelta

# Replace with your API Gateway URL after deployment
API_URL = "https://your-api-id.execute-api.region.amazonaws.com/prod"

def test_api():
    print("Testing Events API\n")
    
    # 1. Health Check
    print("1. Health Check")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    
    # 2. Create Event
    print("2. Create Event")
    event_data = {
        "title": "Tech Conference 2025",
        "description": "Annual technology conference featuring the latest innovations",
        "date": (datetime.now() + timedelta(days=90)).isoformat(),
        "location": "San Francisco, CA",
        "capacity": 500,
        "organizer": "Tech Corp",
        "status": "published"
    }
    response = requests.post(f"{API_URL}/events", json=event_data)
    print(f"Status: {response.status_code}")
    created_event = response.json()
    print(f"Response: {json.dumps(created_event, indent=2)}\n")
    event_id = created_event["eventId"]
    
    # 3. Get Event
    print("3. Get Event by ID")
    response = requests.get(f"{API_URL}/events/{event_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 4. List Events
    print("4. List All Events")
    response = requests.get(f"{API_URL}/events")
    print(f"Status: {response.status_code}")
    print(f"Found {len(response.json())} events\n")
    
    # 5. Update Event
    print("5. Update Event")
    update_data = {
        "capacity": 600,
        "status": "published"
    }
    response = requests.put(f"{API_URL}/events/{event_id}", json=update_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    
    # 6. Filter by Status
    print("6. Filter Events by Status")
    response = requests.get(f"{API_URL}/events?status=published")
    print(f"Status: {response.status_code}")
    print(f"Found {len(response.json())} published events\n")
    
    # 7. Delete Event
    print("7. Delete Event")
    response = requests.delete(f"{API_URL}/events/{event_id}")
    print(f"Status: {response.status_code}")
    print("Event deleted successfully\n")
    
    # 8. Verify Deletion
    print("8. Verify Event Deleted")
    response = requests.get(f"{API_URL}/events/{event_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

if __name__ == "__main__":
    test_api()
