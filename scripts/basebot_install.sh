#!/bin/bash

# Define project name and directory


echo ">>>>>>>>>>>>>>"
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

# Create main project file

# Create test directory and test file
# curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/tests.sh" | sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/test.py" > test.py


curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/start_bots.sh" > start_bots.sh
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/stop_bots.sh" > stop_bots.sh
chmod +x start_bots.sh
chmod +x stop_bots.sh


# mkdir scripts

# Check if OpenAI API key exists
# if [ ! -v OPENAI_API_KEY ]; then
if [ -z "${OPENAI_API_KEY}" ]; then 
  # Call another script to set the environment variable
  # sh openai_sh.sh
  # curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/openai_install.sh" | bash

  echo ">>>>>>>>>>>>>>"
  echo "See https://platform.openai.com/account/api-keys for more details" 
  read -p "Enter your OpenAI API key [optional]: " OPENAI_API_KEY
  if [ -z "$OPENAI_API_KEY" ]
  then
      echo "Skipping OpenAI setup"
  else
    # Check if the system is running Linux or macOS
    if [ "$(uname)" == "Linux" ] || [ "$(uname)" == "Darwin" ]; then

      # Check if the user is running Zsh
      if [ "$(echo $SHELL)" == "/bin/zsh" ]; then

        # Check if the Zsh configuration file exists
        if [ -f ~/.zshrc ]; then
          echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.zshrc
          # source ~/.zshrc
          export OPENAI_API_KEY=$OPENAI_API_KEY
          echo "OpenAI API key added to .zshrc"
        elif [ -f ~/.zprofile ]; then
          echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.zprofile
          export OPENAI_API_KEY=$OPENAI_API_KEY
          echo "OpenAI API key added to .zprofile"
        else
          echo "Unable to find Zsh configuration file"
          exit 1
        fi

      else
        # Check if the Bash configuration file exists
        if [ -f ~/.bashrc ]; then
          echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.bashrc
          source ~/.bashrc
          echo "OpenAI API key added to .bashrc"
        elif [ -f ~/.bash_profile ]; then
          echo "export OPENAI_API_KEY=\"$OPENAI_API_KEY\"" >> ~/.bash_profile
          source ~/.bash_profile
          echo "OpenAI API key added to .bash_profile"
        else
          echo "Unable to find Bash configuration file"
          exit 1
        fi
      fi

    else
      # Not Linux or macOS
      echo "This script only supports Linux and macOS"
      exit 1
    fi
  fi
fi
# if [ ! -v OPENAI_API_KEY ]; then
if [ -z "${OPENAI_API_KEY}" ]; then 
  echo "No OpenAI api key, initializing WhyBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_why_bot.py" >> main.py
  sed "s/WhyBot/${project_dir}/g" main.py >> tmp_main.py
  mv tmp_main.py main.py
else 
  echo "Has OpenAI api key, initializing ChatGPTBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_chatgpt.py" >> main.py
  sed "s/ChatGPTBot/${project_dir}/g" main.py >> tmp_main.py
  mv tmp_main.py main.py
fi
############# OPENAI over


# Setup ngrok to let anyone access your bot with a internet-facing url
# curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/ngrok_install.sh" | sh
# Check if ngrok is installed
if ! command -v ngrok &> /dev/null
then
    echo "ngrok is not installed. Installing..."
    # Download ngrok and move it to /usr/local/bin
    curl -o ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip
    unzip ngrok.zip
    rm ngrok.zip
    sudo mv ngrok /usr/local/bin

else
    echo "ngrok is already installed."
fi

# Check if ngrok has an auth token
if [ -z "$NGROK_AUTH_TOKEN" ]
then
    # echo "ngrok is not configured with an auth token. Please run 'ngrok authtoken <your_auth_token>' to configure it."
    # Authenticate with ngrok
    echo ">>>>>>>>>>>>>>"
    echo "Go to https://ngrok.com/docs/getting-started/#step-3-connect-your-agent-to-your-ngrok-account for more details " 
    echo "Enter your ngrok authtoken [optional]:"
    read authtoken
    if [ -z "$authtoken" ]
    then
        echo "Skipping ngrok setup"
    else
        ngrok authtoken $authtoken
        echo "ngrok is now set up and authenticated!"
    fi

fi

############ NGROK over



echo "BaseBot: ${project_dir} project initialized successfully!"




echo ">>>>>>>>>>>>>>"
read -p "Start demo bot [y/N]? " choice
case "$choice" in 
  y|Y ) 
    echo "Starting bot(s) ..."
    nohup uvicorn main:app --port 8000 --host 0.0.0.0 > bot.log 2>&1 &

    # Get the PID of the app process
    APP_PID=$!

    # Save the PID to a file
    echo $APP_PID > app.pid
    echo "App started with PID $APP_PID"
    echo "To stop the bot, run ./stop_bots.sh "

    # Insert test script code here
    echo ">>>>>>>>>>>>>>"
    read -p "Start test script [y/N]? " choice
    case "$choice" in 
      y|Y )
        echo "Encoding local bot url into a qr code..."
        curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/dev/scripts/share_localhost.sh" | sh
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



