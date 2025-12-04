# Events API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using CDK.

## Architecture

- **API Gateway**: Public REST API endpoint with CORS enabled
- **AWS Lambda**: Python 3.12 runtime on ARM64 architecture
- **DynamoDB**: NoSQL database with pay-per-request billing
- **FastAPI**: Modern Python web framework with automatic API documentation
- **AWS CDK**: Infrastructure as Code for deployment

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Event filtering by status
- ✅ Custom event IDs support
- ✅ CORS enabled for cross-origin requests
- ✅ Input validation with Pydantic
- ✅ Automatic timestamps (createdAt, updatedAt)
- ✅ RESTful API design with proper HTTP status codes

## Event Schema

```json
{
  "eventId": "string (UUID or custom)",
  "title": "string (1-200 chars)",
  "description": "string (max 1000 chars)",
  "date": "string (ISO date format)",
  "location": "string (1-200 chars)",
  "capacity": "integer (> 0)",
  "organizer": "string (1-100 chars)",
  "status": "draft|published|cancelled|completed|active",
  "createdAt": "string (ISO timestamp)",
  "updatedAt": "string (ISO timestamp)"
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/events` | Create a new event |
| GET | `/events` | List all events (supports `?status=` filter) |
| GET | `/events/{eventId}` | Get a specific event |
| PUT | `/events/{eventId}` | Update an event |
| DELETE | `/events/{eventId}` | Delete an event |

## Setup & Deployment

### Prerequisites

- AWS Account with configured credentials
- AWS CDK CLI: `npm install -g aws-cdk`
- Python 3.12+
- Docker (for Lambda bundling)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install infrastructure dependencies**
   ```bash
   cd infrastructure
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Bootstrap CDK (first time only)**
   ```bash
   cdk bootstrap
   ```

4. **Deploy to AWS**
   ```bash
   cdk deploy
   ```

   The deployment will output your API Gateway URL:
   ```
   Outputs:
   ApiStack.EventsApiEndpoint = https://xxxxxxxxxx.execute-api.region.amazonaws.com/prod/
   ```

### Development with CDK Watch

For faster development iterations, use CDK watch mode:

```bash
cd infrastructure
cdk watch --hotswap-fallback
```

This automatically detects changes in the `backend/` directory and redeploys.

## Usage Examples

### Create an Event

```bash
curl -X POST https://your-api-url/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15T09:00:00Z",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "published"
  }'
```

### List All Events

```bash
curl https://your-api-url/prod/events
```

### Filter Events by Status

```bash
curl https://your-api-url/prod/events?status=published
```

### Get a Specific Event

```bash
curl https://your-api-url/prod/events/{eventId}
```

### Update an Event

```bash
curl -X PUT https://your-api-url/prod/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{
    "capacity": 600,
    "status": "completed"
  }'
```

### Delete an Event

```bash
curl -X DELETE https://your-api-url/prod/events/{eventId}
```

## Testing

Run the automated test suite:

```bash
chmod +x test_api.sh
./test_api.sh
```

Or test individual endpoints manually using the examples above.

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── README.md           # Backend documentation
│   └── example_requests.py # Example API calls
├── infrastructure/
│   ├── app.py              # CDK app entry point
│   ├── cdk.json            # CDK configuration
│   ├── requirements.txt    # CDK dependencies
│   ├── README.md          # Infrastructure documentation
│   └── stacks/
│       └── api_stack.py   # API infrastructure definition
├── test_api.sh            # Automated test script
├── DEPLOYMENT.md          # Detailed deployment guide
└── README.md             # This file
```

## API Documentation

### Interactive Documentation (Live API)

Once deployed, FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `https://your-api-url/prod/docs`
- **ReDoc**: `https://your-api-url/prod/redoc`

### Static Documentation (Code Reference)

Auto-generated code documentation is available in `backend/docs/`:

```bash
# View the documentation
open backend/docs/index.html

# Regenerate after code changes
cd backend
pdoc main.py -o docs --no-search
```

## Cost Estimation

With AWS Free Tier:
- **DynamoDB**: Free for 25 GB storage, 25 WCU, 25 RCU
- **Lambda**: Free for 1M requests/month
- **API Gateway**: Free for 1M requests/month (first 12 months)

Typical monthly cost after free tier: **$5-20** depending on usage.

## Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/ApiStack-EventsApiFunction --follow
```

View DynamoDB table in AWS Console:
1. Navigate to DynamoDB service
2. Find "EventsTable"
3. Click "Explore table items"

## Cleanup

To remove all AWS resources:

```bash
cd infrastructure
cdk destroy
```

This will delete the API Gateway, Lambda function, DynamoDB table (and all data), and IAM roles.

## Security Considerations

For production deployments:

- ✅ Enable API Gateway authentication (API keys, Cognito, IAM)
- ✅ Restrict CORS to specific domains
- ✅ Add AWS WAF rules for API protection
- ✅ Enable CloudWatch logging and monitoring
- ✅ Change DynamoDB RemovalPolicy to RETAIN
- ✅ Set up automated backups
- ✅ Use AWS Secrets Manager for sensitive data
- ✅ Enable API Gateway throttling and rate limiting

## Troubleshooting

### Lambda Timeout
Increase timeout in `infrastructure/stacks/api_stack.py`:
```python
timeout=Duration.seconds(60)
```

### CORS Issues
Verify CORS settings in both:
- `backend/main.py` (FastAPI middleware)
- `infrastructure/stacks/api_stack.py` (API Gateway)

### DynamoDB Access Denied
Ensure Lambda has proper permissions:
```python
events_table.grant_read_write_data(api_lambda)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) guide
- Review AWS CloudWatch logs
- Open an issue on GitHub
