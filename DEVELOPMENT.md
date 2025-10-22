# Development Guide

This guide covers the development workflow, tools, and best practices for the Observer Backend project.

## Quick Start

### 1. Install Development Dependencies

```bash
# Install all dependencies including development tools
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Set Up Pre-commit Hooks

Pre-commit hooks automatically format and lint your code before each commit:

```bash
make pre-commit
# OR: pre-commit install
```

### 3. Verify Setup

```bash
# Run all quality checks
make format      # Format code
make lint-quick  # Lint code
make test        # Run tests
```

## Development Workflow

### Day-to-Day Development

1. **Before starting work:**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **While developing:**
   ```bash
   # Run server
   make run

   # Run tests as you code
   make test-fast
   ```

3. **Before committing:**
   ```bash
   # Format and lint
   make format
   make lint-quick

   # Run full test suite
   make test

   # Commit (pre-commit hooks will run automatically)
   git add .
   git commit -m "feat: add new feature"
   ```

4. **Before pushing:**
   ```bash
   # Final checks
   make check
   make test

   # Push
   git push origin feature/your-feature-name
   ```

## Code Quality Tools

### Black (Code Formatter)

Automatically formats Python code to ensure consistency.

```bash
# Format all code
make format
# OR: black .

# Check formatting without making changes
black --check .
```

**Configuration**: `pyproject.toml` → `[tool.black]`
- Line length: 100
- Target Python version: 3.10

### isort (Import Sorter)

Organizes import statements.

```bash
# Sort imports
make format
# OR: isort .

# Check imports without making changes
isort --check-only .
```

**Configuration**: `pyproject.toml` → `[tool.isort]`
- Profile: black (compatible with Black)
- Sections: FUTURE, STDLIB, DJANGO, THIRDPARTY, FIRSTPARTY, LOCALFOLDER

### Flake8 (Linter)

Checks code for PEP 8 compliance and common errors.

```bash
# Run linting
make lint-quick
# OR: flake8 .
```

**Configuration**: `.flake8`
- Max line length: 100
- Ignores: E203, W503, E501 (Black compatibility)
- Max complexity: 10

### Pylint (Deep Analysis)

More comprehensive code analysis (optional for local use).

```bash
# Run pylint
make lint
# OR: pylint accounts/ clinical/ research/ shared/ backend/
```

**Configuration**: `.pylintrc`
- Django plugin enabled
- Customized for Django projects

### pytest (Testing)

Run tests with coverage tracking.

```bash
# Run tests with coverage
make test

# Run tests without coverage (faster)
make test-fast

# Run verbose tests
make test-verbose

# Run specific test file
pytest accounts/tests/test_models.py

# Run specific test
pytest accounts/tests/test_models.py::TestUserModel::test_create_user
```

**Configuration**: `pyproject.toml` → `[tool.pytest.ini_options]`

## Makefile Commands

The `Makefile` provides convenient shortcuts for common tasks:

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

## Pre-commit Hooks

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

**Manual execution:**
```bash
# Run hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for emergency commits (not recommended)
git commit --no-verify
```

## CI/CD Pipeline

### GitHub Actions Workflow

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

**Viewing CI results:**
- Check the "Actions" tab on GitHub
- CI status shown on pull requests
- Must pass all checks before merging

### Local CI Simulation

Test your changes locally before pushing:

```bash
# Run all CI checks locally
make format
make lint-quick
make check
python manage.py makemigrations --check --dry-run
make test
```

## Testing Guidelines

### Writing Tests

1. **Location**: Place tests in `<app>/tests/` directory
2. **Naming**: Use `test_*.py` or `*_tests.py`
3. **Structure**: Use descriptive test names

**Example:**
```python
# accounts/tests/test_authentication.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserAuthentication:
    def test_user_can_login_with_valid_credentials(self):
        # Arrange
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        # Act
        can_login = user.check_password('testpass123')

        # Assert
        assert can_login is True
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.slow
@pytest.mark.unit
@pytest.mark.api
def test_something():
    pass
```

Run specific test categories:
```bash
pytest -m unit          # Run unit tests only
pytest -m "not slow"    # Skip slow tests
pytest -m api           # Run API tests only
```

## Troubleshooting

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. **Formatting issues**: Run `make format` to auto-fix
2. **Linting issues**: Review flake8 errors and fix manually
3. **Django check failures**: Fix Django configuration issues

### Import Errors After Installing New Package

```bash
# Regenerate requirements
pip freeze > requirements.txt

# Or for dev dependencies
pip freeze > requirements-dev.txt
```

### Coverage Not Updating

```bash
# Clean coverage cache
make clean

# Re-run tests
make test
```

## Best Practices

1. **Always run pre-commit hooks**: `make pre-commit` (one-time setup)
2. **Format before committing**: `make format`
3. **Run tests frequently**: `make test-fast` during development
4. **Keep coverage high**: Aim for >80% coverage
5. **Follow commit conventions**: Use `feat:`, `fix:`, `docs:`, etc.
6. **Update tests**: Add/update tests for new features
7. **Check migrations**: Never commit without checking migrations

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/
- **Black Documentation**: https://black.readthedocs.io/
- **pytest Documentation**: https://docs.pytest.org/
- **Pre-commit Documentation**: https://pre-commit.com/
