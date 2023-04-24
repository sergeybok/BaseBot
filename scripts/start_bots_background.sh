#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)

# Start the app in the background and save the logs to a file
echo "Starting bot(s) in the background ..."
nohup uvicorn main:app --port 8000 --host 0.0.0.0 > bot.log 2>&1 &

# Get the PID of the app process
APP_PID=$!

# Save the PID to a file
echo $APP_PID > app.pid
echo "App started with PID $APP_PID"
# echo "To stop the bot, run ./stop_bots.sh "
echo "${bold}To stop the bot, run ./stop_bots.sh  ${normal}" 


