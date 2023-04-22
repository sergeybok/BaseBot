#!/bin/bash

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
    # Authenticate with ngrok
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
