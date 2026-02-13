.PHONY: help install install-dev format lint test migrate clean run shell

# NOTE: Activate your conda environment before running make commands:
# conda activate observer

# Use python -m to run commands (uses active Python environment)
PYTHON := python
PIP := pip

# Default target
help:
	@echo "Observer Backend - Development Commands"
	@echo ""
	@echo "IMPORTANT: Activate conda environment first: conda activate observer"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make lint          - Run all linters (flake8, pylint)"
	@echo "  make lint-quick    - Run quick linting with flake8 only"
	@echo "  make test          - Run tests with coverage"
	@echo "  make test-fast     - Run tests without coverage"
	@echo "  make migrate       - Run migrations for all databases"
	@echo "  make migrate-make  - Create new migrations"
	@echo "  make clean         - Clean cache and build files"
	@echo "  make run           - Run development server"
	@echo "  make shell         - Open Django shell"
	@echo "  make check         - Run Django system checks"
	@echo "  make pre-commit    - Install pre-commit hooks"
	@echo "  make coverage      - Generate and open HTML coverage report"

install:
	@echo "Installing production dependencies..."
	$(PIP) install -r requirements.txt

install-dev:
	@echo "Installing development dependencies..."
	$(PIP) install -r requirements-dev.txt

format:
	@echo "Formatting code with Black..."
	$(PYTHON) -m black .
	@echo "Sorting imports with isort..."
	$(PYTHON) -m isort .
	@echo "✓ Code formatted successfully"

lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 .
	@echo "Running pylint..."
	@$(PYTHON) -m pylint accounts/ clinical/ research/ shared/ backend/; \
	PYLINT_EXIT=$$?; \
	if [ $$PYLINT_EXIT -eq 1 ] || [ $$PYLINT_EXIT -eq 32 ]; then \
		echo "✗ Pylint found fatal errors"; \
		exit 1; \
	else \
		echo "✓ Pylint completed (rating displayed above)"; \
	fi
	@echo "✓ Linting completed"

lint-quick:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 .
	@echo "✓ Quick linting completed"

test:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest --cov --cov-report=html --cov-report=term-missing
	@echo "✓ Tests completed. Coverage report: htmlcov/index.html"

test-fast:
	@echo "Running tests without coverage..."
	$(PYTHON) -m pytest
	@echo "✓ Tests completed"

test-verbose:
	@echo "Running tests with verbose output..."
	$(PYTHON) -m pytest -v --cov --cov-report=term-missing
	@echo "✓ Tests completed"

migrate:
	@echo "Running migrations for all databases..."
	$(PYTHON) manage.py migrate --database=accounts
	$(PYTHON) manage.py migrate --database=clinical
	$(PYTHON) manage.py migrate --database=research
	@echo "✓ Migrations completed"

migrate-make:
	@echo "Creating new migrations..."
	$(PYTHON) manage.py makemigrations
	@echo "✓ Migrations created"

clean:
	@echo "Cleaning cache and build files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .tox/ dist/ build/
	@echo "✓ Cleaned successfully"

run:
	@echo "Starting development server..."
	$(PYTHON) manage.py runserver

shell:
	@echo "Opening Django shell..."
	$(PYTHON) manage.py shell

check:
	@echo "Running Django system checks..."
	$(PYTHON) manage.py check
	@echo "✓ System checks passed"

pre-commit:
	@echo "Installing pre-commit hooks..."
	$(PYTHON) -m pre_commit install
	@echo "✓ Pre-commit hooks installed"

coverage:
	@echo "Generating HTML coverage report..."
	$(PYTHON) -m pytest --cov --cov-report=html
	@echo "Opening coverage report..."
	open htmlcov/index.html || xdg-open htmlcov/index.html
