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
events_table_name = os.environ.get("EVENTS_TABLE_NAME", "EventsTable")
users_table_name = os.environ.get("USERS_TABLE_NAME", "UsersTable")
registrations_table_name = os.environ.get("REGISTRATIONS_TABLE_NAME", "RegistrationsTable")

events_table = dynamodb.Table(events_table_name)
users_table = dynamodb.Table(users_table_name)
registrations_table = dynamodb.Table(registrations_table_name)

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
    waitlistEnabled: bool = False

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
    registeredCount: int = 0
    waitlistEnabled: bool = False
    waitlist: list[str] = Field(default_factory=list)
    createdAt: str
    updatedAt: str
    
    @property
    def availableSpots(self) -> int:
        """Computed field: capacity - registeredCount"""
        return self.capacity - self.registeredCount
    
    @property
    def waitlistCount(self) -> int:
        """Computed field: length of waitlist"""
        return len(self.waitlist)

# User models
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100, pattern="^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    
    @classmethod
    def validate_not_whitespace(cls, v: str, field_name: str) -> str:
        """Validate that string is not empty or all whitespace"""
        if not v or not v.strip():
            raise ValueError(f"{field_name} cannot be empty or whitespace only")
        return v
    
    def model_post_init(self, __context) -> None:
        """Additional validation after model initialization"""
        self.validate_not_whitespace(self.userId, "userId")
        self.validate_not_whitespace(self.name, "name")

class User(BaseModel):
    userId: str
    name: str
    createdAt: str
    updatedAt: str

# Registration models
class RegistrationCreate(BaseModel):
    eventId: str = Field(..., min_length=1)

class Registration(BaseModel):
    userId: str
    eventId: str
    status: str = Field(..., pattern="^(confirmed|waitlist)$")
    registeredAt: str
    eventTitle: str  # Denormalized for convenience
    eventDate: str   # Denormalized for convenience

class RegistrationList(BaseModel):
    registrations: list[Registration]
    total: int

# Helper functions
def validate_registration(user_id: str, event_id: str) -> tuple[bool, str, dict]:
    """
    Validate registration prerequisites
    Returns: (is_valid, error_message, event_data)
    """
    # Check user exists
    try:
        user_response = users_table.get_item(Key={"userId": user_id})
        if "Item" not in user_response:
            return False, "User not found", {}
    except Exception as e:
        return False, f"Failed to check user: {str(e)}", {}
    
    # Check event exists
    try:
        event_response = events_table.get_item(Key={"eventId": event_id})
        if "Item" not in event_response:
            return False, "Event not found", {}
        event = event_response["Item"]
    except Exception as e:
        return False, f"Failed to check event: {str(e)}", {}
    
    # Check user not already registered
    try:
        reg_response = registrations_table.get_item(
            Key={"userId": user_id, "eventId": event_id}
        )
        if "Item" in reg_response:
            return False, "User already registered for this event", {}
    except Exception as e:
        return False, f"Failed to check registration: {str(e)}", {}
    
    # Check user not already on waitlist
    if user_id in event.get("waitlist", []):
        return False, "User already on waitlist for this event", {}
    
    return True, "", event

