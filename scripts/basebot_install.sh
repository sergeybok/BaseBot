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
pip install --upgrade openai
pip install git+https://github.com/sergeybok/BaseBot.git

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

# Create test directory and test file
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/tests.sh" | sh

# Create scripts directory
mkdir "scripts"
cd "scripts"

# Create start and stop scripts
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/start_bots.sh" > start_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/stop_bots.sh" > stop_bots.sh
chmod +x start_bots.sh
chmod +x stop_bots.sh

# Setup OpenAI
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/openai_install.sh" > openai_install.sh
chmod +x openai_install.sh
sh openai_install.sh

# Prompt user to setup ngrok
read -p "Setup ngrok [y/N]?" choice
case "$choice" in 
  y|Y ) 
    # Setup ngrok to let anyone access your bot with a internet-facing url
    curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/ngrok_install.sh" > ngrok_install.sh
    chmod +x ngrok_install.sh
    sh ngrok_install.sh
esac

# Setup localhost sharing
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/share_localhost.sh" > share_localhost.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/share_localhost.py" > share_localhost.py
chmod +x share_localhost.sh

# Success!
echo "BaseBot: ${project_dir} project initialized successfully!"

# Start the app in the background, show qr with local network address, and save the logs to a file
sh start_bots.sh
