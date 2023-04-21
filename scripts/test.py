import requests 
import argparse
import time 
import uuid

from basebot import TheMessage, MessageWrapper, MessageContents

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, help='localhost:{port}', default=8000)
args = parser.parse_args()

bot_name = input('BotName [ChatGPTBot]: ')
if bot_name == '':
    bot_name = 'ChatGPTBot'

local_uuid = 'test1f3a-97ee-4e7e-8242-7b1d202c0fb5'
url = f'http://localhost:{args.port}/bots/{bot_name}'
resp = requests.get(url+'/about').json()
bot_id = resp['bot_id']

def message_init():
    return TheMessage(timestamp=time.time(),
                      sender_id=local_uuid, 
                      contents=MessageContents(text=''),
                      message_id=str(uuid.uuid4()),
                      recipient_id=bot_id)

def get_message_to():
    msg = input('Prompt: ')
    msg_w = message_init()
    msg_w.contents.text = msg
    resp = requests.post(url + '/respond', json=msg_w.dict())
    resp = resp.json()
    out_msg = TheMessage.parse_obj(resp)
    print(f"{bot_name}: {out_msg.contents.text}")

print('\tCtrl+C to EXIT')

while True:
    get_message_to()
