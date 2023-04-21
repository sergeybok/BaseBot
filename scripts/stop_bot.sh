#!/bin/bash

# Read the PID of the app process from the PID file
APP_PID=$(cat app.pid)

# Terminate the app process
kill $APP_PID

echo "App stopped"
