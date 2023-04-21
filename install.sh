#!/bin/bash

# Define project name and directory
echo "Enter project name:"
read project_name
project_dir="$project_name"

# Create project directory
mkdir "$project_dir"
cd "$project_dir"

# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install --upgrade pip
pip install wheel
pip install pytest
pip install coverage
pip install ruff
pip install git+https://github.com/sergeybok/BaseBot.git
pip install sphinx
 
# Create requirements file
touch requirements.txt

# Initialize Git repository
git init

# Create .gitignore file
touch .gitignore
echo "# Python" >> .gitignore
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "build/" >> .gitignore
echo "dist/" >> .gitignore
echo "*.egg-info/" >> .gitignore

# Create main project file
touch main.py

# Create test directory and test file
zsh tests.sh

# Setup OpenAI API key
zsh openai_sh.sh

# Setup ngrok to let anyone access your bot with a internet-facing url
ngrok_install.sh

# Initialize Sphinx documentation
sphinx-quickstart

# Open project directory in VSCode
code .

# Exit virtual environment
deactivate

echo "Python project initialized successfully!"

