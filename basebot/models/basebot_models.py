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


def preview_str(s, limit=16):
    if len(s) > limit:
        return s[:limit] + '..'
    return s

class BaseBot:
    """
    BaseBot is the baseclass to make chatbot APIs. Extend the class with your own bot.

    Attributes
    ----------
    name : str
        the name of the bot generated by prepending 'bot.' to the class name
    credits : int
        the number of credits required to ask a single question
    endpoint_* : str
        the endpoint urls added to the FastAPI app by add_endpoints(app) method
    icon_path : str
        the path to your bot icon image

    Endpoints
    -------
    "/bots/{self.__class__.__name__}/about" 
    "/bots/{self.__class__.__name__}/respond" 
    "/bots/{self.__class__.__name__}/history" 
    "/bots/{self.__class__.__name__}/templates" 

    Methods
    -------
    __init__(self, credits:int=0, icon_path:str=None) -> None
        Initializes the bot. Defaults to no credits (no limit on use) and automatically 
          tries to find an image with the same name as the class name as the icon image
    validate_message(self, message:Union[TheMessage, MessageWrapper]) -> TheMessage
        Validation of the message before calling response(). Checks for keywords such as 'Help', and checks sufficient credits if implemented.
    check_credits(self, user_id:str=None) -> bool
        returns True if user has sufficient credits. Needs to be overriden for BaseBot class.
    help(self) -> str
        Returns a helpful message about what the bot does and how to use it. Should be overriden.
    templates(self, user_id=None) -> Union[List[str], List[Template]]
        Returns helpful template phrases repeatedly used in queries.
    _templates(self, request:TemplateRequest=None) -> TemplateResponse
        Wrapper around templates() that receives and returns WebModels
    respond(self, message: MessageWrapper) -> Union[TheMessage, MessageWrapper]
        The main method to override. Takes user message as input. And responds with the bot's response message.
        Suggested use:
        ```
        def respond(self, message):
            context_messages: List[TheMessage] = self.get_message_context(message)
            # do your chatbot logic here
            # ...
            resp_text = {Bot text response}
            resp_images: list = [{Bot image response}, ...]
            resp_message = self.get_message_to(message.get_sender_id())
            resp_message.set_text(resp_text)
            resp_message.set_images_pil(resp_images)
            return resp_message
        ```
    _respond(self, request:TheMessage) -> TheMessage
        Wrapper around respond() that receives TheMessage, validates it, 
          saves it by calling save_chat_message(), calls respond(), and returns TheMessage
    save_chat_message(self, message: TheMessage) -> None
        Persists a message. Needs to be overriden if inheriting from BaseBot.
    get_message_context(self, message:Union[TheMessage, MessageWrapper], limit=10, before_ts=None, descending:bool=True) -> List[MessageWrapper]:
        Uses get_message_history() to fetch the most recent messages to and from the same user as the input message.
        Should be overriden if you don't simply want the {limit} most recent messages as context.
    get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]
        Queries a database to find messages between this bot and the user. The app expects most recent message first (descending order by timestamp).
        Should be overriden if inheriting from BaseBot.
    _get_message_history(self, request: MessageHistoryRequest) -> MessageHistoryResponse
        Wrapper around get_message_history that expects and returns the WebModels
    get_message_to(self, user_id) -> MessageWrapper
        Initializes and returns a new response message with all of the relevant fields set except for contents.
    about(self) -> AboutResponse 
        Returns the metadata of the bot AboutResponse(name=self.name, description=self.help(), icon={b64 str})
    add_endpoints(self, app:FastAPI) -> None
        Adds the routing for the endpoints and corresponding functions
    """
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
    
    def validate_message(self, message:Union[TheMessage, MessageWrapper]) -> TheMessage:
        if isinstance(message, MessageWrapper):
            message = message.get_message()
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
        """
        returns True if user has sufficient credits. Needs to be overriden for BaseBot class.
        """
        if self.credits > 0:
            print(f'{self.name} WARNING: check_credits(message:TheMessage) function \n\t should be overriden if you want to protect your bot!')
        return True
    def help(self) -> str:
        """
        Returns a helpful message about what the bot does and how to use it. Should be overriden.
        """
        print(f'{self.name} SUGGESTIONS: help() function should be overriden to provide \n\ta helpful message about what the bot is and how to use it.')
        return None
    def templates(self, user_id=None) -> Union[List[str],List[Template]]:
        """
        Returns helpful template phrases repeatedly used in queries.
        """
        print(f'{self.name} SUGGESTIONS: templates() function should be overriden \n\tif there are specific phrases people reuse all the time in prompts.')
        return []
    def _templates(self, request:TemplateRequest=None) -> TemplateResponse:
        """
        Wrapper around templates() that receives and returns WebModels
        """
        try:
            templates = self.templates(user_id=request.user_id) 
        except:
            templates = self.templates()
        if templates and len(templates) > 0 and type(templates[0]) == str:
            templates = [ Template(preview=preview_str(t), text=t) for t in templates ]
        return TemplateResponse(templates=templates)
    def respond(self, message: MessageWrapper) -> Union[TheMessage, MessageWrapper]:
        """
        The main method to override. Takes user message as input. And responds with the bot's response message.
        Suggested use:
        ```
        def respond(self, message):
            context_messages: List[TheMessage] = self.get_message_context(message)
            # do your chatbot logic here
            # ...
            resp_text = 'Bot text response'
            resp_images = [{Bot image response}, ...]
            resp_message = self.get_message_to(message.get_sender_id())
            resp_message.set_text(resp_text)
            resp_message.set_images_pil(resp_images)
            return resp_message
        ```
        """
        print(f'{self.name} WARNING: respond(message:TheMessage) function should be overriden!')
        resp_msg = MessageWrapper(user_id=self.name, to_user_id=message.get_sender_id())
        if message.contents.text:
            resp_msg.set_text('You said: ' + message.get_text())
        return resp_msg.get_message()
    def _respond(self, message: TheMessage):
        """
        Wrapper around respond() that receives TheMessage, validates it, 
          saves it by calling save_chat_message(), calls respond(), and returns TheMessage
        """
        valid_msg = self.validate_message(message)
        if valid_msg is not None:
            return valid_msg
        # Not sure if I should save the validation messages?
        self.save_chat_message(message)
        resp = self.respond(MessageWrapper(message))
        if type(message) == TheMessage:
            self.save_chat_message(message)
            return  resp
        self.save_chat_message(resp.get_message())
        return resp.get_message()

    def save_chat_message(self, message: TheMessage):
        """
        Persists a message. Needs to be overriden if inheriting from BaseBot.
        """
        print(f'{self.name} WARNING: save_chat_message(message:TheMessage) function should be overriden!')
        return
    def get_message_context(self, message:Union[TheMessage, MessageWrapper], limit=10, before_ts=None, descending:bool=True) -> List[MessageWrapper]:
        """
        Uses get_message_history() to fetch the most recent messages to and from the same user as the input message.
        Should be overriden if you don't simply want the {limit} most recent messages as context.
        """
        if type(message) == MessageWrapper:
            message = message.get_message()
        previous_messages = self.get_message_history(message.user_id, limit=limit+1, before_ts=before_ts, descending=descending)
        if previous_messages:
            return [MessageWrapper(message=msg) for msg in previous_messages if msg.message_id != message.message_id][:limit]
        return []
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        """
        Queries a database to find messages between this bot and the user. The app expects most recent message first (descending order by timestamp).
        Should be overriden if inheriting from BaseBot.
        """
        print(f'{self.name} WARNING: get_message_history(user_id, limit, ...) function should be overriden!')
        return []
    def _get_message_history(self, request: MessageHistoryRequest) -> MessageHistoryResponse:
        """
        Wrapper around get_message_history that expects and returns the WebModels
        """
        messages = self.get_message_history(request.user_id, request.limit, before_ts=request.before_ts, descending=False)
        return MessageHistoryResponse(messages=messages)
    def get_message_to(self, user_id) -> MessageWrapper:
        """
        Initializes and returns a new response message with all of the relevant fields set except for contents.
        """
        return MessageWrapper(sender_id=self.name, recipient_id=user_id)
    def about(self) -> AboutResponse:
        """
        Returns the metadata of the bot AboutResponse(name=self.name, description=self.help(), icon={b64 str})
        """
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
        """
        Adds the routing for the endpoints and corresponding functions
        """
        print('\tAdding: ', self.endpoint_respond)
        app.add_api_route(self.endpoint_respond, self._respond,  methods=["POST"], response_model=TheMessage)
        app.add_api_route(self.endpoint_about, self.about,  methods=["GET"])
        app.add_api_route(self.endpoint_history, self._get_message_history,  methods=["POST"], response_model=MessageHistoryResponse)
        app.add_api_route(self.endpoint_templates, self._templates, methods=['GET','POST'], response_model=TemplateResponse)



class BaseBotWithLocalDb(BaseBot):
    def __init__(self, db_util: MongoUtil = None):
        super().__init__()
        if db_util:
            self.db_util = db_util
        else:
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

