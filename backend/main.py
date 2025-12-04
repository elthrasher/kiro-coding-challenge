import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from mangum import Mangum
import boto3
from boto3.dynamodb.conditions import Key

# Initialize FastAPI app
app = FastAPI(title="Events API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("EVENTS_TABLE_NAME", "EventsTable")
table = dynamodb.Table(table_name)

# Pydantic models
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    date: str = Field(..., description="Event date in ISO format")
    location: str = Field(..., min_length=1, max_length=200)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1, max_length=100)
    status: str = Field(..., pattern="^(draft|published|cancelled|completed|active)$")

class EventCreate(EventBase):
    eventId: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|published|cancelled|completed|active)$")

class Event(EventBase):
    eventId: str
    createdAt: str
    updatedAt: str

# API Routes
@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """Create a new event"""
    event_id = event.eventId if event.eventId else str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    item = {
        "eventId": event_id,
        "title": event.title,
        "description": event.description,
        "date": event.date,
        "location": event.location,
        "capacity": event.capacity,
        "organizer": event.organizer,
        "status": event.status,
        "createdAt": timestamp,
        "updatedAt": timestamp
    }
    
    try:
        table.put_item(Item=item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/events", response_model=list[Event])
def list_events(status: Optional[str] = None):
    """List all events, optionally filtered by status"""
    try:
        if status:
            response = table.scan(
                FilterExpression=Key("status").eq(status)
            )
        else:
            response = table.scan()
        
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID"""
    try:
        response = table.get_item(Key={"eventId": event_id})
        
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return response["Item"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event"""
    # First check if event exists
    try:
        response = table.get_item(Key={"eventId": event_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check event: {str(e)}")
    
    # Build update expression
    update_data = event_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updatedAt"] = datetime.utcnow().isoformat()
    
    update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
    expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
    expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
    
    try:
        response = table.update_item(
            Key={"eventId": event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return response["Attributes"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str):
    """Delete an event"""
    try:
        # Check if event exists
        response = table.get_item(Key={"eventId": event_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        table.delete_item(Key={"eventId": event_id})
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

# Lambda handler
handler = Mangum(app)
