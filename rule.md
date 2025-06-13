# Python Project Standards & Rules

## 1. Package Structure Requirements

### 1.1 Directory Organization

```
project_root/
├── src/                    # Source code package
│   ├── __init__.py        # Root package init
│   ├── utils/utils.py           # Common utilities
│   ├── model/             # Data models
│   ├── view/              # UI components
│   ├── presenter/         # Business logic
│   └── controller/        # Controllers (if needed)
├── scripts/               # Automation scripts
│   ├── setup.sh          # Project setup
│   ├── build.sh          # Build process
│   ├── deploy.sh         # Deployment
│   └── backup.sh         # Backup procedures
├── tests/                 # Test files
├── docs/                  # Documentation
├── assets/               # Static assets
├── config/              # Configuration files
├── requirements.txt     # Dependencies
├── requirements-dev.txt # Dev dependencies
├── Makefile            # Build automation
├── README.md           # Documentation
├── .gitignore         # Git ignore rules
└── main.py            # Entry point
```

### 1.2 Project Utils (utils.py)

Must provide standard utility functions:

```python
def read_file(filepath: Union[str, Path]) -> str:
    """Read content from a text file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_json(filepath: Union[str, Path], data: Dict[str, Any]) -> None:
    """Save data to a JSON file. Creates directories if needed."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
```

### 1.3 Package __init__.py Requirements

```python
"""
Model Package
Contains all data models for the application.
"""
from .auth_model import AuthModel
from .data_model import DataModel

__all__ = ['AuthModel', 'DataModel']
```

## 2. Code Formatting Standards

### 2.1 Spacing Rules

- Single blank line between methods
- Double blank line between classes
- One blank line at file end
- 4 spaces indentation (no tabs)
- 88 character line limit (Black standard)

### 2.2 Import Organization

```python
# Standard library
import os
from typing import Dict, List

# Third-party
import requests

# Local
from src.model import DataModel
```

## 3. Documentation Requirements

### 3.1 Docstrings

```python
def authenticate(self, username: str, password: str) -> bool:
    """
    Authenticate user with credentials.
    
    Args:
        username: User's login name
        password: User's password
    Returns:
        True if authentication successful
    Raises:
        ConnectionError: If auth server unavailable
    """
    pass
```

### 3.2 README Structure

Must include:

- Project description
- Installation guide
- Usage instructions
- Project structure
- Contributing guidelines
- License information

## 4. Architecture Patterns

### 4.1 MVP Requirements

- Model: Data and business logic only
- View: UI components, no business logic
- Presenter: Mediates Model and View

### 4.2 Observer Pattern

- Models notify observers of changes
- Implement add/remove observer methods
- Use loose coupling

### 4.3 Separation of Concerns

- Views: No business logic
- Models: No UI imports
- Presenters: Handle Model-View interaction

## 5. Error Handling

### 5.1 Exception Handling

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

- Validate all user inputs
- Validate network data
- Use type hints
- Sanitize external inputs

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

### 6.2 Coverage Standards

- 80% code coverage minimum
- Test all public methods
- Test error conditions
- Test edge cases

## 7. Configuration Management

### 7.1 Config Requirements

- Use JSON/YAML config files
- No hardcoded sensitive data
- Support multiple environments
- Use environment variables for secrets
- Document all config options

## 8. Version Control

### 8.1 Git Requirements

- Maintain .gitignore
- No sensitive/IDE files
- Meaningful commits
- Branch naming conventions

### 8.2 .gitignore Essentials

```
# Python
__pycache__/
*.py[cod]
env/
venv/

# IDE
.vscode/
.idea/

# Project
config/secrets.json
logs/
```

## 9. Project Setup

### 9.1 Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 9.2 Makefile Targets

- setup: Create venv and install deps
- clean: Remove build artifacts
- build: Build project
- test: Run tests with coverage
- format: Run Black and isort
- lint: Run flake8

## 10. Code Quality

### 10.1 Required Tools

- Black for formatting
- flake8 for linting
- isort for imports
- mypy for types
- pytest for testing
- coverage for test coverage

### 10.2 Configuration

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
```

## 11. Security Standards

### 11.1 Authentication

- Validate all auth attempts
- Secure password handling
- Proper session management
- No sensitive logging

### 11.2 Data Protection

- Input sanitization
- Parameterized queries
- Secure communications
- Data encryption

## 12. Performance

### 12.1 Optimization

- Profile critical code
- Handle large datasets
- Implement caching
- Resource cleanup

### 12.2 Logging

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app.log'), logging.StreamHandler()]
)
```
