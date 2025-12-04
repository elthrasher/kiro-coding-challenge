---
inclusion: fileMatch
fileMatchPattern: "**/main.py|**/api*.py|**/routes*.py|**/endpoints*.py"
---

# API Standards and Conventions

This document defines the REST API standards and conventions for this project. These guidelines ensure consistency, predictability, and best practices across all API endpoints.

## HTTP Methods

Use HTTP methods according to their semantic meaning:

### GET
- **Purpose**: Retrieve resources
- **Idempotent**: Yes
- **Safe**: Yes (no side effects)
- **Request Body**: Not allowed
- **Success Codes**: 200 (OK), 206 (Partial Content)
- **Example**: `GET /events` - List all events

### POST
- **Purpose**: Create new resources
- **Idempotent**: No
- **Safe**: No
- **Request Body**: Required
- **Success Codes**: 201 (Created), 202 (Accepted)
- **Response**: Include `Location` header with new resource URI
- **Example**: `POST /events` - Create a new event

### PUT
- **Purpose**: Update/replace entire resource
- **Idempotent**: Yes
- **Safe**: No
- **Request Body**: Required (full resource)
- **Success Codes**: 200 (OK), 204 (No Content)
- **Example**: `PUT /events/{id}` - Replace entire event

### PATCH
- **Purpose**: Partial update of resource
- **Idempotent**: Yes (should be)
- **Safe**: No
- **Request Body**: Required (partial resource)
- **Success Codes**: 200 (OK), 204 (No Content)
- **Example**: `PATCH /events/{id}` - Update specific fields

### DELETE
- **Purpose**: Remove resources
- **Idempotent**: Yes
- **Safe**: No
- **Request Body**: Not allowed
- **Success Codes**: 200 (OK), 204 (No Content), 202 (Accepted)
- **Example**: `DELETE /events/{id}` - Delete an event

## HTTP Status Codes

### Success Codes (2xx)

- **200 OK**: Request succeeded, response includes body
  - Use for: GET, PUT, PATCH with response body
  
- **201 Created**: Resource successfully created
  - Use for: POST operations
  - Must include: `Location` header or resource ID in response
  
- **204 No Content**: Request succeeded, no response body
  - Use for: DELETE, PUT, PATCH without response body
  
- **206 Partial Content**: Partial data returned (pagination)
  - Use for: GET with range/pagination

### Client Error Codes (4xx)

- **400 Bad Request**: Invalid request syntax or validation error
  - Use for: Malformed JSON, validation failures
  - Include: Detailed error message and field-level errors
  
- **401 Unauthorized**: Authentication required or failed
  - Use for: Missing or invalid authentication credentials
  
- **403 Forbidden**: Authenticated but not authorized
  - Use for: Insufficient permissions
  
- **404 Not Found**: Resource does not exist
  - Use for: Invalid resource ID
  - Include: Clear message about what was not found
  
- **409 Conflict**: Request conflicts with current state
  - Use for: Duplicate resources, version conflicts
  
- **422 Unprocessable Entity**: Validation error
  - Use for: Semantic validation failures
  - Include: Field-level validation errors
  
- **429 Too Many Requests**: Rate limit exceeded
  - Include: `Retry-After` header

### Server Error Codes (5xx)

- **500 Internal Server Error**: Unexpected server error
  - Use for: Unhandled exceptions
  - Never expose: Stack traces or internal details
  
- **502 Bad Gateway**: Invalid response from upstream
  - Use for: External service failures
  
- **503 Service Unavailable**: Temporary unavailability
  - Use for: Maintenance, overload
  - Include: `Retry-After` header
  
- **504 Gateway Timeout**: Upstream timeout
  - Use for: External service timeouts

## JSON Response Format Standards

### Success Response Format

```json
{
  "data": {
    "id": "123",
    "attribute": "value"
  },
  "meta": {
    "timestamp": "2025-12-04T00:00:00Z",
    "version": "1.0"
  }
}
```

For collections:

```json
{
  "data": [
    {"id": "1", "name": "Item 1"},
    {"id": "2", "name": "Item 2"}
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "timestamp": "2025-12-04T00:00:00Z"
  }
}
```

### Error Response Format

