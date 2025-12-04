# Design Document: User Registration and Event Management

## Overview

This design extends the existing Events API to support user registration and event capacity management. The system will enable users to register for events with capacity constraints, waitlist functionality, and registration tracking. The design follows the existing FastAPI/DynamoDB architecture and maintains consistency with established API standards.

The core functionality includes:
- User account creation and management
- Event capacity enforcement with waitlist support
- Registration and unregistration workflows
- Automatic waitlist promotion when spots become available
- User registration history tracking

## Architecture

### High-Level Architecture

The user registration system extends the existing serverless architecture:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│             │◀─────│              │◀─────│  (FastAPI)  │◀─────│              │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
                                                                   │
                                                                   ├─ EventsTable
                                                                   ├─ UsersTable
                                                                   └─ RegistrationsTable
```

### Data Flow

**Registration Flow:**
1. Client sends POST request to `/users/{userId}/registrations`
2. Lambda validates user and event existence
3. Lambda checks event capacity
4. If capacity available: Add to registrations, decrement capacity
5. If full with waitlist: Add to waitlist
6. If full without waitlist: Return 409 Conflict
7. Return registration status to client

**Unregistration Flow:**
1. Client sends DELETE request to `/users/{userId}/registrations/{eventId}`
2. Lambda validates registration exists
3. Lambda removes registration, increments capacity
4. If waitlist exists: Promote first waitlist user automatically
5. Return success to client

### Database Design

**Three DynamoDB Tables:**

1. **UsersTable** (New)
   - Partition Key: `userId`
   - Stores user profile information

2. **EventsTable** (Existing - Modified)
   - Partition Key: `eventId`
   - Add fields: `registeredCount`, `waitlistEnabled`, `waitlist`

3. **RegistrationsTable** (New)
   - Partition Key: `userId`
   - Sort Key: `eventId`
   - GSI: `eventId-userId-index` for reverse lookups
   - Stores registration status (confirmed/waitlist)

## Components and Interfaces

### 1. User Management Component

**Responsibilities:**
- Create and validate user accounts
- Retrieve user information
- Validate user existence for registration operations

**API Endpoints:**

```python
POST /users
  Request: {"userId": "string", "name": "string"}
  Response: 201 Created, User object
  Errors: 400 (validation), 409 (duplicate)

GET /users/{userId}
  Response: 200 OK, User object
  Errors: 404 (not found)
```

### 2. Event Management Component (Extended)

**Responsibilities:**
- Existing event CRUD operations
- Track registration counts and capacity
- Manage waitlist configuration

**Modified Event Model:**
```python
class Event(EventBase):
    eventId: str
    capacity: int
    registeredCount: int = 0
    waitlistEnabled: bool = False
    waitlist: list[str] = []  # List of userIds
    createdAt: str
    updatedAt: str
```

### 3. Registration Management Component

**Responsibilities:**
- Handle registration requests
- Enforce capacity constraints
- Manage waitlist operations
- Automatic waitlist promotion
- Track registration status

**API Endpoints:**

```python
POST /users/{userId}/registrations
  Request: {"eventId": "string"}
  Response: 201 Created, Registration object
  Errors: 400 (validation), 404 (user/event not found), 
          409 (already registered/event full)

DELETE /users/{userId}/registrations/{eventId}
  Response: 204 No Content
  Errors: 404 (registration not found)

GET /users/{userId}/registrations
  Response: 200 OK, List of Registration objects
  Errors: 404 (user not found)
```

### 4. Capacity Management Component

**Responsibilities:**
- Atomic capacity checks and updates
- Prevent race conditions on last spot
- Coordinate registration and capacity changes

**Internal Operations:**
```python
def check_and_reserve_spot(event_id: str, user_id: str) -> RegistrationStatus
def release_spot(event_id: str, user_id: str) -> None
def promote_from_waitlist(event_id: str) -> Optional[str]
```

## Data Models

### User Model

```python
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100, 
                       pattern="^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=200)

class User(BaseModel):
    userId: str
    name: str
    createdAt: str
    updatedAt: str
