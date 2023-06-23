#!/bin/bash

# Marketplace API endpoint URLs
AUTH_URL="https://dev.friendlyai.xyz/users/login_account"
REGISTRATION_URL="https://dev.friendlyai.xyz/users/register_bot"

# Print usage instructions
echo ""
echo "You are about to register a bot on the Friendly AI marketplace."
echo "Please make sure that your bot implements the BaseBot protocol and is deployed before proceeding."
echo ""
echo "Please enter the following information:"
echo ""

# Prompt the user for input
read -p "Username (email): " USERNAME
read -p "Password: " -s PASSWORD
echo ""
read -p "Bot URL: " BOT_URL

# Log in the user
AUTH_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"email\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" $AUTH_URL)

# Parse the access token
ACCESS_TOKEN=$(echo $AUTH_RESPONSE | sed -n 's/.*"token":"\([^"]*\)".*/\1/p')

# Send the API request to register the bot
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" -d "{\"bot_url\": \"$BOT_URL\"}" $REGISTRATION_URL)

# Parse response
SUCCESS=$(echo $RESPONSE | sed -n 's/.*"success":\([^"]*\),.*/\1/p')
REASON=$(echo $RESPONSE | sed -n 's/.*"reason":"\([^"]*\)".*/\1/p')

echo ""
if [[ $SUCCESS ]]; then
  echo "You have successfully registered $BOT_URL."
  echo "Please go to https://friendlyai.xyz/bots/latest to view your bot on the Friendly AI marketplace."
  echo "Note that it may take up to a couple of minutes for your publication to be reflected on our marketplace."
else
  echo $REASON
  echo "Registration failed. Please try again."
fi
