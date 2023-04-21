#!/bin/bash

# Download ngrok and move it to /usr/local/bin
curl -o ngrok.zip https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-darwin-amd64.zip
unzip ngrok.zip
rm ngrok.zip
sudo mv ngrok /usr/local/bin

# Authenticate with ngrok
echo "Enter your ngrok authtoken:"
read authtoken
ngrok authtoken $authtoken

echo "ngrok is now set up and authenticated!"

