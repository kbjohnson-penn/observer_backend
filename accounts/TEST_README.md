# Accounts App Tests

## Test Summary

- **Total Tests**: 40
- **Coverage**: Models, APIs, Authentication, Permissions

## What We Test

### Models (9 tests)

- **Tier**: Creation, string format, uniqueness (5-tier system: 1=lowest, 5=highest)
- **Organization**: Basic creation and display
- **Profile**: User relationships and string representation

### Authentication (8 tests)

- **JWT Logout**: Valid/invalid token handling
- **Token Verification**: Token validation and lifecycle
- **Profile API**: Get/update profile with authentication

### Permissions (2 tests)

- **Tier Access**: Verify tier hierarchy
- **Superuser**: Creation and elevated permissions

### Serializers (8 tests)

- **User Registration**: Data validation, password/email/username checks
- **Profile Serialization**: API response formatting

### Signals (2 tests)

- **Auto Profile Creation**: Profile created when user is created
- **Profile Updates**: Signal-driven updates

### Utilities (3 tests)

- **Address Functions**: Split/combine addresses ("123 Main St, Apt 4")

### Extended Features (8 tests)

- **Organization Fields**: Address, contact validation
- **Auth Flow**: Login, refresh, logout, protected endpoints

## Running Tests

```bash
# All tests
python manage.py test accounts

# Specific test
python manage.py test accounts.tests.TierModelTest
```

## API Test Coverage

### Actual Endpoints vs Tests
**Available APIs:**
- `POST /api/v1/auth/token/` (Login)
- `POST /api/v1/auth/token/refresh/` (Refresh)
- `POST /api/v1/auth/token/verify/` (Verify)
- `POST /api/v1/auth/logout/` (Logout)
- `GET /api/v1/profile/` (Get profile)
- `PATCH /api/v1/profile/` (Update profile)

**Coverage: 6/6 main endpoints (100%)**

### How to Verify APIs Work
```bash
# Run API tests specifically
python manage.py test accounts.tests.LogoutAPITest
python manage.py test accounts.tests.ProfileAPITest
python manage.py test accounts.tests.AuthenticationAPITest

# Check test coverage
pip install coverage
coverage run manage.py test accounts
coverage report
```

## Features Tested

- JWT authentication & token management
- 5-tier access control system
- Multi-database routing (accounts/clinical/research)
- Email/username uniqueness
- Signal-driven profile creation
- Address parsing utilities
- API security & validation

## Database Setup

- Uses `accounts` and `default` databases
- Auto-creates/destroys test databases
- Handles Django signals properly