All error responses must follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ],
    "timestamp": "2025-12-04T00:00:00Z",
    "path": "/api/users",
    "requestId": "req-123-456"
  }
}
```

### Error Response Fields

- **code**: Machine-readable error code (UPPER_SNAKE_CASE)
- **message**: Human-readable error description
- **details**: Array of field-level errors (optional)
- **timestamp**: ISO 8601 timestamp
- **path**: Request path that caused the error
- **requestId**: Unique request identifier for tracing

### Common Error Codes

```python
ERROR_CODES = {
    "VALIDATION_ERROR": "Request validation failed",
    "RESOURCE_NOT_FOUND": "Requested resource does not exist",
    "DUPLICATE_RESOURCE": "Resource already exists",
    "UNAUTHORIZED": "Authentication required",
    "FORBIDDEN": "Insufficient permissions",
    "RATE_LIMIT_EXCEEDED": "Too many requests",
    "INTERNAL_ERROR": "Internal server error",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable"
}
```

## Naming Conventions

### Endpoints

- Use **plural nouns** for collections: `/events`, `/users`
- Use **kebab-case** for multi-word resources: `/event-categories`
- Use **path parameters** for resource IDs: `/events/{eventId}`
- Use **query parameters** for filtering: `/events?status=active&limit=10`

### JSON Fields

- Use **camelCase** for field names: `firstName`, `createdAt`
- Use **ISO 8601** for dates: `2025-12-04T00:00:00Z`
- Use **consistent naming**: `id` not `ID` or `Id`

## Pagination

For list endpoints, support pagination:

```
GET /events?page=1&pageSize=20&sort=createdAt&order=desc
```

Response:

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5,
    "hasNext": true,
    "hasPrevious": false
  },
  "links": {
    "self": "/events?page=1&pageSize=20",
    "next": "/events?page=2&pageSize=20",
    "previous": null,
    "first": "/events?page=1&pageSize=20",
    "last": "/events?page=5&pageSize=20"
  }
}
```

## Filtering and Sorting

### Filtering

```
GET /events?status=active&location=SF&capacity[gte]=100
```

Operators:
- `field=value` - Exact match
- `field[gte]=value` - Greater than or equal
- `field[lte]=value` - Less than or equal
- `field[in]=val1,val2` - In list

### Sorting

```
GET /events?sort=createdAt&order=desc
```

Or multiple fields:

```
GET /events?sort=status,createdAt&order=asc,desc
```

## Versioning

Use URL path versioning:

```
/v1/events
/v2/events
```

- Always include version in URL
- Maintain backward compatibility within major versions
- Deprecate old versions with clear timeline

## CORS Headers

Always include appropriate CORS headers:

```python
Access-Control-Allow-Origin: *  # Or specific domains
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 86400
```

## Request/Response Headers

### Required Request Headers

- `Content-Type: application/json` (for POST/PUT/PATCH)
- `Accept: application/json`
- `Authorization: Bearer <token>` (for authenticated endpoints)

### Standard Response Headers

- `Content-Type: application/json`
- `X-Request-ID: <unique-id>` (for request tracing)
- `X-RateLimit-Limit: 1000`
- `X-RateLimit-Remaining: 999`
- `X-RateLimit-Reset: 1638360000`

## Validation Rules

### Input Validation

1. **Type Validation**: Ensure correct data types
2. **Format Validation**: Email, URL, date formats
3. **Range Validation**: Min/max values, string lengths
4. **Business Logic Validation**: Domain-specific rules

### Validation Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "INVALID_FORMAT",
        "value": "invalid-email"
      },
      {
        "field": "capacity",
        "message": "Must be greater than 0",
        "code": "OUT_OF_RANGE",
        "value": -5
      }
    ]
  }
}
```

## Security Best Practices

1. **Never expose sensitive data** in error messages
2. **Sanitize all inputs** to prevent injection attacks
3. **Use HTTPS** for all API endpoints
4. **Implement rate limiting** to prevent abuse
5. **Validate content types** to prevent MIME confusion
6. **Use parameterized queries** to prevent SQL injection
7. **Implement proper authentication** and authorization
8. **Log security events** for audit trails

## Documentation Requirements

Every endpoint must document:

1. **Purpose**: What the endpoint does
2. **Authentication**: Required permissions
3. **Request**: Parameters, headers, body schema
4. **Response**: Success and error responses with examples
5. **Status Codes**: All possible status codes
6. **Rate Limits**: Request limits if applicable

Example:

```python
@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """
    Create a new event.
    
    Args:
        event: Event data including title, description, date, location, etc.
    
    Returns:
        Event: Created event with generated ID and timestamps
    
    Raises:
        400: Invalid request data or validation error
        409: Event with same ID already exists
        500: Internal server error
    
    Rate Limit: 100 requests per minute
    """
    pass
```

## Testing Requirements

All API endpoints must have:

1. **Unit tests** for business logic
2. **Integration tests** for database operations
3. **API tests** for HTTP layer
4. **Error case tests** for all error scenarios
5. **Performance tests** for critical endpoints

## Monitoring and Logging

Log the following for each request:

```json
{
  "timestamp": "2025-12-04T00:00:00Z",
  "requestId": "req-123-456",
  "method": "POST",
  "path": "/events",
  "statusCode": 201,
  "duration": 45,
  "userId": "user-123",
  "ip": "192.168.1.1",
  "userAgent": "Mozilla/5.0..."
}
```

## Implementation Checklist

When implementing a new API endpoint:

- [ ] Follow HTTP method semantics
- [ ] Return appropriate status codes
- [ ] Use standard JSON response format
- [ ] Include proper error handling
- [ ] Add input validation
- [ ] Implement pagination (for lists)
- [ ] Add filtering and sorting (for lists)
- [ ] Include CORS headers
- [ ] Add authentication/authorization
- [ ] Write comprehensive documentation
- [ ] Add unit and integration tests
- [ ] Implement logging and monitoring
- [ ] Consider rate limiting
- [ ] Review security implications
