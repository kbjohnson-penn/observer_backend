# Observer Backend

Django 5.0.1 REST API backend for healthcare encounter data management.

## Features

- **RESTful API**: Patient, provider, and encounter data management
- **JWT Authentication**: Secure token-based authentication
- **Multimodal Data**: Support for various healthcare encounter types
- **Azure Storage**: File management and storage integration
- **Admin Interface**: Comprehensive Django admin for data management
- **Mock Data**: Automated test data generation

**Note**: This is a Git submodule. For Docker setup, see the main repository README.

## Development Setup

**Prerequisites**: This submodule is designed to run via Docker from the main repository.

### Local Development (without Docker)

If you need to run locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up MariaDB database
# Configure environment variables (see main repo /env/ files)

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Mock Data Generation

```bash
# Generate test data
python manage.py generate_mock_data

# Custom generation
python manage.py generate_mock_data --clinic-patients 100 --seed 42
```

## API Features

The project provides the following API endpoints:

### Public API (v1)

- `/api/v1/public/patients/` - Patient data
- `/api/v1/public/providers/` - Provider data
- `/api/v1/public/encounters/` - Patient encounter data
- `/api/v1/public/departments/` - Department information
- `/api/v1/public/encountersources/` - Encounter sources
- `/api/v1/public/mmdata/` - Multimodal data

### Private API (v1)

- `/api/v1/private/patients/` - Patient data management
- `/api/v1/private/providers/` - Provider data management
- `/api/v1/private/encounters/` - Encounter data management
- `/api/v1/private/departments/` - Department management
- `/api/v1/private/encountersources/` - Encounter sources management
- `/api/v1/private/mmdata/` - Multimodal data management
- `/api/v1/private/encounterfiles/` - Encounter files management

### Authentication API (v1)

- `POST /api/v1/auth/token/` - Login (get authentication token)
- `POST /api/v1/auth/token/refresh/` - Refresh authentication token
- `POST /api/v1/auth/token/verify/` - Verify authentication token
- `POST /api/v1/auth/logout/` - User logout

### Profile API (v1)

- `GET/PUT /api/v1/profile/` - User profile operations

### API Features

- **Browsable API**: Visit <http://localhost:8000/api> for interactive documentation
- **Authentication**: JWT tokens with login/logout/refresh endpoints
- **Data Models**: Patients, Providers, Encounters, Departments, and Multimodal Data
- **File Management**: Azure Storage integration for encounter files
- **Encounter Types**: Support for Penn Personalized Care (PPC) and SimCenter data

## Project Structure

```
dashboard/
├── api/                    # API views, serializers, URLs
│   ├── serializers/       # Data serializers
│   ├── views/            # API views and viewsets
│   └── urls/             # URL configurations
├── models/               # Data models
├── management/commands/  # Django management commands
├── migrations/          # Database migrations
└── tests/               # Test files
```

## Key Models

- **Patient**: Patient demographic and clinical data
- **Provider**: Healthcare provider information
- **Encounter**: Patient-provider interactions
- **Department**: Healthcare departments
- **EncounterSource**: Source systems (PPC, SimCenter)
- **EncounterFile**: File attachments for encounters
- **MultimodalData**: Additional encounter data and flags

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Changelog

Check [CHANGELOG.md](CHANGELOG.md) to get the version details.

# Updated Database setup

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
  

2. Delete all migration files:

# Delete all migration files except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

3. Create fresh migrations:

/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py makemigrations accounts
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py makemigrations clinical
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py makemigrations research

4. Apply migrations to correct databases:

# First, migrate Django's built-in apps
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py migrate

# Then migrate each app to its specific database
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py migrate --database=accounts
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py migrate --database=clinical
/Users/mopidevi/miniconda3/envs/observer/bin/python manage.py migrate --database=research

5. Verify everything worked:

# Check all tables were created
mysql -u observer -pobserver_password -e "USE observer_accounts; SHOW TABLES;"
mysql -u observer -pobserver_password -e "USE observer_clinical; SHOW TABLES;"
mysql -u observer -pobserver_password -e "USE observer_research; SHOW TABLES;"