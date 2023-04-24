#!/bin/bash

echo "Starting bot(s) ..."
uvicorn main:app --port 8000 --host 0.0.0.0 

