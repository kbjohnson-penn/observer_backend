# Observer Backend

Django 5.0.1 REST API backend for healthcare encounter data management.

## Features

- **RESTful API**: Patient, provider, and encounter data management
- **Secure Authentication**: JWT tokens with httpOnly cookie support and CSRF protection
- **Multi-Database Architecture**: Separate databases for accounts, clinical, and research data
- **Environment-Based Configuration**: Separate settings for development, testing, and production
- **Security Headers**: Comprehensive security middleware with HSTS, XSS protection, and more
- **Multimodal Data**: Support for various healthcare encounter types
- **Azure Storage**: File management and storage integration
- **Admin Interface**: Comprehensive Django admin for data management
- **Mock Data**: Automated test data generation

**Note**: This is a Git submodule. For Docker deployment, see the main repository README.

## Development Setup

### Environment Configuration

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Update environment variables** in `.env`:
   - Set `ENVIRONMENT=development` for local development
   - Configure database credentials
   - Update `SECRET_KEY` for production

### Local Development

For local development without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up MariaDB databases
./helpers/clean_db.sh  # From main project directory

# Run migrations
python manage.py migrate --database=accounts
python manage.py migrate --database=clinical
python manage.py migrate --database=research

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Environment-Specific Settings

The application supports three environments:

- **Development** (`ENVIRONMENT=development`): Relaxed security, console email, debug mode

### Mock Data Generation

```bash
# Generate test data
python manage.py generate_mock_data

# Custom generation
python manage.py generate_mock_data --clinic-patients 100 --seed 42
```

### API Features

- **Browsable API**: Visit <http://localhost:8000/api> for interactive documentation
- **Secure Authentication**: JWT tokens with httpOnly cookies and CSRF protection
- **Rate Limiting**: Authentication endpoints protected against brute force attacks
- **Security Headers**: HSTS, XSS protection, clickjacking prevention, and more
- **Data Models**: Patients, Providers, Encounters, Departments, and Multimodal Data
- **File Management**: Azure Storage integration for encounter files
- **Encounter Types**: Support for Penn Personalized Care (PPC) and SimCenter data

## Project Structure

```
backend/
├── settings/              # Environment-specific settings
│   ├── base.py           # Common settings
│   ├── development.py    # Development settings
│   ├── testing.py        # Test settings
│   └── production.py     # Production settings
├── urls.py               # Main URL configuration
└── wsgi.py              # WSGI application

accounts/                 # User authentication & profiles
├── api/                  # Authentication API endpoints
├── models/              # User models
└── tests/               # Authentication tests

clinical/                 # Clinical data management
├── api/                  # Clinical API endpoints
├── models/              # Patient, Provider, Encounter models
└── tests/               # Clinical data tests

research/                 # Research data management
├── api/                  # Research API endpoints
├── models/              # Research models
└── tests/               # Research tests

shared/                   # Shared utilities
├── authentication.py    # Custom JWT authentication
├── db_router.py         # Database routing
└── api/                 # Shared API components
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Changelog

Check [CHANGELOG.md](CHANGELOG.md) to get the version details.

## Database Setup

The Observer backend uses a multi-database architecture with separate databases for different data types:

### 1. Create MariaDB Databases

```sql
mysql -u root -p

DROP DATABASE IF EXISTS observer_accounts;
DROP DATABASE IF EXISTS observer_clinical; 
DROP DATABASE IF EXISTS observer_research;

CREATE DATABASE observer_accounts;
CREATE DATABASE observer_clinical;
CREATE DATABASE observer_research;

GRANT ALL PRIVILEGES ON observer_accounts.* TO 'observer'@'localhost';
GRANT ALL PRIVILEGES ON observer_accounts.* TO 'observer'@'%';
GRANT ALL PRIVILEGES ON observer_clinical.* TO 'observer'@'localhost';
GRANT ALL PRIVILEGES ON observer_clinical.* TO 'observer'@'%';
GRANT ALL PRIVILEGES ON observer_research.* TO 'observer'@'localhost';
GRANT ALL PRIVILEGES ON observer_research.* TO 'observer'@'%';

FLUSH PRIVILEGES;
```

### 2. Run Database Migrations

```bash
# Create migrations for each app
python manage.py makemigrations accounts
python manage.py makemigrations clinical
python manage.py makemigrations research

# Apply migrations to default database (Django built-ins)
python manage.py migrate

# Apply migrations to specific databases
python manage.py migrate --database=accounts
python manage.py migrate --database=clinical
python manage.py migrate --database=research
```

### 3. Verify Database Setup

```bash
# Check tables were created in each database
mysql -u observer -pobserver_password -e "USE observer_accounts; SHOW TABLES;"
mysql -u observer -pobserver_password -e "USE observer_clinical; SHOW TABLES;"
mysql -u observer -pobserver_password -e "USE observer_research; SHOW TABLES;"
```

## Security Features

- **httpOnly Cookies**: JWT tokens stored securely in httpOnly cookies
- **CSRF Protection**: CSRF tokens required for state-changing operations
- **Rate Limiting**: Authentication endpoints protected against brute force attacks
- **Security Headers**: HSTS, XSS protection, clickjacking prevention
- **Environment-based Security**: Different security levels for development vs production
- **Multi-Database Isolation**: Separate databases for different data types