```

**Validation Rules:**
- `userId`: Alphanumeric, hyphens, underscores only
- `name`: Cannot be empty or whitespace-only
- Both fields are required

### Registration Model

```python
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
```

**Registration Status:**
- `confirmed`: User has a confirmed spot
- `waitlist`: User is on the waitlist

### Extended Event Model

```python
class EventCreate(EventBase):
    eventId: Optional[str] = None
    waitlistEnabled: bool = False

class Event(EventBase):
    eventId: str
    capacity: int
    registeredCount: int = 0
    availableSpots: int  # Computed: capacity - registeredCount
    waitlistEnabled: bool
    waitlistCount: int  # Computed: len(waitlist)
    createdAt: str
    updatedAt: str
```

### DynamoDB Schema

**UsersTable:**
```json
{
  "userId": "user123",
  "name": "John Doe",
  "createdAt": "2025-12-03T10:00:00Z",
  "updatedAt": "2025-12-03T10:00:00Z"
}
```

**EventsTable (Extended):**
```json
{
  "eventId": "event456",
  "title": "Tech Conference",
  "description": "...",
  "date": "2025-06-15T09:00:00Z",
  "location": "San Francisco",
  "capacity": 100,
  "registeredCount": 95,
  "organizer": "Tech Corp",
  "status": "published",
  "waitlistEnabled": true,
  "waitlist": ["user789", "user012"],
  "createdAt": "2025-12-01T10:00:00Z",
  "updatedAt": "2025-12-03T10:00:00Z"
}
```

**RegistrationsTable:**
```json
{
  "userId": "user123",
  "eventId": "event456",
  "status": "confirmed",
  "registeredAt": "2025-12-03T10:00:00Z"
}
```

**GSI: eventId-userId-index**
- Partition Key: `eventId`
- Sort Key: `userId`
- Purpose: Query all registrations for an event


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### User Management Properties

**Property 1: User creation round-trip**
*For any* valid user with userId and name, creating the user then retrieving it should return the same user information.
**Validates: Requirements 1.1**

**Property 2: Duplicate userId rejection**
*For any* user that has been successfully created, attempting to create another user with the same userId should be rejected with an error.
**Validates: Requirements 1.2**

**Property 3: Whitespace name rejection**
*For any* string composed entirely of whitespace characters, attempting to create a user with that name should be rejected with an error.
**Validates: Requirements 1.3**

**Property 4: Whitespace userId rejection**
*For any* string composed entirely of whitespace characters, attempting to create a user with that userId should be rejected with an error.
**Validates: Requirements 1.4**

### Event Capacity Properties

**Property 5: Capacity enforcement**
*For any* event with capacity N, after N successful registrations, the (N+1)th registration attempt should either be rejected (if no waitlist) or added to waitlist (if waitlist enabled).
**Validates: Requirements 2.1**

**Property 6: Waitlist acceptance when full**
*For any* event with waitlist enabled and at full capacity, registration attempts should add users to the waitlist rather than rejecting them.
**Validates: Requirements 2.2**

**Property 7: Rejection when full without waitlist**
*For any* event without waitlist enabled and at full capacity, registration attempts should be rejected with an error.
**Validates: Requirements 2.3**

### Registration Properties

**Property 8: Registration capacity invariant**
*For any* event, after a successful registration, the registeredCount should increase by 1 and availableSpots should decrease by 1.
**Validates: Requirements 3.1**

**Property 9: Duplicate registration rejection**
*For any* user already registered for an event, attempting to register again for the same event should be rejected with an error.
**Validates: Requirements 3.2**

**Property 10: Registration persistence round-trip**
*For any* valid registration, after registering a user for an event, querying that user's registrations should include the event.
**Validates: Requirements 3.3**

**Property 11: Non-existent event rejection**
*For any* non-existent eventId, attempting to register a user for that event should be rejected with an error.
**Validates: Requirements 3.4**

**Property 12: Non-existent user rejection**
*For any* non-existent userId, attempting to register that user for an event should be rejected with an error.
**Validates: Requirements 3.5**

### Waitlist Properties

**Property 13: Waitlist addition when full**
*For any* event with waitlist enabled and at full capacity, registering a user should add them to the waitlist with status "waitlist".
**Validates: Requirements 4.1**

**Property 14: Full event rejection without waitlist**
*For any* event without waitlist and at full capacity, registration attempts should be rejected with an error indicating the event is full.
**Validates: Requirements 4.2**

**Property 15: Duplicate waitlist rejection**
*For any* user already on the waitlist for an event, attempting to register again should be rejected with an error.
**Validates: Requirements 4.3**

**Property 16: Waitlist FIFO ordering**
*For any* sequence of users added to a waitlist, the order in which they are promoted should match the order in which they were added (first-in, first-out).
**Validates: Requirements 4.4**

### Unregistration Properties

**Property 17: Unregistration capacity invariant**
*For any* confirmed registration, after unregistering, the registeredCount should decrease by 1 and availableSpots should increase by 1.
**Validates: Requirements 5.1**

**Property 18: Automatic waitlist promotion**
*For any* event with a non-empty waitlist, when a user unregisters, the first user on the waitlist should be automatically promoted to confirmed status and removed from the waitlist.
**Validates: Requirements 5.2**

**Property 19: Invalid unregistration rejection**
*For any* user not registered for an event, attempting to unregister from that event should be rejected with an error.
**Validates: Requirements 5.3**

**Property 20: Unregistration persistence round-trip**
*For any* confirmed registration, after unregistering, querying that user's registrations should not include the event.
**Validates: Requirements 5.4**

**Property 21: Waitlist removal preserves order**
*For any* waitlist with multiple users, removing a user from the waitlist should maintain the relative order of the remaining users.
**Validates: Requirements 5.5**

### Registration Query Properties

**Property 22: Complete registration list**
*For any* user registered for N events, querying their registrations should return exactly N registrations.
**Validates: Requirements 6.1**

**Property 23: Registration status inclusion**
*For any* user with both confirmed and waitlist registrations, querying their registrations should return both types.
**Validates: Requirements 6.3**

**Property 24: Registration status accuracy**
*For any* registration returned in a query, the status field should accurately reflect whether the registration is confirmed or on the waitlist.
**Validates: Requirements 6.4**

### System Invariants

**Property 25: Capacity conservation invariant**
*For any* event at any point in time, the equation `registeredCount + availableSpots = capacity` must hold true.
**Validates: Requirements 7.1**

**Property 26: Atomic waitlist promotion**
*For any* waitlist promotion, the promoted user should appear in the registrations table with status "confirmed" and should not appear in the event's waitlist array.
**Validates: Requirements 7.2**

## Error Handling

### Error Response Format

Following the API standards, all errors return structured responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [],
    "timestamp": "2025-12-03T10:00:00Z",
    "path": "/users/user123/registrations",
    "requestId": "req-abc-123"
  }
}
```

