---
inclusion: fileMatch
fileMatchPattern: "**/infrastructure/**/*.py|**/cdk*.json|**/app.py|**/stacks/**/*.py"
---

# AWS Credentials Management

This document provides guidelines for managing AWS credentials when working with AWS CDK, deployment scripts, and AWS service interactions.

## Credential Requirements Check

Before executing any AWS-related commands, always verify that AWS credentials are properly configured.

### When to Prompt for Credentials

Prompt the user for AWS credentials when:

1. **Deploying Infrastructure**
   - Running `cdk deploy`, `cdk bootstrap`, `cdk synth`
   - Executing deployment scripts
   - Running infrastructure tests that interact with AWS

2. **Accessing AWS Services**
   - Reading from or writing to DynamoDB, S3, or other AWS services
   - Invoking Lambda functions
   - Checking CloudWatch logs
   - Listing AWS resources

3. **Running CDK Watch**
   - Starting `cdk watch` or `cdk watch --hotswap-fallback`
   - Background processes that need persistent AWS access

4. **Testing Against Live Resources**
   - Integration tests that connect to real AWS services
   - API tests against deployed endpoints (if they require AWS SDK calls)

### When NOT to Prompt

Do NOT prompt for credentials when:

- Working on local code that doesn't interact with AWS
- Running unit tests with mocked AWS services
- Editing configuration files
- Generating documentation
- Running linters or formatters

## Credential Verification

Before running AWS commands, check if credentials are available:

```bash
# Quick credential check
aws sts get-caller-identity

# If this fails, credentials are not configured
```

## Prompting Template

When credentials are needed, use this template:

```
I need to execute AWS commands that require valid credentials.

Please provide your AWS credentials in one of these ways:

1. **Temporary Session Credentials** (Recommended for security):
   ```bash
   export AWS_DEFAULT_REGION="your-region"
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   export AWS_SESSION_TOKEN="your-session-token"
   ```

2. **Long-term Credentials** (Less secure):
   ```bash
   export AWS_DEFAULT_REGION="your-region"
   export AWS_ACCESS_KEY_ID="your-access-key"
   export AWS_SECRET_ACCESS_KEY="your-secret-key"
   ```

3. **AWS CLI Profile**:
   ```bash
   export AWS_PROFILE="your-profile-name"
   export AWS_DEFAULT_REGION="your-region"
   ```

After providing credentials, I'll proceed with: [describe the operation]
```

## Credential Security Best Practices

### DO:

1. **Use Temporary Credentials**
   - Prefer AWS STS temporary credentials with session tokens
   - These expire automatically, reducing security risk
   - Obtain from AWS SSO, IAM roles, or `aws sts assume-role`

2. **Use Environment Variables**
   - Set credentials as environment variables for the session
   - They won't persist after the terminal closes
   - Example:
     ```bash
     export AWS_ACCESS_KEY_ID="..."
     export AWS_SECRET_ACCESS_KEY="..."
     export AWS_SESSION_TOKEN="..."
     ```

3. **Use AWS Profiles**
   - Configure profiles in `~/.aws/credentials` and `~/.aws/config`
   - Switch between profiles using `AWS_PROFILE` environment variable
   - Keeps credentials separate from code

4. **Verify Credential Scope**
   - Check which AWS account you're using:
     ```bash
     aws sts get-caller-identity
     ```
   - Confirm the account ID matches your intended target

5. **Use IAM Roles When Possible**
   - For EC2, Lambda, ECS: Use IAM roles instead of credentials
   - For local development: Use AWS SSO or temporary credentials

### DON'T:

1. **Never Store Credentials in Code**
   - Don't hardcode credentials in Python files
   - Don't commit credentials to Git
   - Don't include credentials in configuration files

2. **Never Store Credentials in Scripts**
   - Don't put credentials in shell scripts
   - Don't include credentials in deployment scripts
   - Exception: Temporary scripts that are gitignored (like `watch-with-creds.sh`)

3. **Never Share Credentials**
   - Don't share credentials via chat, email, or messaging
   - Don't include credentials in screenshots or logs
   - Don't paste credentials in public forums

4. **Never Use Root Account Credentials**
   - Always use IAM user credentials
   - Follow principle of least privilege
   - Use MFA for sensitive operations

## Handling Credentials in Different Scenarios

### Scenario 1: CDK Deployment

```bash
# Before running cdk deploy, verify credentials
aws sts get-caller-identity

# If credentials are missing, prompt user:
# "I need AWS credentials to deploy the CDK stack. Please provide..."

# Then run deployment
cdk deploy
```

### Scenario 2: Background Processes (CDK Watch)

For long-running processes like `cdk watch`, credentials must be available in the environment:

