#!/bin/bash

# create tests directory and test case file
mkdir tests
touch tests/test_main.py

# add continuity test
cat << EOF > tests/test_main.py
import requests 
import argparse
import uuid

from basebot import TheMessage, MessageWrapper, MessageContents

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, help="localhost:{port}", default=8000)
args = parser.parse_args()

bot_name = input("Which bot are you trying to test?\n\nBotName: ")
local_uuid = str(uuid.uuid4())
url = f"http://localhost:{args.port}/bots/{bot_name}"
resp = requests.get(url+"/about").json()
bot_id = resp["bot_id"]

def message_init():
    import time 
    import uuid
    return TheMessage(timestamp=time.time(),
                      sender_id=local_uuid, 
                      contents=MessageContents(text=""),
                      message_id=str(uuid.uuid4()),
                      recipient_id=bot_id)

def get_message_to():
    msg = input("Prompt: ")
    msg_w = message_init()
    msg_w.contents.text = msg
    resp = requests.post(url + "/respond", json=msg_w.dict())
    resp = resp.json()
    out_msg = TheMessage.parse_obj(resp)
    print(f"{bot_name}: {out_msg.contents.text}")

while True:
    get_message_to()
EOF
