---
inclusion: always
---

# Documentation Check Reminder

Always check existing documentation before implementing features, making changes, or answering questions about the project.

## Documentation Locations

### Project Documentation

1. **README.md** (Root)
   - Project overview and architecture
   - Setup and deployment instructions
   - Usage examples
   - API endpoint summary
   - Cost estimation
   - Troubleshooting guide

2. **DEPLOYMENT.md**
   - Detailed deployment steps
   - Prerequisites and requirements
   - CDK bootstrap instructions
   - Testing procedures
   - Cleanup instructions
   - Production recommendations

3. **TEST_RESULTS.md**
   - Test execution results
   - API endpoint validation
   - Status code verification
   - Feature implementation checklist

### Backend Documentation

4. **backend/README.md**
   - Backend-specific setup
   - Event schema details
   - API endpoints reference
   - Local development guide
   - Deployment notes

5. **backend/docs/** (Generated API Docs)
   - `index.html` - Documentation index
   - `main.html` - Complete API reference
   - `README.md` - Documentation guide
   - Auto-generated from code with pdoc

6. **backend/example_requests.py**
   - Working code examples
   - API usage patterns
   - Test scenarios

### Infrastructure Documentation

7. **infrastructure/README.md**
   - CDK infrastructure overview
   - Architecture components
   - Deployment commands
   - Testing instructions
   - Cost considerations
   - Security notes

### Steering Files

8. **.kiro/steering/api-standards.md**
   - REST API conventions
   - HTTP methods and status codes
   - JSON response formats
   - Error handling standards
   - Validation rules
   - Security best practices

9. **.kiro/steering/aws-credentials.md**
   - AWS credential management
   - When to prompt for credentials
   - Security best practices
   - Credential sources
   - Troubleshooting

10. **.kiro/steering/check-documentation.md** (This file)
    - Documentation locations
    - When to check docs
    - How to use documentation

## When to Check Documentation

### Before Starting Work

Always check documentation when:

1. **Implementing New Features**
   - Review API standards for consistency
   - Check existing patterns in example code
   - Verify naming conventions
   - Understand current architecture

2. **Modifying Existing Code**
   - Read relevant documentation sections
   - Understand current implementation
   - Check for dependencies
   - Review related test cases

3. **Answering Questions**
   - Check README for project overview
   - Review specific documentation sections
   - Look at example code
   - Verify current behavior

4. **Deploying or Testing**
   - Review DEPLOYMENT.md for procedures
   - Check infrastructure README
   - Verify credential requirements
   - Follow testing guidelines

5. **Troubleshooting Issues**
   - Check troubleshooting sections
   - Review error handling documentation
   - Look at test results
   - Verify configuration

### During Development

Check documentation when:

1. **Unsure About Standards**
   - API conventions → api-standards.md
   - AWS operations → aws-credentials.md
   - Response formats → api-standards.md

2. **Need Examples**
   - API usage → backend/example_requests.py
   - Deployment → DEPLOYMENT.md
   - Testing → test_api.sh

3. **Implementing Error Handling**
   - Error response format → api-standards.md
   - Status codes → api-standards.md
   - Validation → api-standards.md

4. **Working with AWS**
   - Credentials → aws-credentials.md
   - Infrastructure → infrastructure/README.md
   - Deployment → DEPLOYMENT.md

## How to Use Documentation

### Quick Reference Workflow

1. **Identify the Topic**
   - API design → api-standards.md
   - Deployment → DEPLOYMENT.md
   - Setup → README.md
   - AWS → aws-credentials.md

2. **Read Relevant Sections**
   - Don't skip documentation
   - Read thoroughly before implementing
   - Note any constraints or requirements

3. **Follow Established Patterns**
   - Use existing code as reference
   - Maintain consistency
   - Follow conventions

4. **Update Documentation**
   - If you add features, update docs
   - If you find errors, fix them
   - Keep documentation current

### Documentation Priority

When multiple docs are relevant, check in this order:

1. **Steering files** (.kiro/steering/) - Standards and conventions
2. **README files** - Overview and setup
3. **Generated docs** (backend/docs/) - API reference
4. **Example code** - Working implementations
5. **Test files** - Expected behavior

## Common Documentation Patterns

### For API Questions

```
1. Check api-standards.md for conventions
2. Review backend/README.md for endpoint details
3. Look at backend/docs/main.html for API reference
4. Check backend/example_requests.py for usage examples
5. Verify with test_api.sh for expected behavior
```

### For Deployment Questions

```
1. Check DEPLOYMENT.md for step-by-step guide
2. Review infrastructure/README.md for architecture
3. Check aws-credentials.md for credential requirements
4. Look at infrastructure/stacks/api_stack.py for implementation
5. Verify with TEST_RESULTS.md for expected outcomes
```

### For Setup Questions

```
1. Check README.md for overview
2. Review backend/README.md for backend setup
3. Check infrastructure/README.md for infrastructure setup
4. Look at requirements.txt files for dependencies
5. Follow DEPLOYMENT.md for complete setup
```

### For Standards Questions

```
1. Check api-standards.md for API conventions
2. Review aws-credentials.md for AWS practices
3. Look at existing code for patterns
4. Check backend/docs/ for implementation details
```

## Documentation Maintenance

### Keep Documentation Updated

When making changes:

1. **Update README files** if behavior changes
2. **Regenerate API docs** if code changes
   ```bash
   cd backend
   pdoc main.py -o docs --no-search
   ```
3. **Update DEPLOYMENT.md** if deployment process changes
4. **Update TEST_RESULTS.md** if test outcomes change
5. **Update steering files** if standards evolve

### Documentation Quality Checklist

- [ ] Is the information accurate?
- [ ] Are examples working and tested?
- [ ] Are instructions clear and complete?
- [ ] Are all features documented?
- [ ] Are error cases covered?
- [ ] Are prerequisites listed?
- [ ] Are commands copy-pasteable?
- [ ] Are links working?

## FastAPI Built-in Documentation

Remember that FastAPI provides automatic interactive documentation:

### Swagger UI
- **URL**: `https://your-api-url/prod/docs`
- **Features**: Interactive API testing, request/response schemas
- **Use for**: Testing endpoints, viewing OpenAPI spec

### ReDoc
- **URL**: `https://your-api-url/prod/redoc`
- **Features**: Clean, readable API documentation
- **Use for**: Reading API documentation, sharing with others

### When to Use Each

- **Swagger UI**: When you need to test API calls interactively
- **ReDoc**: When you need clean, readable documentation
- **backend/docs/**: When you need code-level documentation
- **README files**: When you need setup and usage guides
- **Steering files**: When you need standards and conventions

## Documentation Search Tips

### Finding Information Quickly

1. **Use file search** for specific terms
   ```bash
   grep -r "search-term" *.md
   ```

2. **Check table of contents** in longer docs

3. **Use browser search** (Ctrl+F / Cmd+F) in HTML docs

4. **Look at file names** for topic hints
   - api-standards.md → API conventions
   - aws-credentials.md → AWS credential management
   - DEPLOYMENT.md → Deployment procedures

### Common Search Terms

- "status code" → api-standards.md
- "credentials" → aws-credentials.md
- "deploy" → DEPLOYMENT.md, infrastructure/README.md
- "setup" → README.md, backend/README.md
- "test" → TEST_RESULTS.md, test_api.sh
- "error" → api-standards.md (error handling)
- "endpoint" → backend/README.md, api-standards.md

## Documentation Anti-Patterns

### DON'T:

1. **Skip documentation** and guess implementation details
2. **Assume behavior** without checking docs
3. **Ignore standards** defined in steering files
4. **Forget to update docs** when changing code
5. **Create inconsistent patterns** without checking existing code
6. **Reinvent solutions** that are already documented

### DO:

1. **Read documentation first** before implementing
2. **Follow established patterns** from docs and examples
3. **Update documentation** when making changes
4. **Ask for clarification** if docs are unclear
5. **Reference documentation** when explaining decisions
6. **Keep documentation current** and accurate

## Quick Reference Card

| Need | Check |
|------|-------|
| API conventions | .kiro/steering/api-standards.md |
| AWS credentials | .kiro/steering/aws-credentials.md |
| Project overview | README.md |
| Deployment steps | DEPLOYMENT.md |
| Test results | TEST_RESULTS.md |
| Backend setup | backend/README.md |
| API reference | backend/docs/main.html |
| Code examples | backend/example_requests.py |
| Infrastructure | infrastructure/README.md |
| CDK code | infrastructure/stacks/api_stack.py |

## Remember

> **Documentation is not optional. It's the source of truth for the project.**

Before implementing, modifying, or answering questions:
1. ✅ Check relevant documentation
2. ✅ Follow established patterns
3. ✅ Maintain consistency
4. ✅ Update docs when needed

This ensures:
- Consistent implementation
- Fewer errors and rework
- Better maintainability
- Easier onboarding
- Reliable information
