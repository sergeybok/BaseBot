#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

# Define project name and directory
# echo "Enter project name:"
echo "${bold}Enter your bot name${normal}:" 
read project_name
project_dir="$project_name"

# Create project directory
mkdir "$project_dir"
cd "$project_dir"

# Initialize virtual environment
echo "Creating Python venv..."
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
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/test.py" > ./tests/test.py

# Create scripts directory
mkdir "scripts"
cd "scripts"

# Create start and stop scripts
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/start_bots.sh" > start_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/stop_bots.sh" > stop_bots.sh
chmod +x start_bots.sh
chmod +x stop_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/start_bots_background.sh" > start_bots_background.sh
chmod +x start_bots_background.sh

# Create bot marketplace registration script
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/register.sh" > register.sh
chmod +x register.sh

# Setup OpenAI
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/openai_install.sh" > openai_install.sh
chmod +x openai_install.sh
sh openai_install.sh "$project_dir"


echo "Setting up starterbot:"
if [ -z "${OPENAI_API_KEY}" ]; then 
  echo "No OpenAI api key, initializing WhyBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_why_bot.py" | sed "s/WhyBot/${project_dir}/g" > ../main.py
else 
  echo "Has OpenAI api key, initializing ChatGPTBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_chatgpt.py" | sed "s/ChatGPTBot/${project_dir}/g" > ../main.py
fi

# Setup Webui
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/webui_install.sh" > webui_install.sh
chmod +x webui_install.sh
cd ../
sh scripts/webui_install.sh
cd scripts





# Prompt user to setup ngrok
read -p "${bold}Setup ngrok [y/N]? ${normal} " choice
case "$choice" in 
  y|Y ) 
    # Setup ngrok to let anyone access your bot with a internet-facing url
    curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/ngrok_install.sh" > ngrok_install.sh
    chmod +x ngrok_install.sh
    sh ngrok_install.sh
esac

# Setup localhost sharing
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/share_localhost.sh" > share_localhost.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/share_localhost.py" > share_localhost.py
chmod +x share_localhost.sh

# Success!
echo "BaseBot: ${project_dir} project initialized successfully!"

# Return to project root
cd ..

# Start the app in the background, show qr with local network address, and save the logs to a file
read -p "${bold}Start demo starter bot [Y/n]?${normal} " choice
case "$choice" in 
  n|N ) 
    echo "To start the bots yourself, run ${bold}./scripts/start_bots.sh${normal} from the root project directory"
    exit 0    
esac

echo "Running ${bold}python scripts/share_localhost.py${normal} to display the local URL as well as QR code"
echo "If you have the app simply type in this URL (or scan QR code) and input it into the app"
python3 scripts/share_localhost.py --bot_name $project_dir
echo "If you do not have the app at hand, you can simply run ${bold}python scripts/test.py${normal} in another terminal"

echo "..running ${bold}./scripts/start_bots.sh${normal} from the root project directory"
sh scripts/start_bots.sh
