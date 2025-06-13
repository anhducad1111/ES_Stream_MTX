# Python Project Standards & Rules

## 1. Package Structure Requirements

### 1.1 Directory Organization

```
project_root/
├── src/                    # Source code package
│   ├── __init__.py        # Root package init
│   ├── model/             # Data models
│   │   ├── __init__.py
│   │   └── *.py
│   ├── view/              # UI components
│   │   ├── __init__.py
│   │   └── *.py
│   ├── presenter/         # Business logic
│   │   ├── __init__.py
│   │   └── *.py
│   └── controller/        # Controllers (if needed)
│       ├── __init__.py
│       └── *.py
├── tests/                 # Test files
├── docs/                  # Documentation
├── assets/                # Static assets
├── config/                # Configuration files
├── requirements.txt       # Dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
└── main.py               # Entry point
```

### 1.2 Package __init__.py Requirements

- __MUST__ have `__init__.py` in every package directory
- __MUST__ export public classes/functions in `__all__`
- __SHOULD__ include docstring describing package purpose
- __MAY__ include version info for root package

Example:

```python
"""
Model Package
Contains all data models for the application.
"""

from .auth_model import AuthModel
from .data_model import DataModel

__all__ = [
    'AuthModel',
    'DataModel'
]
```

## 2. Code Formatting Standards

### 2.1 Spacing Rules

- __MUST__ have single blank line between methods within a class
- __MUST__ have double blank line between classes
- __MUST__ have exactly one blank line at the end of every file
- __MUST__ use 4 spaces for indentation (no tabs)
- __MUST__ limit line length to 88 characters (Black standard)

### 2.2 Class Structure

```python
class ExampleClass:
    """Class docstring explaining purpose."""

    def __init__(self):
        """Initialize instance."""
        pass

    def method_one(self):
        """Method docstring."""
        pass

    def method_two(self):
        """Another method docstring."""
        pass


class AnotherClass:
    """Another class with double blank line separation."""
    pass
```

### 2.3 Import Organization

```python
# Standard library imports
import os
import sys
from typing import Dict, List

# Third-party imports
import requests
import customtkinter as ctk

# Local application imports
from src.model.auth_model import AuthModel
from src.view.main_view import MainView
```

## 3. Documentation Requirements

### 3.1 Docstrings

- __MUST__ have docstrings for all classes
- __MUST__ have docstrings for all public methods
- __SHOULD__ use Google or NumPy docstring style
- __SHOULD__ include parameter and return type information

Example:

```python
def authenticate(self, username: str, password: str) -> bool:
    """
    Authenticate user with credentials.
    
    Args:
        username: User's login name
        password: User's password
        
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        ConnectionError: If unable to connect to auth server
    """
    pass
```

### 3.2 README.md Structure

```markdown
# Project Name

## Description
Brief project description

## Installation
Step-by-step installation guide

## Usage
How to run and use the application

## Project Structure
Directory structure explanation

## Contributing
Guidelines for contributors

## License
License information
```

## 4. Architecture Patterns

### 4.1 MVP (Model-View-Presenter) Requirements

- __Model__: Data and business logic only
- __View__: UI components, no business logic
- __Presenter__: Mediates between Model and View

### 4.2 Observer Pattern

- Models SHOULD notify observers of state changes
- Use observer pattern for loose coupling
- Implement add_observer/remove_observer methods

### 4.3 Separation of Concerns

- Views MUST NOT contain business logic
- Models MUST NOT import UI frameworks
- Presenters handle all interactions between Model and View

## 5. Error Handling

### 5.1 Exception Handling

- __MUST__ use specific exception types
- __MUST__ handle exceptions gracefully
- __SHOULD__ log errors appropriately
- __MUST NOT__ use bare except clauses

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    return default_value
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

### 5.2 Input Validation

- __MUST__ validate all user inputs
- __MUST__ validate network data
- __SHOULD__ use type hints for validation

## 6. Testing Requirements

### 6.1 Test Structure

```
tests/
├── __init__.py
├── test_models/
├── test_views/
├── test_presenters/
└── conftest.py
```

### 6.2 Test Coverage

- __SHOULD__ aim for >80% code coverage
- __MUST__ test all public methods
- __MUST__ test error conditions

## 7. Configuration Management

### 7.1 Configuration Files

- __MUST__ use configuration files for settings
- __SHOULD__ use JSON or YAML for config
- __MUST NOT__ hardcode sensitive data
- __SHOULD__ support environment-specific configs

### 7.2 Environment Variables

- Use environment variables for sensitive data
- Provide defaults for development
- Document all required environment variables

## 8. Version Control

### 8.1 Git Requirements

- __MUST__ have .gitignore file
- __MUST NOT__ commit sensitive data
- __MUST NOT__ commit IDE-specific files
- __SHOULD__ use meaningful commit messages

### 8.2 .gitignore Template

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
config/secrets.json
logs/
```

## 9. Dependencies Management

### 9.1 Requirements Files

- __MUST__ have requirements.txt
- __SHOULD__ pin specific versions
- __MAY__ use requirements-dev.txt for development dependencies

### 9.2 Virtual Environment

- __MUST__ use virtual environment
- __SHOULD__ document Python version requirements
- __MUST__ not commit virtual environment

## 10. Security Requirements

### 10.1 Authentication

- __MUST__ validate all authentication attempts
- __MUST__ use secure password handling
- __SHOULD__ implement proper session management
- __MUST NOT__ log sensitive information

### 10.2 Input Sanitization

- __MUST__ sanitize all external inputs
- __MUST__ validate network data
- __SHOULD__ use parameterized queries for databases

## 11. Performance Guidelines

### 11.1 Code Optimization

- __SHOULD__ profile performance-critical code
- __MUST__ handle large datasets efficiently
- __SHOULD__ implement proper caching where needed

### 11.2 Resource Management

- __MUST__ properly close file handles
- __MUST__ clean up network connections
- __SHOULD__ implement proper garbage collection

## 12. Logging Standards

### 12.1 Logging Levels

- DEBUG: Detailed diagnostic information
- INFO: General operational messages
- WARNING: Warning messages
- ERROR: Error conditions
- CRITICAL: Critical error conditions

### 12.2 Log Format

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 13. Code Quality Tools

### 13.1 Recommended Tools

- __Black__: Code formatting
- __flake8__: Linting
- __mypy__: Type checking
- __pytest__: Testing
- __coverage__: Test coverage

### 13.2 Pre-commit Hooks

- Format code with Black
- Run linting checks
- Run type checking
- Run tests

## 14. Deployment Requirements

### 14.1 Production Readiness

- __MUST__ have proper error handling
- __MUST__ have logging configured
- __MUST__ have health checks
- __SHOULD__ have monitoring

### 14.2 Environment Configuration

- Separate configs for dev/staging/prod
- Use environment variables for secrets
- Document deployment process

---

## Compliance Checklist

Before project delivery, ensure:

- [ ] All directories have __init__.py files
- [ ] All Python files follow formatting standards
- [ ] All classes and public methods have docstrings
- [ ] README.md is complete and accurate
- [ ] .gitignore is properly configured
- [ ] requirements.txt lists all dependencies
- [ ] No hardcoded secrets or sensitive data
- [ ] All imports are properly organized
- [ ] Code follows MVP architecture principles
- [ ] Error handling is implemented
- [ ] Logging is configured
- [ ] Tests are written for core functionality