### Error Codes

**User Management Errors:**
- `USER_NOT_FOUND` (404): User does not exist
- `DUPLICATE_USER` (409): User with userId already exists
- `INVALID_USER_DATA` (400): Validation failed (empty/whitespace fields)

**Event Management Errors:**
- `EVENT_NOT_FOUND` (404): Event does not exist
- `INVALID_EVENT_DATA` (400): Validation failed (invalid capacity, etc.)

**Registration Errors:**
- `ALREADY_REGISTERED` (409): User already registered for event
- `EVENT_FULL` (409): Event at capacity with no waitlist
- `REGISTRATION_NOT_FOUND` (404): Registration does not exist
- `INVALID_REGISTRATION_DATA` (400): Validation failed

**System Errors:**
- `INTERNAL_ERROR` (500): Unexpected server error
- `CONCURRENT_MODIFICATION` (409): Optimistic locking failure

### Error Handling Strategy

1. **Input Validation**: Validate all inputs before database operations
2. **Existence Checks**: Verify referenced entities exist before operations
3. **Atomic Operations**: Use DynamoDB conditional expressions for consistency
4. **Graceful Degradation**: Return partial results when possible
5. **Detailed Logging**: Log all errors with context for debugging

### Validation Rules

**User Validation:**
- `userId`: Required, 1-100 chars, alphanumeric with hyphens/underscores
- `name`: Required, 1-200 chars, not all whitespace

