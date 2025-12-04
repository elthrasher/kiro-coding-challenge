# Implementation Plan: User Registration and Event Management

- [x] 1. Set up database tables and infrastructure
  - Create UsersTable in DynamoDB with userId as partition key
  - Create RegistrationsTable with composite key (userId, eventId)
  - Add GSI eventId-userId-index to RegistrationsTable for reverse lookups
  - Extend EventsTable schema with registeredCount, waitlistEnabled, and waitlist fields
  - Update CDK stack to provision new tables with appropriate permissions
  - _Requirements: 1.1, 2.1, 3.1, 7.1_

- [ ] 2. Implement user management
- [x] 2.1 Create user data models and validation
  - Define UserCreate and User Pydantic models with validation rules
  - Implement validation for userId (alphanumeric, hyphens, underscores only)
  - Implement validation for name (non-empty, not all whitespace)
  - _Requirements: 1.1, 1.3, 1.4_

- [ ]* 2.2 Write property test for user creation round-trip
  - **Property 1: User creation round-trip**
  - **Validates: Requirements 1.1**

- [ ]* 2.3 Write property test for duplicate userId rejection
  - **Property 2: Duplicate userId rejection**
  - **Validates: Requirements 1.2**

- [ ]* 2.4 Write property test for whitespace validation
  - **Property 3: Whitespace name rejection**
  - **Property 4: Whitespace userId rejection**
  - **Validates: Requirements 1.3, 1.4**

- [x] 2.5 Implement POST /users endpoint
  - Create user in UsersTable with timestamps
  - Use conditional write to prevent duplicate userIds
  - Return 201 Created with user object
  - Handle errors: 400 (validation), 409 (duplicate)
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.6 Implement GET /users/{userId} endpoint
  - Retrieve user from UsersTable
  - Return 200 OK with user object
  - Handle errors: 404 (not found)
  - _Requirements: 1.1_

- [ ] 3. Extend event management for registrations
- [x] 3.1 Update event data models
  - Add registeredCount, waitlistEnabled, and waitlist fields to Event model
  - Add computed fields: availableSpots, waitlistCount
  - Update EventCreate to accept waitlistEnabled parameter
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 3.2 Update POST /events endpoint
  - Initialize registeredCount to 0
  - Initialize waitlist to empty array
  - Set waitlistEnabled from request (default false)
  - Validate capacity > 0
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ]* 3.3 Write property test for capacity enforcement
  - **Property 5: Capacity enforcement**
  - **Validates: Requirements 2.1**

- [ ] 4. Implement registration management core logic
- [x] 4.1 Create registration data models
  - Define RegistrationCreate and Registration Pydantic models
  - Define RegistrationList model for query responses
  - Add status field with "confirmed" and "waitlist" values
  - Include denormalized event data (title, date) for convenience
  - _Requirements: 3.1, 4.1, 6.3, 6.4_

- [x] 4.2 Implement registration validation helper
  - Check user exists in UsersTable
  - Check event exists in EventsTable
  - Check user not already registered (query RegistrationsTable)
  - Check user not already on waitlist (check event.waitlist array)
  - Return validation result with appropriate error codes
  - _Requirements: 3.2, 3.4, 3.5, 4.3_

- [x] 4.3 Implement capacity check and reservation logic
  - Query event to get current registeredCount and capacity
  - Determine if spot available, waitlist needed, or rejection required
  - Use conditional expressions for atomic capacity updates
  - Return reservation status: confirmed, waitlist, or rejected
  - _Requirements: 2.1, 2.2, 2.3, 3.1_

- [ ]* 4.4 Write property test for registration capacity invariant
  - **Property 8: Registration capacity invariant**
  - **Validates: Requirements 3.1**

- [ ]* 4.5 Write property test for duplicate registration rejection
  - **Property 9: Duplicate registration rejection**
  - **Validates: Requirements 3.2**

- [ ] 5. Implement POST /users/{userId}/registrations endpoint
- [x] 5.1 Implement confirmed registration flow
  - Validate user and event exist
  - Check capacity available
  - Create registration record with status "confirmed"
  - Atomically increment event registeredCount
  - Use DynamoDB transaction for consistency
  - Return 201 Created with registration object
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 5.2 Write property test for registration persistence
  - **Property 10: Registration persistence round-trip**
  - **Validates: Requirements 3.3**

- [ ]* 5.3 Write property test for non-existent entity rejection
  - **Property 11: Non-existent event rejection**
  - **Property 12: Non-existent user rejection**
  - **Validates: Requirements 3.4, 3.5**

