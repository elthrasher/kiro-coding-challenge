# Events API Infrastructure

AWS CDK infrastructure for deploying the Events API using API Gateway, Lambda, and DynamoDB.

## Architecture

- **API Gateway**: Public REST API endpoint with CORS enabled
- **Lambda Function**: Runs FastAPI application (Python 3.12)
- **DynamoDB Table**: Stores event data with pay-per-request billing
- **IAM Roles**: Automatic permissions for Lambda to access DynamoDB

## Prerequisites

- AWS CLI configured with credentials
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Python 3.12+
- Docker (for Lambda bundling)

## Setup

```bash
# Install CDK dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap
```

## Deploy

```bash
# Synthesize CloudFormation template
cdk synth

# Deploy to AWS
cdk deploy

# Note the API Gateway URL in the output
```

After deployment, the API Gateway URL will be displayed in the output. Use this URL to access your API.

## Testing the API

```bash
# Get the API URL from CDK output
API_URL="https://your-api-id.execute-api.region.amazonaws.com/prod"

# Health check
curl $API_URL/health

# Create an event
curl -X POST $API_URL/events \
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

# List all events
curl $API_URL/events

# Get specific event
curl $API_URL/events/{eventId}

# Update event
curl -X PUT $API_URL/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete event
curl -X DELETE $API_URL/events/{eventId}
```

## Useful Commands

* `cdk ls` - List all stacks
* `cdk synth` - Synthesize CloudFormation template
* `cdk deploy` - Deploy stack to AWS
* `cdk diff` - Compare deployed stack with current state
* `cdk destroy` - Remove all resources from AWS

## Cost Considerations

- **DynamoDB**: Pay-per-request billing (free tier: 25 GB storage, 25 WCU, 25 RCU)
- **Lambda**: Pay per invocation (free tier: 1M requests/month)
- **API Gateway**: Pay per request (free tier: 1M requests/month for 12 months)

## Security Notes

For production:
- Change `RemovalPolicy.DESTROY` to `RemovalPolicy.RETAIN` for DynamoDB
- Restrict CORS origins to specific domains
- Add API Gateway authentication (API keys, Cognito, etc.)
- Enable CloudWatch logging and monitoring
- Add WAF rules for API protection
