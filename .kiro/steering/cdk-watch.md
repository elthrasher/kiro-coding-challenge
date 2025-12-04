# CDK Watch Development Workflow

## Overview

When `cdk watch` is running, it automatically detects changes to your code and deploys them to AWS. This eliminates the need for manual deployment commands during development.

## Key Points

### 1. No Manual Deployment Needed

When `cdk watch` is active:
- ❌ **DON'T** run `cdk deploy` manually
- ❌ **DON'T** run `cdk synth` manually
- ✅ **DO** just save your files and wait for auto-deployment
- ✅ **DO** watch the console output for deployment status

### 2. Console Output Contains Logs

The `cdk watch` console shows:
- File change detection
- Deployment progress
- Lambda function logs in real-time
- Error messages and stack traces
- Deployment completion status

### 3. Reading Logs

**Instead of running separate log commands:**
```bash
# DON'T do this when cdk watch is running:
aws logs tail /aws/lambda/YourFunction --follow
```

**Just read the console output:**
- Logs appear automatically in the `cdk watch` terminal
- Look for Lambda execution logs after API calls
- Error messages appear inline with deployment status

### 4. Workflow

```
1. Start cdk watch once:
   cd infrastructure
   ./watch.sh  # or cdk watch

2. Make code changes in backend/main.py

3. Save the file

4. Watch console for:
   - "Detected change to..."
   - "Deploying..."
   - "✅ Deployment complete"

5. Test your API

6. Check console for Lambda logs

7. Repeat from step 2
```

### 5. When to Check Console Logs

After making an API request:
1. Look at the `cdk watch` console
2. Lambda logs appear automatically
3. Check for errors or unexpected behavior
4. No need to run separate log commands

### 6. Stopping CDK Watch

When you're done developing:
```bash
# Press Ctrl+C in the cdk watch terminal
# This stops the watch process but doesn't undeploy
```

## Common Scenarios

### Scenario 1: Testing After Code Changes

```
1. Edit backend/main.py
2. Save file
3. Wait for "✅ Deployment complete" in console
4. Run test script: ./test_registration_api.sh
5. Check cdk watch console for Lambda logs
6. Fix any issues and repeat
```

### Scenario 2: Debugging Errors

```
1. Run API test
2. See error in test output
3. Check cdk watch console for detailed Lambda logs
4. Find the error in the logs
5. Fix code
6. Save and wait for auto-deployment
7. Test again
```

### Scenario 3: Checking Deployment Status

```
Look for these messages in cdk watch console:

✅ Good:
- "Detected change to backend/main.py"
- "Deploying ApiStack..."
- "✅ ApiStack deployed successfully"

❌ Problems:
- "❌ Deployment failed"
- "Error: ..."
- Stack trace messages
```

## Benefits of CDK Watch

1. **Faster Development**: No manual deployment commands
2. **Immediate Feedback**: See logs as they happen
3. **Less Context Switching**: Everything in one terminal
4. **Automatic**: Just save and go

## When NOT to Use CDK Watch

- **Production deployments**: Use `cdk deploy` with proper review
- **Infrastructure changes**: Major CDK stack changes may need manual deployment
- **CI/CD pipelines**: Use explicit `cdk deploy` commands
- **Initial setup**: First deployment should be manual to verify

## Troubleshooting

### CDK Watch Not Detecting Changes

```bash
# Stop and restart cdk watch
Ctrl+C
./watch.sh
```

### Deployment Stuck

```bash
# Check CloudFormation console for stack status
# May need to cancel update and restart
```

### Logs Not Appearing

```bash
# Ensure Lambda has proper logging permissions
# Check CloudWatch Logs directly if needed
aws logs tail /aws/lambda/ApiStack-EventsApiFunction --follow
```

## Quick Reference

| Action | Command | When |
|--------|---------|------|
| Start watch | `./watch.sh` or `cdk watch` | Once at start of dev session |
| Make changes | Edit files | Anytime |
| Deploy | Just save | Automatic |
| Check logs | Look at console | After API calls |
| Stop watch | `Ctrl+C` | End of dev session |
| Manual deploy | `cdk deploy` | Production or major changes |

## Remember

> **When cdk watch is running, the console is your friend. All logs and deployment status appear there automatically.**

Don't run separate commands to:
- Deploy changes (it's automatic)
- Check logs (they're in the console)
- Verify deployment (watch the console output)

Just code, save, and watch the console!
