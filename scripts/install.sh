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
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_app.py" >> app.py

# Create test directory and test file
# curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/tests.sh" | sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/test.py" >> test.py

# Check if OpenAI API key exists
if [ ! -v OPENAI_API_KEY ]; then
  # Call another script to set the environment variable
  # sh openai_sh.sh
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/openai_install.sh" | sh
fi


# Setup ngrok to let anyone access your bot with a internet-facing url
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/ngrok_install.sh" | sh


# Exit virtual environment
deactivate

echo "BaseBot: ${project_dir} project initialized successfully!"

