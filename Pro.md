Here's how to create a complete Python project with all the requested components:

### 1. Project Structure
```
share/copyright/
├── copyright_updater/       # Package directory
│   ├── __init__.py
│   ├── updater.py           # Main script (renamed from copyright_updater.py)
│   └── config.yaml          # Configuration
├── tests/                   # Unit tests
│   ├── __init__.py
│   ├── test_updater.py
│   └── test_data/           # Test files
├── .pylintrc                # Pylint config
├── pyproject.toml           # Black config + project metadata
├── README.md
├── requirements.txt
└── .pre-commit-config.yaml  # Pre-commit hooks
```

### 2. Key Files

#### `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=42"]
build-backend = "setuptools.build_meta"

[tool.black]
line-length = 120
target-version = ["py38"]
include = '\.py$'
exclude = '''
/(
  \.git
  | \.venv
  | build
  | dist
  | tests/test_data
)/
'''

[tool.pytest.ini_options]
python_files = "test_*.py"
testpaths = ["tests"]
addopts = "--verbose --cov=copyright_updater --cov-report=term-missing"
```

#### `.pylintrc`
```ini
[MASTER]
load-plugins=pylint.extensions.mccabe
init-hook="import sys; sys.path.append('.')"

[MESSAGES CONTROL]
disable=
    C0114,  # Missing module docstring
    C0103,  # Variable naming
    R0903,  # Too few public methods
    R0913,  # Too many arguments
    R0914,  # Too many local variables

[FORMAT]
max-line-length=120
indent-string=4

[DESIGN]
max-args=6
max-locals=15
max-returns=6
max-branches=12

[LOGGING]
logging-modules=logging
```

#### `requirements.txt`
```
pyyaml>=6.0
python-magic>=0.4.27
pylint>=3.0.0
black>=23.9.0
pytest>=7.4.0
pytest-cov>=4.1.0
pre-commit>=3.3.0
```

#### `.pre-commit-config.yaml`
```yaml
repos:
- repo: https://github.com/psf/black
  rev: 23.9.1
  hooks:
    - id: black
      args: [--line-length=120]

- repo: https://github.com/pylint-dev/pylint
  rev: v3.0.0
  hooks:
    - id: pylint
      additional_dependencies: ['pylint-extensions']
      args: ["--rcfile=.pylintrc"]
      files: "^copyright_updater/"

- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.4.0
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
    - id: check-added-large-files
```

### 3. Setup Instructions

1. **Initialize the project**:
   ```bash
   cd share/copyright
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   pre-commit install
   ```

2. **Run the tools manually**:
   ```bash
   # Format code
   black .

   # Run linter
   pylint copyright_updater

   # Run tests
   pytest -v --cov

   # Run updater
   python -m copyright_updater.updater /path/to/files update
   ```

3. **Test file example** (`tests/test_updater.py`):
```python
import pytest
from pathlib import Path
from copyright_updater.updater import get_language, extract_shbang_components

def test_shbang_parsing():
    assert extract_shbang_components("#!/usr/bin/python3.12") == ["python312", "python3", "python"]
    assert extract_shbang_components("#!/bin/bash -e") == ["bash"]

def test_language_detection(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("#!/usr/bin/env python3\nprint('hello')")
    assert get_language(test_file, mock_config, mock_patterns) == "python"
```

### 4. CI/CD Integration (GitHub Actions)

Create `.github/workflows/ci.yml`:
```yaml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Black
      run: black --check .
    - name: Run Pylint
      run: pylint --rcfile=.pylintrc copyright_updater
    - name: Run tests
      run: pytest -v --cov --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Key Features

1. **Complete Development Environment**:
   - Formatter (Black)
   - Linter (Pylint)
   - Unit testing (pytest)
   - Coverage reporting

2. **Automated Quality Checks**:
   - Pre-commit hooks
   - CI pipeline
   - Test coverage tracking

3. **Modular Structure**:
   - Proper Python packaging
   - Separate test suite
   - Configurable components

4. **Reproducible Setup**:
   - Clear requirements
   - Standardized configurations
   - Cross-platform support

This setup gives you a professional-grade Python project with all the requested tools integrated into the development workflow.
