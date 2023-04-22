#!/bin/bash

# Define the name of the virtual environment
venv_name="venv"

# Check if the virtual environment exists
if [ ! -d "$venv_name" ]; then
    # If not, create it
    echo "Creating virtual environment..."
    python3 -m venv "$venv_name"
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$venv_name/bin/activate"

# Check if the required Python packages are installed
if ! python3 -c "import qrcode" &> /dev/null; then
    # If not, install them using pip
    echo "Installing qrcode..."
    pip install -q qrcode
fi

# Run the share_localhost.py script
echo "Running share_localhost.py..."
python3 scripts/share_localhost.py

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

