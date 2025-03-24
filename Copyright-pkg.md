Yes! Here's how to package and deploy the script on Ubuntu 22.04:

### 1. Package Structure
Create this directory structure:
```
copyright_updater/
├── copyright_updater/
│   ├── __init__.py
│   ├── main.py          # Your Python script
│   └── config.json
├── setup.py
├── README.md
└── requirements.txt
```

### 2. Required Files

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name="copyright_updater",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'python-magic',  # For file type detection
    ],
    entry_points={
        'console_scripts': [
            'copyright-updater = copyright_updater.main:main'
        ]
    },
    package_data={
        'copyright_updater': ['config.json']
    },
    python_requires='>=3.8',
)
```

**requirements.txt**:
```
python-magic
```

### 3. Installation on Ubuntu 22.04

```bash
# Install system dependencies
sudo apt update && sudo apt install -y python3-dev libmagic1

# Create virtual environment (recommended)
python3 -m venv ~/copyright_env
source ~/copyright_env/bin/activate

# Install the package
pip install .  # From package directory
```

### 4. Create Debian Package (Optional)

1. Install packaging tools:
```bash
sudo apt install -y python3-stdeb fakeroot
```

2. Build package:
```bash
python3 setup.py --command-packages=stdeb.command bdist_deb
```

3. Install the .deb file:
```bash
sudo dpkg -i deb_dist/python3-copyright-updater_1.0.0-1_all.deb
```

### 5. System-wide Installation (Alternative)

```bash
# Install directly
sudo python3 setup.py install

# Verify installation
which copyright-updater
# Should show: /usr/local/bin/copyright-updater
```

### 6. Usage
```bash
# Dry run
copyright-updater /path/to/directory dryrun

# Actual update
copyright-updater /path/to/directory update
```

### 7. Additional Configuration

**For systemd service** (create `/etc/systemd/system/copyright-updater.service`):
```ini
[Unit]
Description=Copyright Header Updater

[Service]
Type=oneshot
ExecStart=/usr/local/bin/copyright-updater /path/to/target update

[Install]
WantedBy=multi-user.target
```

### Key Features:
1. **Self-contained Package**: Includes config.json and dependencies
2. **CLI Integration**: Installs as system command
3. **Debian Packaging**: For easy distribution
4. **Logging**: Output to `copyright_updater.log` in current directory
5. **Permission Preservation**: Maintains original file permissions

### Verification:
```bash
# Check modified files
grep UPDATED copyright_updater.log

# Verify permissions
ls -l $(awk '/UPDATED/ {print $3}' copyright_updater.log | head -1)
```

### Uninstallation:
```bash
# For pip install
pip uninstall copyright_updater

# For deb package
sudo apt remove python3-copyright-updater
```

This packaging method ensures:
- Proper dependency management
- Configuration file preservation
- System integration
- Easy updates and maintenance
- Compatibility with Ubuntu 22.04's Python 3.10 environment
