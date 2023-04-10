from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Union
from PIL import Image
import os

from ..utils.image_utils import img_to_b64_string
from ..utils.database_util import MongoUtil
from .the_message import TheMessage, MessageWrapper
from .web_models import AboutResponse, MessageHistoryRequest, MessageHistoryResponse
from .web_models import TemplateRequest, TemplateResponse, Template


def preview_str(s, limit=14):
    if len(s) > limit:
        return s[:limit] + '...'
    return s

class BaseBot:
    app = None
    
    # Class Methods
    @staticmethod
    def start_app(*args) -> FastAPI:
        app = FastAPI()
        for bot in args:
            if isinstance(bot, BaseBot):
                bot.add_endpoints(app)
            else:
                print('WARNING:',bot, 'is not an instance of BaseBot, make sure you define your new class like so: class MyBot(BaseBot)')
        BaseBot.app = app
        return app 
    
    # Instance Methods
    def __init__(self, credits:int=0, icon_path:str=None):
        self.name = 'bot.'+self.__class__.__name__
        self.endpoint_respond = f'/bots/{self.__class__.__name__}/respond'
        self.endpoint_about = f'/bots/{self.__class__.__name__}/about'
        self.endpoint_history = f'/bots/{self.__class__.__name__}/history'
        self.endpoint_templates = f'/bots/{self.__class__.__name__}/templates'
        self.credits = credits
        if icon_path:
            self.icon_path = icon_path
        else:
            self.icon_path = None
            for ext in ['.png', '.jpg', '.jpeg', '.JPEG']:
                if os.path.exists(self.__class__.__name__+ext):
                    self.icon_path = self.__class__.__name__+ext
    def __repr__(self) -> str:
        return self.name + '\n\t'.join([v for k,v in vars(self).items() if k.startswith('endpoint_') and type(v) == str])
    
    def validate_message(self, message:TheMessage) -> TheMessage:
        if message.contents.text.lower().strip() == 'help':
            help_msg = self.help()
            if help_msg is not None:
                resp_msg = MessageWrapper(user_id=self.name, to_user_id=message.user_id)
                resp_msg.set_text(help_msg)
                return resp_msg.get_message()
        if self.check_credits(message.user_id):
            return None
        else: # not enough credits
            resp_msg = MessageWrapper(user_id=self.name, to_user_id=message.user_id)
            resp_msg.set_text(f"Sorry you do not have enough credits. One message costs {self.credits} credits.")
            return resp_msg.get_message()
    def check_credits(self, user_id) -> bool:
        if self.credits > 0:
            print(f'{self.name} WARNING: check_credits(message:TheMessage) function \n\t should be overriden if you want to protect your bot!')
        return True
    def help(self):
        print(f'{self.name} SUGGESTIONS: help() function should be overriden to provide \n\ta helpful message about what the bot is and how to use it.')
        return None
    def templates(self, user_id=None) -> Union[List[str],List[Template]]:
        print(f'{self.name} SUGGESTIONS: templates() function should be overriden \nt\tif there are specific phrases people reuse all the time in prompts.')
        return None
    def _templates(self, request:TemplateRequest=None) -> TemplateResponse:
        if request:
            templates = self.templates(user_id=request.user_id) 
        else:
            templates = self.templates()
        if len(templates) > 0 and type(templates[0]) == str:
            templates = [ Template(preview=preview_str(t), text=t) for t in templates ]
        return TemplateResponse(templates=templates)
    def respond(self, message: MessageWrapper) -> Union[TheMessage, MessageWrapper]:
        print(f'{self.name} WARNING: respond(message:TheMessage) function should be overriden!')
        resp_msg = MessageWrapper(user_id=self.name, to_user_id=message.get_user_id())
        if message.contents.text:
            resp_msg.set_text('You said: ' + message.get_text())
        return resp_msg.get_message()
    def _respond(self, message: TheMessage):
        resp = self.respond(MessageWrapper(message))
        if isinstance(message, TheMessage):
            return  resp
        return resp.get_message()

    def save_chat_message(self, message: TheMessage):
        print(f'{self.name} WARNING: save_chat_message(message:TheMessage) function should be overriden!')
        return
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        print(f'{self.name} WARNING: get_message_history(user_id, limit, ...) function should be overriden!')
        return MessageHistoryResponse(messages=[])
    def _get_message_history(self, request: MessageHistoryRequest) -> MessageHistoryResponse:
        messages = self.get_message_history(request.user_id, request.limit, before_ts=request.before_ts, descending=False)
        return MessageHistoryResponse(messages=messages)
    def get_message_to(self, user_id) -> MessageWrapper:
        return MessageWrapper(user_id=self.name, to_user_id=user_id)
    def about(self) -> AboutResponse:
        icon = None
        if self.icon_path is not None:
            try:
                icon = Image.open(self.icon_path).resize((64,64))
                icon = img_to_b64_string(icon)
            except Exception as e:
                print(f'{self.name} failed to load icon image at {self.icon_path} with exception:\n\t', e)
                icon = None
                pass
        return AboutResponse(name=self.name, icon=icon)
    def add_endpoints(self, app:FastAPI):
        print('\tAdding: ', self.endpoint_respond)
        app.add_api_route(self.endpoint_respond, self.respond,  methods=["POST"], response_model=TheMessage)
        app.add_api_route(self.endpoint_about, self.about,  methods=["GET"])
        app.add_api_route(self.endpoint_history, self._get_message_history,  methods=["POST"], response_model=MessageHistoryResponse)
        app.add_api_route(self.endpoint_templates, self._templates, methods=['GET','POST'], response_model=TemplateResponse)



class BaseBotWithLocalDb(BaseBot):
    def __init__(self):
        super().__init__()
        self.db_util = MongoUtil()
    
    def save_chat_message(self, message: TheMessage):
        self.db_util.save_chat_message(self.name, message)
        return

    def get_message_history(self, user_id:str, limit:int=10, before_ts:float=None, descending:bool=True) -> List[TheMessage]:
        messages = self.db_util.get_chat_messages(name=self.name, user_id=user_id,limit=limit, before_ts=before_ts)
        if descending:
            messages = list(reversed(messages))
        return messages



class BaseBotWithDb(BaseBot):
    def __init__(self, email:str=None, api_key:str=None):
        super().__init__()
        if email is None:
            assert 'BASEBOT_EMAIL' in os.environ, 'You must either provide an email to BaseBotWithDb initializer or set it as environ variable by doing export BASEBOT_EMAIL=your_registered@email.com'
            email = os.environ['BASEBOT_EMAIL']
        if api_key is None:
            assert 'BASEBOT_API_KEY' in os.environ, 'You must either provide an api key to BaseBotWithDb initializer or set it as environ variable by doing export BASEBOT_API_KEY=123abc'
            api_key = os.environ['BASEBOT_API_KEY']
        self.email = email 
        self.api_key = api_key 
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        # TODO Add server call to our server which has a backend
        raise NotImplementedError('TODO implement this')
        # if request is None:
        #     request = MessageHistoryRequest()
        # messages = mongo.get_chat_messages(name=self.name, user_id=request.user_id,limit=request.limit, before_ts=request.before_ts)
        # return MessageHistoryResponse(messages=messages)

