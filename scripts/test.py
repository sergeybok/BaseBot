import argparse

import requests
from basebot import MessageContents, TheMessage

local_uuid = 'test1f3a-97ee-4e7e-8242-7b1d202c0fb5'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help='localhost:{port}', default=8000)
    args = parser.parse_args()

    bot_name = input('BotName: ')
    url = f'http://localhost:{args.port}/bots/{bot_name}'
    resp = requests.get(url+'/about').json()
    bot_id = resp['bot_id']

    def message_init():
        import time
        import uuid
        return TheMessage(timestamp=time.time(),
                        sender_id=local_uuid, 
                        contents=MessageContents(text=''),
                        message_id=str(uuid.uuid4()),
                        recipient_id=bot_id)

    def get_message_to():
        text = input('Prompt: ')
        msg_w = message_init()
        msg_w.contents.text = text
        resp = requests.post(url + '/respond', json=msg_w.dict())
        resp = resp.json()
        out_msg = TheMessage.parse_obj(resp)
        print(f"{bot_name}: {out_msg.contents.text}")

    print('\t Ctrl+C to EXIT')

    while True:
        get_message_to()
