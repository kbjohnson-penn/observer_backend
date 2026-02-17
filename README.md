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

**Note**: This is a Git submodule. For container deployment, see the main repository README.

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

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
make pre-commit

# Set up MariaDB databases (from main project directory)
./helpers/clean_db.sh

# Run migrations
make migrate

# Create admin user
python manage.py createsuperuser

# Run server
make run
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit` and prevent commits if checks fail.

**Installed hooks:**
1. Trailing whitespace removal
2. End-of-file fixer
3. YAML/JSON validation
4. Large file check
5. Black formatting
6. isort import sorting
7. Flake8 linting
8. Django system checks

```bash
# Run hooks on all files manually
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

## Development Workflow

1. **Before starting work:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **While developing:**
   ```bash
   make run        # Run server
   make test-fast  # Run tests as you code
   ```

3. **Before committing:**
   ```bash
   make format     # Format and lint
   make lint-quick
   make test       # Full test suite
   git add .
   git commit -m "feat: add new feature"
   ```

4. **Before pushing:**
   ```bash
   make check
   make test
   git push origin feature/your-feature-name
   ```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make install` | Install production dependencies |
| `make install-dev` | Install development dependencies |
| `make format` | Format code with Black and isort |
| `make lint` | Run all linters (flake8 + pylint) |
| `make lint-quick` | Run flake8 only (faster) |
| `make test` | Run tests with coverage |
| `make test-fast` | Run tests without coverage |
| `make migrate` | Run migrations for all databases |
| `make migrate-make` | Create new migrations |
| `make clean` | Clean cache and build files |
| `make run` | Run development server |
| `make shell` | Open Django shell |
| `make check` | Run Django system checks |
| `make pre-commit` | Install pre-commit hooks |
| `make coverage` | Generate and open HTML coverage report |

## Code Quality Tools

### Black (Code Formatter)

```bash
make format          # Format all code
black --check .      # Check without changes
```

**Configuration**: `pyproject.toml` → `[tool.black]` (line length: 100, Python 3.10)

### isort (Import Sorter)

```bash
make format          # Sort imports
isort --check-only . # Check without changes
```

**Configuration**: `pyproject.toml` → `[tool.isort]` (profile: black)

### Flake8 (Linter)

```bash
make lint-quick      # Run linting
```

**Configuration**: `.flake8` (max line length: 100, max complexity: 10)

### Pylint (Deep Analysis)

```bash
make lint            # Run pylint (optional, for local use)
```

**Configuration**: `.pylintrc` (Django plugin enabled)

## Testing

### Running Tests

```bash
make test                    # With coverage
make test-fast               # Without coverage (faster)
make test-verbose            # Verbose output

# Run specific tests
pytest accounts/tests/test_models.py
pytest accounts/tests/test_models.py::TestUserModel::test_create_user
```

**Configuration**: `pyproject.toml` → `[tool.pytest.ini_options]`

## Mock Data Generation

```bash
python manage.py generate_mock_data
python manage.py generate_mock_data --clinic-patients 100 --seed 42
```

## CI/CD Pipeline

The CI pipeline runs on every push and pull request to `main` or `dev` branches.

**Pipeline steps:**
1. Checkout code
2. Setup Python 3.10
3. Install dependencies
4. Run Black format check
5. Run isort import check
6. Run Flake8 linting
7. Run Django system checks
8. Check for pending migrations
9. Run tests with coverage
10. Upload coverage to Codecov

### Local CI Simulation

```bash
make format
make lint-quick
make check
python manage.py makemigrations --check --dry-run
make test
```

## API Features

- **Browsable API**: Visit <http://localhost:8000/api> for interactive documentation
- **Secure Authentication**: JWT tokens with httpOnly cookies and CSRF protection
- **Rate Limiting**: Authentication endpoints protected against brute force attacks
- **Security Headers**: HSTS, XSS protection, clickjacking prevention, and more
- **Data Models**: Patients, Providers, Encounters, Departments, and Multimodal Data
- **File Management**: Azure Storage integration for encounter files
- **Encounter Types**: Support for Penn Personalized Care (PPC) and SimCenter data

## Project Structure

```text
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
python manage.py makemigrations accounts
python manage.py makemigrations clinical
python manage.py makemigrations research

python manage.py migrate --database=accounts
python manage.py migrate --database=clinical
python manage.py migrate --database=research
```

### 3. Verify Database Setup

```bash
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

## Troubleshooting

### Pre-commit Hook Failures

1. **Formatting issues**: Run `make format` to auto-fix
2. **Linting issues**: Review flake8 errors and fix manually
3. **Django check failures**: Fix Django configuration issues

### Import Errors After Installing New Package

```bash
pip freeze > requirements.txt
pip freeze > requirements-dev.txt
```

### Coverage Not Updating

```bash
make clean
make test
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

All pull requests must pass CI checks before merging.

## Changelog

Check [CHANGELOG.md](CHANGELOG.md) to get the version details.