```bash
# Option 1: Export credentials before starting
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
cdk watch --hotswap-fallback

# Option 2: Create a temporary script (gitignored)
# infrastructure/watch-with-creds.sh
#!/bin/bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
source venv/bin/activate
cdk watch --hotswap-fallback
```

**Important**: Always add credential-containing scripts to `.gitignore`

### Scenario 3: Testing Against Live AWS

```bash
# Before running integration tests
export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."

# Run tests
pytest tests/integration/
```

### Scenario 4: Checking Logs

```bash
# Verify credentials first
aws sts get-caller-identity

# Then access logs
aws logs tail /aws/lambda/MyFunction --follow
```

## Credential Expiration

### Detecting Expired Credentials

Temporary credentials expire. Watch for these errors:

```
ExpiredToken: The security token included in the request is expired
InvalidClientTokenId: The security token included in the request is invalid
```

### Handling Expiration

When credentials expire:

1. **Stop any running processes** (like `cdk watch`)
2. **Obtain fresh credentials** from your credential source
3. **Re-export environment variables** with new credentials
4. **Restart the process**

Example:

```bash
# Stop the watch process
# Ctrl+C or kill the process

# Get new credentials and export them
export AWS_ACCESS_KEY_ID="new-key"
export AWS_SECRET_ACCESS_KEY="new-secret"
export AWS_SESSION_TOKEN="new-token"

# Restart watch
cdk watch --hotswap-fallback
```

## Credential Sources

### 1. AWS SSO (Recommended)

```bash
# Configure SSO
aws configure sso

# Login
aws sso login --profile my-profile

# Use the profile
export AWS_PROFILE=my-profile
```

### 2. IAM User with MFA

```bash
# Get temporary credentials with MFA
aws sts get-session-token \
  --serial-number arn:aws:iam::ACCOUNT:mfa/USER \
  --token-code 123456

# Export the returned credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

### 3. Assume Role

```bash
# Assume a role
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT:role/ROLE \
  --role-session-name my-session

# Export the returned credentials
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
```

### 4. Environment Variables (Direct)

```bash
# Set directly (least secure, use only for temporary work)
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."  # Optional, for temporary credentials
export AWS_DEFAULT_REGION="us-west-2"
```

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution**: Credentials are not configured. Prompt user for credentials.

### Issue: "ExpiredToken"

**Solution**: Credentials have expired. Request fresh credentials from user.

### Issue: "Access Denied"

**Solution**: Credentials lack necessary permissions. Verify IAM policies.

### Issue: "Invalid security token"

**Solution**: Session token is invalid or expired. Get new temporary credentials.

## Credential Checklist

Before running AWS operations:

- [ ] Verify credentials are needed for this operation
- [ ] Check if credentials are already configured (`aws sts get-caller-identity`)
- [ ] If missing, prompt user with clear instructions
- [ ] Specify which AWS operations will be performed
- [ ] Confirm the AWS region is correct
- [ ] For long-running processes, warn about credential expiration
- [ ] Never store credentials in version control
- [ ] Use temporary credentials when possible
- [ ] Verify you're in the correct AWS account

## Example Prompts

### For CDK Deployment

```
I need to deploy the CDK stack to AWS. This requires valid AWS credentials.

Please provide your AWS credentials by running:

export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"

Once set, I'll proceed with:
1. Synthesizing the CloudFormation template
2. Deploying to AWS account: [account-id]
3. Creating/updating resources: API Gateway, Lambda, DynamoDB
```

### For CDK Watch

```
I need to start CDK watch mode for automatic deployments. This requires persistent AWS credentials.

Since this is a long-running process, please provide credentials that won't expire soon.

Options:
1. Use AWS SSO with long-lived session
2. Provide temporary credentials (will need refresh when expired)
3. Use IAM user credentials (less secure)

Please export your credentials, then I'll start the watch process.
```

### For Log Access

```
I need to check Lambda function logs in CloudWatch. This requires AWS credentials.

Please provide credentials with CloudWatch Logs read permissions:

export AWS_DEFAULT_REGION="us-west-2"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"

I'll then fetch logs from: /aws/lambda/[function-name]
```

## Integration with CI/CD

For automated deployments:

1. **Use IAM Roles** for CI/CD runners (GitHub Actions, GitLab CI, etc.)
2. **Use OIDC** for secure, temporary credential access
3. **Never store credentials** in CI/CD environment variables
4. **Use AWS Secrets Manager** or similar for sensitive values
5. **Rotate credentials regularly**

## Summary

- **Always verify** credentials before AWS operations
- **Prompt clearly** when credentials are needed
- **Use temporary credentials** whenever possible
- **Never commit credentials** to version control
- **Handle expiration gracefully** for long-running processes
- **Follow security best practices** at all times
