#!/bin/bash

# Script name: get_offline_src.sh
# Description: Creates a Python virtualenv and runs an offline Kubernetes list generator

VENV_NAME="offline-venv"

# Create virtual environment
echo "Creating Python virtual environment: $VENV_NAME"
/usr/bin/python3 -m venv "$VENV_NAME"

# Activate virtual environment
echo "Activating virtual environment"
source "$VENV_NAME/bin/activate"

sudo python3 -m pip install --upgrade pip setuptools

pip install ansible==9.13.0

# Run the generate_list script
echo "Running generate_list.sh..."
./generate_list.sh

# Deactivate virtual environment
deactivate
echo "Done. Virtual environment deactivated."
