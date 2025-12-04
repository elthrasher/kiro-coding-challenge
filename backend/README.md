# Events API Backend

FastAPI REST API for managing events with CRUD operations.

## Features

- **CRUD Operations**: Create, Read, Update, Delete events
- **DynamoDB Storage**: Serverless, scalable data storage
- **CORS Enabled**: Cross-origin requests supported
- **Input Validation**: Pydantic models for data validation
- **Lambda Ready**: Mangum adapter for AWS Lambda deployment

## Event Schema

```json
{
  "eventId": "uuid",
  "title": "string (1-200 chars)",
  "description": "string (max 1000 chars)",
  "date": "ISO date string",
  "location": "string (1-200 chars)",
  "capacity": "integer (> 0)",
  "organizer": "string (1-100 chars)",
  "status": "draft|published|cancelled|completed",
  "createdAt": "ISO timestamp",
  "updatedAt": "ISO timestamp"
}
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /events` - Create new event
- `GET /events` - List all events (optional `?status=` filter)
- `GET /events/{eventId}` - Get specific event
- `PUT /events/{eventId}` - Update event
- `DELETE /events/{eventId}` - Delete event

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export EVENTS_TABLE_NAME=EventsTable

# Run locally (requires local DynamoDB or AWS credentials)
uvicorn main:app --reload
```

API will be available at http://localhost:8000

## Deployment

See `../infrastructure/README.md` for deployment instructions.
