#!/bin/bash

read -p "Enter your OpenAI API key: " OPENAI_API_KEY

echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.zshrc

source ~/.zshrc

# TODO: support non zsh keys
echo "OpenAI API key added to .zshrc"