**Event Validation:**
- `capacity`: Required, must be > 0
- `waitlistEnabled`: Boolean, defaults to false

**Registration Validation:**
- `userId`: Must reference existing user
- `eventId`: Must reference existing event
- User cannot be registered twice for same event

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

**User Management:**
- Create user with valid data
- Reject empty userId/name
- Reject duplicate userId
- Retrieve existing user
- Handle non-existent user

**Registration Management:**
- Register user for event with capacity
- Reject duplicate registration
- Add to waitlist when full
- Reject when full without waitlist
- Unregister and free spot
- Promote from waitlist on unregister

**Edge Cases:**
- Zero capacity events
- Negative capacity events
- Empty waitlists
- Single-user waitlists
- Concurrent last-spot registrations

### Property-Based Testing

Property-based testing will verify universal properties across all inputs using **Hypothesis** (Python property-based testing library).

**Configuration:**
- Minimum 100 iterations per property test
- Random generation of users, events, and registration sequences
- Shrinking enabled to find minimal failing cases

**Test Tagging:**
Each property-based test will be tagged with:
```python
# Feature: user-registration, Property 1: User creation round-trip
```

**Property Test Coverage:**

1. **User Properties** (Properties 1-4)
   - Generate random valid/invalid user data
   - Test creation, retrieval, and validation

2. **Capacity Properties** (Properties 5-7)
   - Generate events with random capacities
   - Test capacity enforcement across various scenarios

3. **Registration Properties** (Properties 8-12)
   - Generate random registration sequences
   - Test invariants and error conditions

4. **Waitlist Properties** (Properties 13-16)
   - Generate events with/without waitlists
   - Test waitlist behavior and ordering

5. **Unregistration Properties** (Properties 17-21)
   - Generate registration/unregistration sequences
   - Test capacity updates and waitlist promotion

6. **Query Properties** (Properties 22-24)
   - Generate users with multiple registrations
   - Test query completeness and accuracy

7. **Invariant Properties** (Properties 25-26)
   - Test system invariants hold after all operations
   - Verify atomic operations

**Test Generators:**

```python
@st.composite
def user_strategy(draw):
    """Generate random valid users"""
    return {
        "userId": draw(st.text(min_size=1, max_size=100, 
                              alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), 
                                                    whitelist_characters='-_'))),
        "name": draw(st.text(min_size=1, max_size=200).filter(lambda s: s.strip()))
    }

@st.composite
def event_strategy(draw):
    """Generate random valid events"""
    return {
        "eventId": draw(st.text(min_size=1, max_size=100)),
        "capacity": draw(st.integers(min_value=1, max_value=1000)),
        "waitlistEnabled": draw(st.booleans())
    }

@st.composite
def registration_sequence_strategy(draw):
    """Generate random sequences of registration operations"""
    num_users = draw(st.integers(min_value=1, max_value=20))
    num_events = draw(st.integers(min_value=1, max_value=10))
    operations = draw(st.lists(
        st.tuples(
            st.sampled_from(['register', 'unregister']),
            st.integers(min_value=0, max_value=num_users-1),
            st.integers(min_value=0, max_value=num_events-1)
        ),
        min_size=1,
        max_size=100
    ))
    return operations
```

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Complete Registration Flow**
   - Create user → Create event → Register → Verify registration

2. **Waitlist Flow**
   - Fill event → Add to waitlist → Unregister → Verify promotion

3. **Multi-User Scenarios**
   - Multiple users registering for same event
   - User registering for multiple events

4. **Error Scenarios**
   - Invalid references
   - Duplicate operations
   - Capacity violations

### Test Data Management

**Test Fixtures:**
- Predefined users for consistent testing
- Events with various capacity configurations
- Registration scenarios (empty, partial, full, waitlist)

**Cleanup:**
- Delete test data after each test
- Use unique IDs to avoid conflicts
- Separate test and production tables

