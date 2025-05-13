# Contributing to Observer Backend

Thank you for your interest in contributing to the Observer Backend project! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our Code of Conduct in all your interactions with the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/observer_backend.git`
3. Create a feature branch from `dev`: `git checkout -b feature/your-feature-name`
4. Set up your development environment following the instructions in the README

## Development Workflow

1. Make your changes, following our coding standards
2. Write or update tests as needed
3. Ensure all tests pass
4. Update documentation if necessary
5. Commit your changes with descriptive messages
6. Push your branch to your fork
7. Submit a Pull Request to the `dev` branch

## Reporting Issues

Before submitting an issue, please check if it already exists. When reporting an issue, include:

1. **Steps to Reproduce**: Clear steps to reproduce the issue
2. **Expected behavior**: What you expected to happen
3. **Actual behavior**: What actually happened
4. **Frequency of Occurrence**: How often the issue occurs
5. **Environment configuration**: Details about your environment (OS, Python version, etc.)
6. **Additional Information**: Any other relevant information (screenshots, logs, etc.)

## Feature Requests

Feature requests are welcome. Please provide:

1. A clear description of the feature
2. The motivation behind the feature
3. How it should work
4. Examples of how it would be used

## Pull Request Process

1. Create your PR against the `dev` branch
2. Ensure your branch is up to date with the current `dev` branch
3. Make sure all tests pass and code quality checks are successful
4. Request a review from project maintainers
5. Address any feedback or changes requested during review
6. Once approved, a maintainer will merge your PR

## Code Style Guidelines

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Write docstrings for classes and functions
- Keep functions focused (single responsibility principle)
- Comment complex code sections

## Git Commit Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Limit the first line to 72 characters
- Start commits with a type prefix:
  - `fix:` Bug fixes
  - `feat:` New features
  - `docs:` Documentation updates
  - `test:` Test updates
  - `refactor:` Code refactoring
  - `style:` Code style/formatting changes
  - `perf:` Performance improvements
  - `chore:` Build process or tooling changes

Examples:

```
feat: Add Penn Personalized Care encounter source
fix: Correct patient satisfaction score calculation
docs: Update API documentation for the v1 routes
```

## Testing

- Write tests for all new features and bug fixes
- Maintain or improve code coverage
- Run the full test suite before submitting a PR

## Documentation

- Update relevant documentation for new features
- Document API changes
- Include code examples where appropriate

## Review Process

- PRs require approval from at least one maintainer
- Reviewers will check for:
  - Code quality and style
  - Test coverage
  - Documentation
  - Potential issues or bugs

Thank you for contributing to Observer Backend! Your efforts help make this project better for everyone.
