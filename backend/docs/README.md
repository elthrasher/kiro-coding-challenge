# API Documentation

This directory contains auto-generated API documentation for the Events API backend.

## Contents

- **index.html** - Documentation index page
- **main.html** - Complete API documentation for the main module

## Viewing the Documentation

Open the documentation in your browser:

```bash
# From the backend directory
open docs/index.html

# Or on Linux
xdg-open docs/index.html
```

## Regenerating Documentation

To regenerate the documentation after making changes to the code:

```bash
cd backend
pip install pdoc
pdoc main.py -o docs --no-search
```

## What's Documented

The generated documentation includes:

- **Pydantic Models**:
  - `EventBase` - Base event schema
  - `EventCreate` - Schema for creating events
  - `EventUpdate` - Schema for updating events
  - `Event` - Complete event response schema

- **API Endpoints**:
  - `GET /` - API information
  - `GET /health` - Health check
  - `POST /events` - Create event
  - `GET /events` - List events
  - `GET /events/{eventId}` - Get specific event
  - `PUT /events/{eventId}` - Update event
  - `DELETE /events/{eventId}` - Delete event

- **Functions**:
  - `create_event()` - Create a new event
  - `list_events()` - List all events with optional filtering
  - `get_event()` - Retrieve a specific event
  - `update_event()` - Update an existing event
  - `delete_event()` - Delete an event

## Interactive API Documentation

FastAPI also provides built-in interactive documentation when the API is running:

- **Swagger UI**: `https://your-api-url/prod/docs`
- **ReDoc**: `https://your-api-url/prod/redoc`

These interactive docs allow you to:
- View all endpoints and their parameters
- Test API calls directly from the browser
- See request/response schemas
- Download OpenAPI specification

## Notes

- Documentation is generated from Python docstrings and type hints
- The `--no-search` flag is used to avoid compatibility issues with Pydantic v2
- Documentation is automatically styled with syntax highlighting
