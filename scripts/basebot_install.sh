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
echo "Installing required packages..."
pip install -q --upgrade pip
pip install -q wheel
pip install -q pytest
pip install -q coverage
pip install -q --upgrade openai
pip install -q qrcode
pip install -q git+https://github.com/sergeybok/BaseBot.git

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

# Create tests directory and test case file
mkdir tests
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/test.py" > ./tests/test.py

# Create scripts directory
mkdir "scripts"
cd "scripts"

# Create start and stop scripts
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/start_bots.sh" > start_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/stop_bots.sh" > stop_bots.sh
chmod +x start_bots.sh
chmod +x stop_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/start_bots_background.sh" > start_bots.sh
chmod +x start_bots_background.sh

# Setup OpenAI
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/openai_install.sh" > openai_install.sh
chmod +x openai_install.sh
sh openai_install.sh "$project_dir"

# Prompt user to setup ngrok
read -p "Setup ngrok [y/N]? " choice
case "$choice" in 
  y|Y ) 
    # Setup ngrok to let anyone access your bot with a internet-facing url
    curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/ngrok_install.sh" > ngrok_install.sh
    chmod +x ngrok_install.sh
    sh ngrok_install.sh
esac

# Setup localhost sharing
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/share_localhost.sh" > share_localhost.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev-reorganize-install/scripts/share_localhost.py" > share_localhost.py
chmod +x share_localhost.sh

# Success!
echo "BaseBot: ${project_dir} project initialized successfully!"

# Return to project root
cd ..

# Start the app in the background, show qr with local network address, and save the logs to a file
read -p "Start demo bot [y/N]? " choice
case "$choice" in 
  y|Y ) 
    sh scripts/start_bots_background.sh
    python3 scripts/share_localhost.py --bot_name $project_dir
esac


# Prompt user to start test script
read -p "Start test script [y/N]? " choice
case "$choice" in 
  y|Y )
    
    # Start test script
    echo "Starting test script..."
    python3 ./tests/test.py
esac