def check_and_reserve_spot(event_id: str, user_id: str, event: dict) -> tuple[str, dict]:
    """
    Check capacity and reserve spot or add to waitlist
    Returns: (status, updated_event) where status is 'confirmed', 'waitlist', or 'rejected'
    """
    registered_count = event.get("registeredCount", 0)
    capacity = event.get("capacity", 0)
    waitlist_enabled = event.get("waitlistEnabled", False)
    
    if registered_count < capacity:
        # Spot available - reserve it
        try:
            response = events_table.update_item(
                Key={"eventId": event_id},
                UpdateExpression="SET registeredCount = registeredCount + :inc, updatedAt = :timestamp",
                ConditionExpression="registeredCount < #capacity",
                ExpressionAttributeNames={
                    "#capacity": "capacity"
                },
                ExpressionAttributeValues={
                    ":inc": 1,
                    ":timestamp": datetime.utcnow().isoformat()
                },
                ReturnValues="ALL_NEW"
            )
            return "confirmed", response["Attributes"]
        except events_table.meta.client.exceptions.ConditionalCheckFailedException:
            # Race condition - capacity filled, try waitlist
            if waitlist_enabled:
                return check_and_reserve_spot(event_id, user_id, event)
            else:
                return "rejected", event
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to reserve spot: {str(e)}")
    elif waitlist_enabled:
        # Event full but waitlist enabled
        try:
            response = events_table.update_item(
                Key={"eventId": event_id},
                UpdateExpression="SET waitlist = list_append(if_not_exists(waitlist, :empty_list), :user), updatedAt = :timestamp",
                ExpressionAttributeValues={
                    ":user": [user_id],
                    ":empty_list": [],
                    ":timestamp": datetime.utcnow().isoformat()
                },
                ReturnValues="ALL_NEW"
            )
            return "waitlist", response["Attributes"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add to waitlist: {str(e)}")
    else:
        # Event full and no waitlist
        return "rejected", event

# API Routes
@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# User endpoints
@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """Create a new user"""
    timestamp = datetime.utcnow().isoformat()
    
    item = {
        "userId": user.userId,
        "name": user.name,
        "createdAt": timestamp,
        "updatedAt": timestamp
    }
    
    try:
        # Use conditional write to prevent duplicate userIds
        users_table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(userId)"
        )
        return item
    except users_table.meta.client.exceptions.ConditionalCheckFailedException:
        raise HTTPException(status_code=409, detail="User with this userId already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    """Get a specific user by ID"""
    try:
        response = users_table.get_item(Key={"userId": user_id})
        
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="User not found")
        
        return response["Item"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

# Registration endpoints
@app.post("/users/{user_id}/registrations", response_model=Registration, status_code=201)
def create_registration(user_id: str, registration: RegistrationCreate):
    """Register a user for an event"""
    event_id = registration.eventId
    
    # Validate prerequisites
    is_valid, error_msg, event = validate_registration(user_id, event_id)
    if not is_valid:
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=409, detail=error_msg)
    
    # Check capacity and reserve spot or add to waitlist
    status, updated_event = check_and_reserve_spot(event_id, user_id, event)
    
    if status == "rejected":
        raise HTTPException(status_code=409, detail="Event is full and waitlist is not enabled")
    
    # Create registration record
    timestamp = datetime.utcnow().isoformat()
    registration_item = {
        "userId": user_id,
        "eventId": event_id,
        "status": status,
        "registeredAt": timestamp,
        "eventTitle": event.get("title", ""),
        "eventDate": event.get("date", "")
    }
    
    try:
        registrations_table.put_item(Item=registration_item)
        return registration_item
    except Exception as e:
        # Rollback capacity change if registration record creation fails
        if status == "confirmed":
            try:
                events_table.update_item(
                    Key={"eventId": event_id},
                    UpdateExpression="SET registeredCount = registeredCount - :dec",
                    ExpressionAttributeValues={":dec": 1}
                )
            except:
                pass  # Log this but don't fail the error response
        raise HTTPException(status_code=500, detail=f"Failed to create registration: {str(e)}")

@app.get("/users/{user_id}/registrations", response_model=RegistrationList)
def get_user_registrations(user_id: str):
    """Get all registrations for a user"""
    # Check user exists
    try:
        user_response = users_table.get_item(Key={"userId": user_id})
        if "Item" not in user_response:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check user: {str(e)}")
    
    # Query registrations
    try:
        response = registrations_table.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )
        registrations = response.get("Items", [])
        return {
            "registrations": registrations,
            "total": len(registrations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get registrations: {str(e)}")

@app.delete("/users/{user_id}/registrations/{event_id}", status_code=204)
def delete_registration(user_id: str, event_id: str):
    """Unregister a user from an event"""
    # Check registration exists
    try:
        reg_response = registrations_table.get_item(
            Key={"userId": user_id, "eventId": event_id}
        )
        if "Item" not in reg_response:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        registration = reg_response["Item"]
        reg_status = registration.get("status", "confirmed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check registration: {str(e)}")
    
    # Get event details
    try:
        event_response = events_table.get_item(Key={"eventId": event_id})
        if "Item" not in event_response:
            raise HTTPException(status_code=404, detail="Event not found")
        event = event_response["Item"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event: {str(e)}")
    
    # Delete registration
    try:
        registrations_table.delete_item(
            Key={"userId": user_id, "eventId": event_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete registration: {str(e)}")
    
    # Handle based on registration status
    if reg_status == "confirmed":
        # Decrement registered count
        try:
            events_table.update_item(
                Key={"eventId": event_id},
                UpdateExpression="SET registeredCount = registeredCount - :dec, updatedAt = :timestamp",
                ExpressionAttributeValues={
                    ":dec": 1,
                    ":timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update event capacity: {str(e)}")
        
        # Check for waitlist promotion
        waitlist = event.get("waitlist", [])
        if waitlist:
            promoted_user_id = waitlist[0]
            
            # Use transaction for atomic promotion
            try:
                dynamodb_client = boto3.client("dynamodb")
                dynamodb_client.transact_write_items(
                    TransactItems=[
                        {
                            "Update": {
                                "TableName": events_table_name,
                                "Key": {"eventId": {"S": event_id}},
                                "UpdateExpression": "REMOVE waitlist[0] SET updatedAt = :timestamp",
                                "ExpressionAttributeValues": {
                                    ":timestamp": {"S": datetime.utcnow().isoformat()}
                                }
                            }
                        },
                        {
                            "Update": {
                                "TableName": registrations_table_name,
                                "Key": {
                                    "userId": {"S": promoted_user_id},
                                    "eventId": {"S": event_id}
                                },
                                "UpdateExpression": "SET #status = :confirmed",
                                "ExpressionAttributeNames": {"#status": "status"},
                                "ExpressionAttributeValues": {
                                    ":confirmed": {"S": "confirmed"}
                                }
                            }
                        }
                    ]
                )
            except Exception as e:
                # Log error but don't fail the unregistration
                print(f"Failed to promote from waitlist: {str(e)}")
    
    elif reg_status == "waitlist":
        # Remove from waitlist array
        try:
            waitlist = event.get("waitlist", [])
            if user_id in waitlist:
                waitlist.remove(user_id)
                events_table.update_item(
                    Key={"eventId": event_id},
                    UpdateExpression="SET waitlist = :waitlist, updatedAt = :timestamp",
                    ExpressionAttributeValues={
                        ":waitlist": waitlist,
                        ":timestamp": datetime.utcnow().isoformat()
                    }
                )
        except Exception as e:
            # Log error but don't fail the unregistration
            print(f"Failed to remove from waitlist: {str(e)}")
    
    return None

# Event-centric registration endpoints
@app.post("/events/{event_id}/registrations", response_model=Registration, status_code=201)
def create_registration_for_event(event_id: str, registration: dict):
    """Register a user for an event (event-centric endpoint)"""
    user_id = registration.get("userId")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="userId is required")
    
    # Validate prerequisites
    is_valid, error_msg, event = validate_registration(user_id, event_id)
    if not is_valid:
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=409, detail=error_msg)
    
    # Check capacity and reserve spot or add to waitlist
    status, updated_event = check_and_reserve_spot(event_id, user_id, event)
    
    if status == "rejected":
        raise HTTPException(status_code=409, detail="Event is full and waitlist is not enabled")
    
    # Create registration record
    timestamp = datetime.utcnow().isoformat()
    registration_item = {
        "userId": user_id,
        "eventId": event_id,
        "status": status,
        "registeredAt": timestamp,
        "eventTitle": event.get("title", ""),
        "eventDate": event.get("date", "")
    }
    
    try:
        registrations_table.put_item(Item=registration_item)
        return registration_item
    except Exception as e:
        # Rollback capacity change if registration record creation fails
        if status == "confirmed":
            try:
                events_table.update_item(
                    Key={"eventId": event_id},
                    UpdateExpression="SET registeredCount = registeredCount - :dec",
                    ExpressionAttributeValues={":dec": 1}
                )
            except:
                pass  # Log this but don't fail the error response
        raise HTTPException(status_code=500, detail=f"Failed to create registration: {str(e)}")

@app.get("/events/{event_id}/registrations", response_model=RegistrationList)
def get_event_registrations(event_id: str):
    """Get all registrations for an event (event-centric endpoint)"""
    # Check event exists
    try:
        event_response = events_table.get_item(Key={"eventId": event_id})
        if "Item" not in event_response:
            raise HTTPException(status_code=404, detail="Event not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check event: {str(e)}")
    
    # Query registrations using GSI
    try:
        response = registrations_table.query(
            IndexName="eventId-userId-index",
            KeyConditionExpression=Key("eventId").eq(event_id)
        )
        registrations = response.get("Items", [])
        return {
            "registrations": registrations,
            "total": len(registrations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get registrations: {str(e)}")

@app.delete("/events/{event_id}/registrations/{user_id}", status_code=204)
def delete_registration_for_event(event_id: str, user_id: str):
    """Unregister a user from an event (event-centric endpoint)"""
    # This is the same logic as the user-centric endpoint
    # Just call the existing function with swapped parameter order
    return delete_registration(user_id, event_id)

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
        "registeredCount": 0,
        "waitlistEnabled": event.waitlistEnabled,
        "waitlist": [],
        "createdAt": timestamp,
        "updatedAt": timestamp
    }
    
    try:
        events_table.put_item(Item=item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/events", response_model=list[Event])
def list_events(status: Optional[str] = None):
    """List all events, optionally filtered by status"""
    try:
        if status:
            response = events_table.scan(
                FilterExpression=Key("status").eq(status)
            )
        else:
            response = events_table.scan()
        
        return response.get("Items", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID"""
    try:
        response = events_table.get_item(Key={"eventId": event_id})
        
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
        response = events_table.get_item(Key={"eventId": event_id})
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
        response = events_table.update_item(
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
        response = events_table.get_item(Key={"eventId": event_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        events_table.delete_item(Key={"eventId": event_id})
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")

# Lambda handler
handler = Mangum(app)
