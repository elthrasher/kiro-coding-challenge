# Events API Deployment Guide

Complete guide to deploy the Events API to AWS.

## Quick Start

```bash
# 1. Navigate to infrastructure directory
cd infrastructure

# 2. Install dependencies
pip install -r requirements.txt

# 3. Bootstrap CDK (first time only)
cdk bootstrap

# 4. Deploy
cdk deploy

# 5. Note the API URL from the output
```

## Detailed Steps

### 1. Prerequisites

Ensure you have:
- AWS account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Python 3.12 or higher
- Node.js and npm (for CDK CLI)
- Docker running (for Lambda packaging)

### 2. Install AWS CDK CLI

```bash
npm install -g aws-cdk
cdk --version
```

### 3. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter output format (json)
```

### 4. Bootstrap CDK

First-time setup for CDK in your AWS account:

```bash
cd infrastructure
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### 5. Review Infrastructure

```bash
# View CloudFormation template
cdk synth

# Check what will be deployed
cdk diff
```

### 6. Deploy

```bash
cdk deploy
```

You'll be asked to confirm security changes. Type 'y' to proceed.

### 7. Get API URL

After deployment, the output will show:

```
Outputs:
ApiStack.EventsApiEndpoint = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
```

Save this URL for testing.

## Testing the Deployment

### Using curl

```bash
# Set your API URL
export API_URL="https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod"

# Test health endpoint
curl $API_URL/health

# Create an event
curl -X POST $API_URL/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sample Event",
    "description": "This is a test event",
    "date": "2025-12-31T18:00:00Z",
    "location": "New York, NY",
    "capacity": 100,
    "organizer": "Event Organizer",
    "status": "published"
  }'
```

### Using Python Script

```bash
cd backend

# Update API_URL in example_requests.py
# Then run:
python example_requests.py
```

## Monitoring

### CloudWatch Logs

View Lambda logs:
```bash
aws logs tail /aws/lambda/ApiStack-EventsApiFunction --follow
```

### DynamoDB Console

View your data in the AWS Console:
1. Go to DynamoDB service
2. Find "EventsTable"
3. Click "Explore table items"

## Updating the API

After making changes to the backend code:

```bash
cd infrastructure
cdk deploy
```

CDK will automatically detect changes and update the Lambda function.

## Cleanup

To remove all resources and avoid charges:

```bash
cd infrastructure
cdk destroy
```

This will delete:
- API Gateway
- Lambda function
- DynamoDB table (and all data)
- IAM roles

## Troubleshooting

### Lambda Timeout
If requests timeout, increase Lambda timeout in `api_stack.py`:
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

### Deployment Fails
- Check AWS credentials: `aws sts get-caller-identity`
- Ensure Docker is running
- Check CDK version: `cdk --version`

## Cost Estimation

With AWS Free Tier:
- **DynamoDB**: Free for 25 GB storage and 25 WCU/RCU
- **Lambda**: Free for 1M requests/month
- **API Gateway**: Free for 1M requests/month (first 12 months)

Typical monthly cost after free tier: $5-20 depending on usage.

## Production Recommendations

1. **Security**:
   - Add API authentication (Cognito, API keys)
   - Restrict CORS to specific domains
   - Enable AWS WAF for API protection

2. **Monitoring**:
   - Set up CloudWatch alarms
   - Enable X-Ray tracing
   - Configure API Gateway access logs

3. **Data**:
   - Change DynamoDB RemovalPolicy to RETAIN
   - Enable point-in-time recovery (already enabled)
   - Set up automated backups

4. **Performance**:
   - Add DynamoDB Global Secondary Indexes if needed
   - Configure Lambda reserved concurrency
   - Enable API Gateway caching
