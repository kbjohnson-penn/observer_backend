# Shared App Tests

## Test Summary

- **Total Tests**: 92
- **Coverage**: Utilities, Validators, Permissions, Infrastructure, Error Handlers
- **Organization**: 5 specialized test files for better maintainability

## What We Test

### Utilities (16 tests)
- **Age Calculation (6 tests)**: Birth date validation, birthday edge cases, future dates, None handling
- **Address Utils (10 tests)**: Address splitting/combining, whitespace handling, max length constraints, roundtrip consistency

### Validators (15 tests) 
- **Phone Numbers (3 tests)**: Valid formats, invalid patterns, empty value handling
- **Numeric Fields (3 tests)**: Number validation, invalid characters, empty values
- **Time/Date (2 tests)**: Datetime objects, string parsing, range validation
- **Generic Fields (2 tests)**: Text validation, length constraints
- **Address Fields (5 tests)**: Format validation, character restrictions, length limits

### Permissions (21 tests)
- **Tier Permissions (6 tests)**: Multi-tier access control, superuser privileges, profile requirements
- **ViewSet Authentication (3 tests)**: Tier-based access methods, user validation
- **Object Permissions (3 tests)**: Encounter access control, unsupported object handling
- **Public Permissions (1 test)**: Read-only API access validation
- **Edge Cases (8 tests)**: Users without profiles, cross-database permission checks

### Infrastructure (25 tests)
- **Database Router (8 tests)**: Read/write routing, cross-database relations, migration control
- **Choices & Constants (8 tests)**: Sex categories, file types, boolean choices, ID range validation
- **Location Data (5 tests)**: Country/state choices, format validation, data consistency
- **Configuration (4 tests)**: SimCenter ID ranges, choice dictionary mappings

### Error Handlers (15 tests)
- **Custom Exceptions (4 tests)**: ObserverAPIException hierarchy, status codes, error details
- **Handler Functions (8 tests)**: 404/403/400/500 responses, logging integration, field errors
- **Safe Object Retrieval (2 tests)**: get_or_404 behavior, custom error messages
- **ViewSet Integration (1 test)**: Exception handling mixin, automatic error responses

## Running Tests

```bash
# All shared tests
python manage.py test shared.tests -v 2

# Individual test files
python manage.py test shared.tests.test_utils -v 2
python manage.py test shared.tests.test_validators -v 2  
python manage.py test shared.tests.test_permissions -v 2
python manage.py test shared.tests.test_infrastructure -v 2
python manage.py test shared.tests.test_error_handlers -v 2

# Specific test classes
python manage.py test shared.tests.test_permissions.TierPermissionsTest -v 2
python manage.py test shared.tests.test_utils.AddressUtilsTest -v 2
```

## Key Features Tested

### Multi-Database Architecture
- **Database Routing**: Proper routing to accounts/clinical/research databases
- **Cross-Database Relations**: Controlled relationship validation between databases
- **Migration Control**: Prevents apps from migrating to wrong databases

### Tier-Based Security
- **Access Control**: Users can only access data at or below their tier level
- **Superuser Privileges**: Superusers bypass tier restrictions
- **Profile Integration**: Automatic profile creation via Django signals
- **Permission Classes**: `HasAccessToEncounter`, `BaseAuthenticatedViewSet` validation

### Data Validation & Utilities
- **Phone Number Parsing**: International formats, special characters, length validation
- **Address Processing**: Smart splitting/combining, whitespace preservation
- **Field Validation**: Generic validators for text, numeric, time, and address fields
- **Age Calculation**: Precise age computation with edge case handling

### Error Handling System
- **Standardized Responses**: Consistent error format across all APIs
- **Logging Integration**: Structured logging for debugging and monitoring  
- **Exception Hierarchy**: Custom exception classes with appropriate HTTP status codes
- **ViewSet Integration**: Automatic exception handling in API endpoints

## Database Setup

- Uses `default`, `accounts`, and `clinical` databases
- Proper database routing with explicit `_using` parameters
- User model integration: Custom accounts.User with profile relationships
- Signal handling: Automatic profile creation with tier assignment

## Critical Shared Logic

### Permission System
1. **Tier Filtering**: `filter_queryset_by_user_tier()` applies access control
2. **Field Mapping**: Supports both ForeignKey (`tier`) and IntegerField (`tier_id`) relationships
3. **Superuser Bypass**: Administrators see all data regardless of tier
4. **Profile Validation**: Users without profiles have no data access

### Address Processing
- **Smart Splitting**: Separates addresses at comma boundaries
- **Length Limits**: Enforces 100-character limits per address line
- **Whitespace Handling**: Preserves intentional spacing in address fields
- **Roundtrip Consistency**: split_address() + combine_address() = original

### Validation Pipeline  
- **Consistent Empty Handling**: None, empty string, and whitespace-only values treated uniformly
- **Field-Specific Rules**: Tailored validation for phone, address, numeric, and time fields
- **Error Messaging**: Clear, actionable validation error messages

## Test Organization

```
shared/tests/
├── __init__.py
├── test_utils.py          # Age calculation & address utilities
├── test_validators.py     # Field validation functions
├── test_permissions.py    # Tier-based access control
├── test_infrastructure.py # Database routing & choices
└── test_error_handlers.py # API error handling system
```

## Next Steps

The shared app testing is complete. Remaining work:
- Clinical app API endpoint tests (stream/download functionality)
- Research app testing implementation
- Integration testing across app boundaries