### Performance Testing

**Load Testing:**
- Concurrent registrations for popular events
- Bulk user creation
- Large registration list queries

**Benchmarks:**
- Registration operation < 200ms
- Query operations < 100ms
- Waitlist promotion < 300ms

## Implementation Notes

### DynamoDB Considerations

**Conditional Writes:**
Use conditional expressions to prevent race conditions:

```python
# Prevent duplicate registrations
table.put_item(
    Item=registration,
    ConditionExpression='attribute_not_exists(userId) AND attribute_not_exists(eventId)'
)

# Atomic capacity decrement
table.update_item(
    Key={'eventId': event_id},
    UpdateExpression='SET registeredCount = registeredCount + :inc',
    ConditionExpression='registeredCount < capacity',
    ExpressionAttributeValues={':inc': 1}
)
```

**Transaction Support:**
Use DynamoDB transactions for multi-item operations:

```python
# Atomic waitlist promotion
dynamodb.transact_write_items(
    TransactItems=[
        {
            'Update': {
                'TableName': 'EventsTable',
                'Key': {'eventId': event_id},
                'UpdateExpression': 'REMOVE waitlist[0] SET registeredCount = registeredCount + :inc',
                'ExpressionAttributeValues': {':inc': 1}
            }
        },
        {
            'Update': {
                'TableName': 'RegistrationsTable',
                'Key': {'userId': promoted_user_id, 'eventId': event_id},
                'UpdateExpression': 'SET #status = :confirmed',
                'ExpressionAttributeNames': {'#status': 'status'},
                'ExpressionAttributeValues': {':confirmed': 'confirmed'}
            }
        }
    ]
)
```

### API Design Considerations

**RESTful Resource Nesting:**
- `/users/{userId}/registrations` - User-centric view
- `/events/{eventId}/registrations` - Event-centric view (future)

**Idempotency:**
- POST operations use conditional writes
- DELETE operations check existence first
- PUT operations are naturally idempotent

**Pagination:**
- Registration lists support pagination for users with many registrations
- Follow API standards for pagination format

### Security Considerations

**Authorization:**
- Users can only register/unregister themselves
- Event organizers can view all registrations (future)
- Admin role can manage all resources (future)

**Input Sanitization:**
- Validate all string inputs
- Prevent injection attacks
- Limit string lengths

**Rate Limiting:**
- Prevent registration spam
- Protect against denial-of-service
- Per-user and per-IP limits

### Monitoring and Observability

**Metrics:**
- Registration success/failure rates
- Waitlist promotion frequency
- Average registration latency
- Capacity utilization per event

**Logging:**
- All registration operations
- Waitlist promotions
- Error conditions with context
- Performance metrics

**Alerts:**
- High error rates
- Slow response times
- Capacity threshold warnings
- Failed waitlist promotions

## Migration Strategy

### Database Migration

1. **Create New Tables:**
   - Deploy UsersTable
   - Deploy RegistrationsTable
   - Add GSI to RegistrationsTable

2. **Extend EventsTable:**
   - Add `registeredCount` field (default 0)
   - Add `waitlistEnabled` field (default false)
   - Add `waitlist` field (default empty list)

3. **Backfill Data:**
   - No existing data to migrate (new feature)

### API Versioning

- New endpoints under `/users` and `/users/{userId}/registrations`
- Existing `/events` endpoints remain unchanged
- No breaking changes to existing API

### Rollout Plan

1. **Phase 1**: Deploy infrastructure (tables, Lambda updates)
2. **Phase 2**: Deploy user management endpoints
3. **Phase 3**: Deploy registration endpoints
4. **Phase 4**: Enable for production traffic
5. **Phase 5**: Monitor and optimize

## Future Enhancements

**Potential Extensions:**
- Email notifications for registrations and waitlist promotions
- Event capacity changes with automatic waitlist processing
- Registration deadlines and automatic unregistration
- Payment integration for paid events
- Group registrations
- Registration transfers between users
- Event-centric registration views for organizers
- Analytics and reporting dashboards
- Waitlist position tracking
- Registration history and audit logs