- [x] 5.4 Implement waitlist registration flow
  - Check if event at capacity and has waitlist enabled
  - Add userId to event waitlist array
  - Create registration record with status "waitlist"
  - Return 201 Created with registration object indicating waitlist status
  - Handle case where waitlist disabled: return 409 Conflict
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 5.5 Write property test for waitlist behavior
  - **Property 6: Waitlist acceptance when full**
  - **Property 7: Rejection when full without waitlist**
  - **Property 13: Waitlist addition when full**
  - **Property 14: Full event rejection without waitlist**
  - **Property 15: Duplicate waitlist rejection**
  - **Validates: Requirements 2.2, 2.3, 4.1, 4.2, 4.3**

- [ ]* 5.6 Write property test for waitlist ordering
  - **Property 16: Waitlist FIFO ordering**
  - **Validates: Requirements 4.4**

- [ ] 6. Implement unregistration and waitlist promotion
- [x] 6.1 Implement basic unregistration logic
  - Validate registration exists
  - Delete registration record from RegistrationsTable
  - Atomically decrement event registeredCount
  - Return 204 No Content
  - Handle errors: 404 (registration not found)
  - _Requirements: 5.1, 5.3, 5.4_

- [ ]* 6.2 Write property test for unregistration capacity invariant
  - **Property 17: Unregistration capacity invariant**
  - **Validates: Requirements 5.1**

- [ ]* 6.3 Write property test for invalid unregistration rejection
  - **Property 19: Invalid unregistration rejection**
  - **Validates: Requirements 5.3**

- [ ]* 6.4 Write property test for unregistration persistence
  - **Property 20: Unregistration persistence round-trip**
  - **Validates: Requirements 5.4**

- [x] 6.4 Implement automatic waitlist promotion
  - Check if event has non-empty waitlist after unregistration
  - Remove first user from waitlist array (FIFO)
  - Update their registration status from "waitlist" to "confirmed"
  - Use DynamoDB transaction for atomicity
  - Log promotion for monitoring
  - _Requirements: 5.2, 7.2_

- [ ]* 6.5 Write property test for waitlist promotion
  - **Property 18: Automatic waitlist promotion**
  - **Property 26: Atomic waitlist promotion**
  - **Validates: Requirements 5.2, 7.2**

- [x] 6.6 Implement waitlist unregistration
  - Check if registration status is "waitlist"
  - Remove userId from event waitlist array
  - Delete registration record
  - Maintain order of remaining waitlist users
  - Return 204 No Content
  - _Requirements: 5.5_

- [ ]* 6.7 Write property test for waitlist removal
  - **Property 21: Waitlist removal preserves order**
  - **Validates: Requirements 5.5**

- [x] 6.8 Implement DELETE /users/{userId}/registrations/{eventId} endpoint
  - Determine if registration is confirmed or waitlist
  - Call appropriate unregistration logic
  - Handle waitlist promotion if applicable
  - Return 204 No Content on success
  - Handle errors: 404 (registration not found)
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Implement registration queries
- [ ] 7.1 Implement GET /users/{userId}/registrations endpoint
  - Query RegistrationsTable by userId
  - Include both confirmed and waitlist registrations
  - Return registration list with status indicators
  - Handle empty results (return empty array)
  - Handle errors: 404 (user not found)
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 7.2 Write property test for registration queries
  - **Property 22: Complete registration list**
  - **Property 23: Registration status inclusion**
  - **Property 24: Registration status accuracy**
  - **Validates: Requirements 6.1, 6.3, 6.4**

- [ ] 8. Implement system invariants and consistency checks
- [ ] 8.1 Add capacity conservation validation
  - Create helper function to verify registeredCount + availableSpots = capacity
  - Call after every registration/unregistration operation
  - Log violations for monitoring
  - Add as assertion in development/test environments
  - _Requirements: 7.1_

- [ ]* 8.2 Write property test for capacity conservation
  - **Property 25: Capacity conservation invariant**
  - **Validates: Requirements 7.1**

- [ ] 9. Add error handling and logging
- [ ] 9.1 Implement structured error responses
  - Create error response helper following API standards format
  - Include error code, message, details, timestamp, path, requestId
  - Define all error codes: USER_NOT_FOUND, DUPLICATE_USER, EVENT_FULL, etc.
  - Ensure consistent error format across all endpoints
  - _Requirements: All_

- [ ] 9.2 Add comprehensive logging
  - Log all registration operations with user and event context
  - Log waitlist promotions with before/after state
  - Log validation failures with details
  - Log performance metrics (operation duration)
  - Use structured logging format for easy parsing
  - _Requirements: All_

- [ ] 10. Update API documentation
- [ ] 10.1 Update FastAPI endpoint documentation
  - Add docstrings to all new endpoints
  - Document request/response schemas
  - Document all possible status codes and error conditions
  - Add usage examples for each endpoint
  - _Requirements: All_

- [ ] 10.2 Regenerate API documentation
  - Run pdoc to generate updated HTML documentation
  - Verify all new endpoints appear in docs
  - Test interactive Swagger UI documentation
  - _Requirements: All_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
