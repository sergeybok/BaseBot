from typing import List
from basebot.models import ParamCompenent
import requests
import time, random
from basebot import BaseBotWithLocalDb, MessageWrapper


# STABLE DIFFUSION WEBUI running in server mode
URL_TXT2IMG = 'http://127.0.0.1:7861/sdapi/v1/txt2img'
URL_IMG2IMG = 'http://127.0.0.1:7861/sdapi/v1/img2img'


STEPS = 30
BSIZE = 1

class VanillaStableDiffusion(BaseBotWithLocalDb):
    def parse_text(self, text:str):
        prompt = ''
        nprompt = ''
        lines = [l.strip() for l in text.split('\n')]
        prompt = lines[0]
        if len(lines) >= 2:
            nprompt = lines[1]
        return prompt, nprompt

    def help(self):
        s = "First line is the prompt\n"
        s += "Second line is the negative prompt (overrides bot settings)\n"
        return s

    def templates(self, user_id=None):
        l = [
            'painting by david hockney',
            'digital art, samdoesart, modern disney',
            'high quality, HD, detailed, masterpiece',
            'trending on artstation'
        ]
        return l
    

    def interface_params(self) -> List[ParamCompenent]:
        params = [
            ParamCompenent(name='cfg', default_value=7.5, type_value='float', min_value=1.0, max_value=20.0),
            ParamCompenent(name='width', default_value=400, type_value='int', min_value=300, max_value=500),
            ParamCompenent(name='height', default_value=400, type_value='int', min_value=300, max_value=500),
            ParamCompenent(name='negative_prompt', default_value='blurry', type_value='str'),
            ParamCompenent(name='seed', default_value=-1, type_value='int'),
        ]
        return params

    def respond(self, message: MessageWrapper):
        msg = message
        images = msg.get_images_b64()
        text = msg.get_text()
        if text is not None:
            prompt, nprompt = self.parse_text(text)
            params = message.get_from_extras('params')
            params['seed'] = int(params.get('seed', '-1'))
            default_params = self.default_params()
            for k, p in params.items():
                default_params[k] = p
            if default_params.get('seed', -1) == -1:
                default_params['seed'] = random.randrange(0, 999_999_999)
            seed = default_params['seed']
            d = {
                'prompt': prompt,
                'negative_prompt':  nprompt if nprompt else default_params['negative_prompt'],
                'cfg_scale': default_params['cfg'], 
                'width': default_params['width'], 
                'height': default_params['height'],
                'seed': seed,
                'steps': STEPS,
                'batch_size': BSIZE, 
            }
            if len(images) == 0:
                resp = requests.post(URL_TXT2IMG, json=d).json()
            else:
                d['init_images'] = images[:1]
                resp = requests.post(URL_IMG2IMG, json=d).json()

            resp_msg = self.get_message_to(user_id=msg.get_sender_id())
            resp_msg.set_text(f'Seed: {seed}')
            resp_msg.set_images_b64(resp['images'])
            return resp_msg
        return {}
    

