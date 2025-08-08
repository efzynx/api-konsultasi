# GitHub CI Pipeline Documentation

This document describes the comprehensive GitHub CI/CD pipeline set up for the API Konsultasi project.

## Pipeline Overview

The CI pipeline consists of multiple jobs that run in parallel and sequence to ensure code quality, security, and functionality:

### 1. Code Quality & Linting (`lint-and-format`)
- **Black**: Code formatting checker
- **isort**: Import sorting checker  
- **flake8**: Python linting and style checking

### 2. Security Scanning (`security-scan`)
- **Safety**: Checks for known security vulnerabilities in dependencies
- **Bandit**: Static security analysis for Python code

### 3. Testing (`test`)
- Runs on multiple Python versions (3.11, 3.12, 3.13)
- Uses MySQL 8.0 service for database testing
- Generates code coverage reports
- Uploads coverage to Codecov

### 4. Docker Build & Test (`docker-build`)
- Builds Docker image using BuildKit
- Tests the containerized application
- Uses GitHub Actions cache for faster builds

### 5. Integration Testing (`integration-test`)
- Tests complete API workflows
- Uses real database connections
- Validates end-to-end functionality

## Triggers

The pipeline runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## Environment Variables

The following environment variables are used in testing:

```bash
SECRET_KEY=test-secret-key-for-ci
DATABASE_URL=mysql+pymysql://test_user:test_password@127.0.0.1:3306/test_db
JWT_SECRET_KEY=test-jwt-secret-key
FLASK_ENV=testing
```

## Local Development

### Running Tests Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=project --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

### Code Quality Checks

1. Format code:
```bash
black .
isort .
```

2. Lint code:
```bash
flake8 .
```

3. Security scan:
```bash
safety check
bandit -r project/
```

### Docker Testing

1. Build image:
```bash
docker build -t api-konsultasi:test .
```

2. Run container:
```bash
docker run -p 5000:5000 --env-file .env api-konsultasi:test
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_models.py       # Database model tests
│   └── test_auth.py         # Authentication tests
└── integration/             # Integration tests
    ├── __init__.py
    └── test_api_flow.py     # End-to-end API workflow tests
```

## Configuration Files

- `pytest.ini`: Pytest configuration
- `pyproject.toml`: Black, isort, and coverage configuration
- `.flake8`: Flake8 linting configuration
- `.github/workflows/ci.yaml`: Main CI pipeline

## Coverage Reports

Code coverage reports are generated in multiple formats:
- Terminal output during CI
- HTML report (locally in `htmlcov/`)
- XML report for Codecov integration

## Troubleshooting

### Common Issues

1. **MySQL Connection Issues**: Ensure the MySQL service is healthy before running tests
2. **Import Errors**: Check that all dependencies are installed
3. **Authentication Failures**: Verify JWT secret keys are set correctly
4. **Docker Build Failures**: Check Dockerfile syntax and dependencies

### Debugging Failed Builds

1. Check the specific job that failed in GitHub Actions
2. Review the logs for error messages
3. Run the same commands locally to reproduce issues
4. Ensure all environment variables are properly set

## Security Considerations

- Secrets are managed through GitHub repository settings
- Test databases use temporary credentials
- Production secrets are never committed to the repository
- Security scanning runs on every build

## Performance Optimizations

- Docker layer caching reduces build times
- Pip dependency caching speeds up Python setup
- Parallel job execution maximizes efficiency
- Matrix builds test multiple Python versions simultaneously

## Contributing

When contributing to this project:

1. Ensure all tests pass locally before pushing
2. Follow the code formatting standards (Black, isort)
3. Add tests for new functionality
4. Update documentation as needed
5. Check that security scans pass

The CI pipeline will automatically validate your changes and provide feedback on any issues.
