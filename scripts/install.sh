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

# Create main project file

# Create test directory and test file
# curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/tests.sh" | sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/test.py" >> test.py


curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/start_bots.sh" >> start_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/stop_bots.sh" >> stop_bots.sh
chmod +x start_bots.sh
chmod +x stop_bots.sh


# Check if OpenAI API key exists
# if [ ! -v OPENAI_API_KEY ]; then
if [ -z "${OPENAI_API_KEY}" ]; then 
  # Call another script to set the environment variable
  # sh openai_sh.sh
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/openai_install.sh" | sh
fi

# if [ ! -v OPENAI_API_KEY ]; then
if [ -z "${OPENAI_API_KEY}" ]; then 
  echo "No OpenAI api key, initializing WhyBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_why_bot.py" >> main.py
  sed "s/WhyBot/${project_dir}/g" main.py >> main.py
else 
  echo "Has OpenAI api key, initializing ChatGPTBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_chatgpt.py" >> main.py
  sed "s/ChatGPTBot/${project_dir}/g" main.py >> main.py
fi

# Setup ngrok to let anyone access your bot with a internet-facing url
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/ngrok_install.sh" | sh



echo "BaseBot: ${project_dir} project initialized successfully!"


echo "Start demo bot [y/N]? "
read SHOULD_START_TEST
if [ -z "$SHOULD_START_TEST" ]
then
    echo "Not starting test script"
    # Exit virtual environment
else
    echo "Starting test script"
    python3 test.py
fi



read -p "Start demo bot [y/N]? " choice
case "$choice" in 
  y|Y ) 
    echo "Starting bot, to stop it run  ./stop_bots.sh "
    sh start_bots.sh
    # Insert test script code here
    read -p "Start test script [y/N]? " choice
    case "$choice" in 
      y|Y ) 
        echo "Starting test script..."
        python3 test.py
        # Insert test script code here
        ;;
      * ) 
        exit 0
        ;;
    esac
    ;;
  * ) 
    deactivate
    exit 0
    ;;
esac



