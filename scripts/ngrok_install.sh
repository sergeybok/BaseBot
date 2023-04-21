#!/bin/bash


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
    # echo "ngrok is not configured with an auth token. Please run 'ngrok authtoken <your_auth_token>' to configure it."
    # Authenticate with ngrok
    echo "Enter your ngrok authtoken:"
    read authtoken
    if [ -z "$authtoken" ]
    then
        echo "Skipping ngrok setup"
    else
        ngrok authtoken $authtoken
        echo "ngrok is now set up and authenticated!"
    fi

fi


