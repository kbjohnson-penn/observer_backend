# Accounts App Tests

## Test Summary

- **Total Tests**: 63
- **Test Modules**: 9 organized modules (refactored from monolithic tests.py)
- **Coverage**: Models, APIs, Authentication, Permissions, httpOnly Cookies

## Test Structure

The test suite has been refactored into logical modules:

```
accounts/tests/
├── __init__.py
├── base.py                  # Base test class with common setup
├── test_authentication.py   # Authentication & httpOnly cookie tests
├── test_models.py          # Model tests (Tier, Organization, Profile)
├── test_permissions.py     # Permission and tier-based access tests
├── test_profile.py         # Profile API tests
├── test_registration.py    # User registration & email verification
├── test_serializers.py     # Serializer validation tests
├── test_signals.py         # Django signal tests
└── test_utils.py           # Utility function tests
```

## What We Test

### 🔐 httpOnly Cookie Authentication (NEW - 3 tests)

- **Cookie Setting**: Login sets httpOnly cookies with security flags
- **Cookie Clearing**: Logout properly clears httpOnly cookies
- **Token Refresh**: Automatic refresh using httpOnly cookies
- **Security Properties**: httpOnly=True, SameSite=Lax, Secure (production)

### Models (22 tests)

- **Tier Model**: String representation, ordering, unique constraints, boolean fields
- **Organization Model**: String representation, fields, website, full address
- **Profile Model**: User relationship, organization/tier relationships
- **EmailVerificationToken**: Token generation, expiration, validation

### Authentication (16 tests)

- **User Login**: httpOnly cookie-based authentication
- **Token Refresh**: Cookie-based token refresh
- **Token Verification**: Access token validation
- **Logout**: Cookie clearing with/without refresh token
- **Email Login**: Login with email instead of username

### Registration & Verification (11 tests)

- **User Registration**: Create inactive user, generate verification token
- **Email Verification**: Token validation, password setup, expiration handling
- **Organization Creation**: Auto-create organization during registration
- **Duplicate Prevention**: Email/username uniqueness

### Profile Management (5 tests)

- **Get Profile**: Authenticated access only
- **Update Profile**: Partial updates with address parsing
- **Serialization**: Proper data formatting and relationships

### Permissions (3 tests)

- **Tier Levels**: Verify 5-tier hierarchy (1=lowest, 5=highest)
- **Superuser Creation**: Admin capabilities

### Signals (2 tests)

- **Auto Profile Creation**: Profile created on user creation
- **Profile Save**: Cascading updates

### Utilities (4 tests)

- **Address Parsing**: Split/combine addresses ("123 Main St, Apt 4")
- **None Handling**: Graceful handling of empty values

## Running Tests

```bash
# All accounts tests
python manage.py test accounts

# Specific test module
python manage.py test accounts.tests.test_authentication
python manage.py test accounts.tests.test_registration

# Specific test class
python manage.py test accounts.tests.test_authentication.CookieAuthenticationTest

# Specific test method
python manage.py test accounts.tests.test_authentication.CookieAuthenticationTest.test_login_sets_httponly_cookies

# With verbosity
python manage.py test accounts -v 2
```

## API Test Coverage

### Authentication Endpoints
- `POST /api/v1/auth/token/` ✅ (Login with httpOnly cookies)
- `POST /api/v1/auth/token/refresh/` ✅ (Refresh using cookies)
- `POST /api/v1/auth/token/verify/` ✅ (Verify access token)
- `POST /api/v1/auth/logout/` ✅ (Clear httpOnly cookies)
- `POST /api/v1/auth/register/` ✅ (User registration)
- `POST /api/v1/auth/verify-email/` ✅ (Email verification)

### Profile Endpoints
- `GET /api/v1/profile/` ✅ (Get authenticated user profile)
- `PATCH /api/v1/profile/` ✅ (Update profile)

**Coverage: 8/8 endpoints (100%)**

## Security Features Tested

### httpOnly Cookie Security
- **XSS Protection**: Cookies not accessible via JavaScript
- **CSRF Protection**: SameSite=Lax attribute
- **HTTPS Only**: Secure flag in production
- **Proper Expiration**: Cookies cleared on logout

### Authentication Flow
```
1. Login → Sets httpOnly cookies (access_token, refresh_token)
2. API Calls → Cookies sent automatically with credentials: 'include'
3. Token Refresh → Uses refresh_token cookie, sets new access_token
4. Logout → Clears both cookies
```

## Test Database Configuration

- **Multi-database**: Uses `accounts` and `default` databases
- **Auto-cleanup**: Test databases created/destroyed automatically
- **Signal Handling**: Proper signal handling for profile creation

## Common Test Commands

```bash
# Run with coverage
pip install coverage
coverage run --source='.' manage.py test accounts
coverage report
coverage html  # Generate HTML report

# Run in parallel (faster)
python manage.py test accounts --parallel

# Keep test database (for debugging)
python manage.py test accounts --keepdb

# Run specific test pattern
python manage.py test accounts -k "cookie"  # Run all cookie-related tests
```

## Test Utilities

### BaseTestCase
Provides common setup including:
- Test users with different tier levels
- Organizations and tiers (1-5)
- API client with authentication helpers

### Authentication Helper
```python
def authenticate_user(self, user=None):
    """Authenticate a user and return tokens."""
    # Sets up JWT authentication for testing
```

## Troubleshooting

### Rate Limiting
Some tests may skip due to rate limiting. This is normal and tests handle it gracefully.

### Multi-Database Issues
Ensure `TEST` settings are configured for both databases in settings.py:
```python
DATABASES = {
    'default': {...},
    'accounts': {
        ...,
        'TEST': {
            'NAME': 'test_observer_accounts',
        }
    }
}
```

## Recent Changes

### httpOnly Cookie Implementation (July 2024)
- Migrated from localStorage to httpOnly cookies
- Added comprehensive cookie security tests
- Updated all authentication tests for cookie-based flow
- Maintained backward compatibility with Authorization headers

### Test Refactoring (July 2024)
- Split 1,102-line tests.py into 9 logical modules
- Improved test organization and maintainability
- Added dedicated httpOnly cookie test suite
- Enhanced test documentation