#!/bin/bash

# Check if OpenAI API key exists
if [ -z "${OPENAI_API_KEY}" ]; then 
  # Call another script to set the environment variable
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
  mv tmp_main.py ../main.py
else 
  echo "Has OpenAI api key, initializing ChatGPTBot"
  curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/demo_chatgpt.py" >> main.py
  sed "s/ChatGPTBot/${project_dir}/g" main.py >> tmp_main.py
  mv tmp_main.py ../main.py
fi
