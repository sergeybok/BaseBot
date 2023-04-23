#!/bin/bash

# Define the name of the virtual environment
venv_name="venv"

# Activate the virtual environment
echo "Activating virtual environment..."
source "$venv_name/bin/activate"

# Run the share_localhost.py script
echo "Running share_localhost.py..."
python3 scripts/share_localhost.py

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

