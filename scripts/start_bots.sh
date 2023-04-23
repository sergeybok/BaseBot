#!/bin/bash

# Start the app in the background and save the logs to a file
echo "Starting bot(s) ..."
nohup uvicorn main:app --port 8000 --host 0.0.0.0 > bot.log 2>&1 &

# Get the PID of the app process
APP_PID=$!

# Save the PID to a file
echo $APP_PID > app.pid
echo "App started with PID $APP_PID"
echo "To stop the bot, run ./stop_bots.sh "

# Prompt user to start test script
read -p "Start test script [y/N]? " choice
case "$choice" in 
  y|Y )
    # Encode local bot url into a qr code
    echo "Encoding local bot url into a qr code..."
    source venv/bin/activate
    sh ./scripts/share_localhost.sh
    deactivate
    # Start test script
    echo "Starting test script..."
    python3 ./tests/test.py
esac