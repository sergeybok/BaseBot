#!/bin/bash

read -p "Enter your OpenAI API key: " OPENAI_API_KEY


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
        echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.zshrc
        source ~/.zshrc
        echo "OpenAI API key added to .zshrc"
      elif [ -f ~/.zprofile ]; then
        echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.zprofile
        source ~/.zprofile
        echo "OpenAI API key added to .zprofile"
      else
        echo "Unable to find Zsh configuration file"
        exit 1
      fi

    else
      # Check if the Bash configuration file exists
      if [ -f ~/.bashrc ]; then
        echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.bashrc
        source ~/.bashrc
        echo "OpenAI API key added to .bashrc"
      elif [ -f ~/.bash_profile ]; then
        echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.bash_profile
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

