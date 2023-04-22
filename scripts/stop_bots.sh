#!/bin/bash

# Read the PID of the app process from the PID file
APP_PID=$(cat ../app.pid)

# Terminate the app process
kill $APP_PID

# Remove the PID file
rm ../app.pid

# Success!
echo "App stopped"
