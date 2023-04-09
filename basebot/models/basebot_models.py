from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from PIL import Image
import os

from ..utils.image_utils import img_to_b64_string
from ..utils.database_util import MongoUtil
from .the_message import TheMessage, MessageWrapper
from .web_models import AboutResponse, MessageHistoryRequest, MessageHistoryResponse


class BaseBot:
    app = None
    def __init__(self):
        self.name = 'bot.'+self.__class__.__name__
        self.endpoint_receive = f'/bots/{self.__class__.__name__}/respond'
        self.endpoint_about = f'/bots/{self.__class__.__name__}/about'
        self.endpoint_history = f'/bots/{self.__class__.__name__}/history'

        self.icon_path = None
        for ext in ['.png', '.jpg', '.jpeg', '.JPEG']:
            if os.path.exists(self.__class__.__name__+ext):
                self.icon_path = self.__class__.__name__+ext
    @staticmethod
    def start_app(*args):
        app = FastAPI()
        for bot in args:
            if isinstance(bot, BaseBot):
                bot.add_endpoints(app)
            else:
                print('WARNING:',bot, 'is not an instance of BaseBot, make sure you define your new class like so: class MyBot(BaseBot)')
        BaseBot.app = app
        return app 

    def respond(self, message: TheMessage):
        print(f'{self.name} WARNING: respond(message:TheMessage) function should be overriden!')
        if message.message.get('text'):
            message.message['text'] = 'You said: ' + message.message.get('text')
        return message

    def save_chat_message(self, message: TheMessage):
        print(f'{self.name} WARNING: save_chat_message(message:TheMessage) function should be overriden!')
        return

   
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        print(f'{self.name} WARNING: get_message_history(user_id, limit, ...) function should be overriden!')
        return MessageHistoryResponse(messages=[])
    
    def _get_message_history(self, request: MessageHistoryRequest) -> MessageHistoryResponse:
        messages = self.get_message_history(request.user_id, request.limit, before_ts=request.before_ts, descending=False)
        return MessageHistoryResponse(messages=messages)
    
    def get_message_to(self, user_id):
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
        print('Adding: ', self.endpoint_receive)
        app.add_api_route(self.endpoint_receive, self.receive_message,  methods=["POST"], response_model=TheMessage)
        app.add_api_route(self.endpoint_about, self.about,  methods=["GET"])
        app.add_api_route(self.endpoint_history, self._get_message_history,  methods=["POST"], response_model=MessageHistoryResponse)



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
    def __init__(self, email:str, api_key:str):
        super().__init__()
        self.email = email 
        self.api_key = api_key 
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        # TODO Add server call to our server which has a backend
        raise NotImplementedError('TODO implement this')
        # if request is None:
        #     request = MessageHistoryRequest()
        # messages = mongo.get_chat_messages(name=self.name, user_id=request.user_id,limit=request.limit, before_ts=request.before_ts)
        # return MessageHistoryResponse(messages=messages)

