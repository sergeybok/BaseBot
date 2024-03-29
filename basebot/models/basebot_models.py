from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional, List, Union, Any
from PIL import Image
import os, pickle
import requests
import schedule
from threading import Thread

from ..utils.image_utils import img_to_b64_string
from ..utils.database_util import MongoUtil, DbUtil, JsonUtil
from .the_message import TheMessage, MessageWrapper
from .web_models import AboutResponse, MessageHistoryRequest, MessageHistoryResponse
from .web_models import TemplateRequest, TemplateResponse, Template, ClearMessageHistoryRequest
from .web_models import ParamCompenent, InterfaceParamsResponse, FeedbackRequest

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import time


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
    bot_id : Optional[str]
        initialized to the name of the bot if not explicitly passed. 
    cache_directory : str
        relative path of cache directory of this bot
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
    "/bots/{self.__class__.__name__}/clear_message_history"
    "/bots/{self.__class__.__name__}/interface_params
    "/bots/{self.__class__.__name__}/feedback

    Methods
    -------
    __init__(self, credits:int=0, icon_path:str=None) -> None
        Initializes the bot. Defaults to no credits (no limit on use) and automatically 
          tries to find an image with the same name as the class name as the icon image
    validate_message(self, message:Union[TheMessage, MessageWrapper]) -> TheMessage
        Validation of the message before calling response(). Checks for keywords such as 'Help', and checks sufficient credits if implemented.
    charge_credits(self, message_id:str=None) -> bool
        returns True if user has sufficient credits and they were successfully charged. Needs to be overriden for BaseBot class.
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
    clear_message_history(self, message: TheMessage) -> None
        Deletes all messages. Needs to be overriden if inheriting from BaseBot.
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
    set_endpoint_name(self, name:str) -> None
        Sets endpoint root name => f"/bots/{self.endpoint_name}/*"
    add_endpoints(self, app:FastAPI) -> None
        Adds the routing for the endpoints and corresponding functions
    """
    app = None
    _scheduled_callbacks = []
    _stopped = False
    # Class Methods
    @staticmethod
    def start_app(*args) -> FastAPI:
        app = FastAPI()
        bot_timer_funcs = []
        for bot in args:
            if isinstance(bot, BaseBot):
                bot.add_endpoints(app)
                if bot._timer_seconds is not None and bot._timer_seconds > 0:
                    bot_timer_funcs.append((bot.timer, bot._timer_seconds))
            else:
                print('ERROR LAUNCHING:', bot, 'is not an instance of BaseBot. Make sure you define your new class like so: class MyBot(BaseBot)')

        BaseBot.app = app
        BaseBot._scheduled_callbacks = bot_timer_funcs

        if os.path.exists('static'):
            app.mount("/static", StaticFiles(directory="static"), name="static")

        def schedule_runner():
            min_interval = float('inf')
            for func, interval in BaseBot._scheduled_callbacks:
                schedule.every(interval).seconds.do(func)
                min_interval = min(min_interval, interval)
            if min_interval != float('inf'):
                now = int(time.time())
                wait_time = min_interval - (now % min_interval)
                start_time = wait_time + now
                print(f'\tScheduler sleeping for {wait_time} seconds')
                while time.time() < start_time and not BaseBot._stopped:
                    time.sleep(1)
                while True and not BaseBot._stopped:
                    schedule.run_pending()
                    time.sleep(1)
        def shutdown_event():
            print('Stopping scheduler')
            BaseBot._stopped = True
            BaseBot._scheduler_thread.join()
        BaseBot._scheduler_thread = Thread(target=schedule_runner)
        BaseBot._scheduler_thread.start()
        app.add_event_handler(event_type='shutdown', func=shutdown_event)
        return app
    
    # Instance Methods
    def __init__(self, price:int=0, icon_path:str=None, bot_id:str=None, timer_seconds:int=None, cache_directory:str='bot_cache', suppress_warnings=False):
        self.name = 'bot.'+self.__class__.__name__
        if bot_id:
            self.bot_id = bot_id
        else:
            self.bot_id = self.name
        
        self.set_endpoint_name(self.__class__.__name__)
        self.price = price
        self._timer_seconds = timer_seconds
        self._suppress_warnings = suppress_warnings
        if icon_path:
            self.icon_path = icon_path
        else:
            self.icon_path = None
            for ext in ['.png', '.jpg', '.jpeg', '.JPEG']:
                if os.path.exists(self.__class__.__name__+ext):
                    self.icon_path = self.__class__.__name__+ext
        self.registered = False
        if os.path.exists(os.path.join('templates', 'index.html')) and os.path.exists(os.path.join('static', 'styles.css')):
            self.jinja_templates = Jinja2Templates(directory="templates")
        else:
            self.jinja_templates = None
        self.cache_directory = os.path.join(cache_directory, self.name)

    def __repr__(self) -> str:
        return self.name + '\n\t'.join([v for k,v in vars(self).items() if k.startswith('endpoint_') and type(v) == str])
    
    def clear_message_history(self, request: ClearMessageHistoryRequest):
        print('clear_message_history method needs to be overriden')

    def interface_params(self) -> List[ParamCompenent]:
        """
        Defines the bot parameters screen in the app. See ParamComponent for more details.
        """
        if not self._suppress_warnings:
            print(f'{self.name} SUGGESTIONS: interface_params() function should be overriden \n\tif you have some optional params for your bot')
        return []

    def _interface_params(self) -> InterfaceParamsResponse:
        params = self.interface_params()
        return InterfaceParamsResponse(params=params)
    
    def default_params(self) -> dict:
        """
        Calls interface_params() and returns {name: default_value} as a dict
        """
        P = self.interface_params()
        out = {}
        for param in P:
            v = param.default_value
            t = param.type_value
            if t == 'float':
                v = float(v)
            if t == 'int':
                v = int(v)
            out[param.name] = v
        return out

    def validate_message(self, message:Union[TheMessage, MessageWrapper]) -> TheMessage:
        if isinstance(message, MessageWrapper):
            message = message.get_message()
        if message.contents.text is not None and message.contents.text.lower().strip() == 'help':
            help_msg = self.help()
            if help_msg is not None:
                resp_msg = MessageWrapper(sender_id=self.name, recipient_id=message.sender_id)
                resp_msg.set_text(help_msg)
                return resp_msg.get_message()
        if self.charge_credits(message.message_id):
            return None
        else: # not enough credits
            resp_msg = MessageWrapper(sender_id=self.name, recipient_id=message.sender_id)
            resp_msg.set_text(f"Sorry you do not have enough credits. One message costs {self.price} credits.")
            return resp_msg.get_message()
    def charge_credits(self, message_id) -> bool:
        """
        returns True if user has sufficient credits and was successfully charged. Needs to be overriden for BaseBot class.
        """
        if self.price > 0:
            print(f'{self.name} WARNING: charge_credits(message:TheMessage) function \n\t should be overriden if you want to protect your bot!')
        return True
    def help(self) -> str:
        """
        Returns a helpful message about what the bot does and how to use it. Should be overriden.
        """
        if not self._suppress_warnings:
            print(f'{self.name} SUGGESTIONS: help() function should be overriden to provide \n\ta helpful message about what the bot is and how to use it.')
        return None
    def templates(self, user_id=None) -> Union[List[str],List[Template]]:
        """
        Returns helpful template phrases repeatedly used in queries.
        """
        if not self._suppress_warnings:
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
        if not self._suppress_warnings:
            print(f'{self.name} WARNING: respond(message:TheMessage) function should be overriden!')
        resp_msg = MessageWrapper(user_id=self.name, recipient_id=message.get_sender_id())
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
        if type(resp) == TheMessage:
            self.save_chat_message(resp)
            return  resp
        self.save_chat_message(resp.get_message())
        return resp.get_message()

    def save_chat_message(self, message: TheMessage):
        """
        Persists a message. Needs to be overriden if inheriting from BaseBot.
        """
        if not self._suppress_warnings:
            print(f'{self.name} WARNING: save_chat_message(message:TheMessage) function should be overriden!')
        return
    def get_message_context(self, message:Union[TheMessage, MessageWrapper], limit=10, before_ts=None, descending:bool=True) -> List[MessageWrapper]:
        """
        Uses get_message_history() to fetch the most recent messages to and from the same user as the input message.
        Should be overriden if you don't simply want the {limit} most recent messages as context.
        """
        if type(message) == MessageWrapper:
            message = message.get_message()
        previous_messages = self.get_message_history(message.sender_id, limit=limit+1, before_ts=before_ts, descending=descending)
        if previous_messages:
            return [MessageWrapper(message=msg) for msg in previous_messages if msg.message_id != message.message_id][:limit]
        return []
    def get_message_history(self, user_id:str, limit=10, before_ts=None, descending:bool=True) -> List[TheMessage]:
        """
        Queries a database to find messages between this bot and the user. The app expects most recent message first (descending order by timestamp).
        Should be overriden if inheriting from BaseBot.
        """
        if not self._suppress_warnings:
            print(f'{self.name} WARNING: get_message_history(user_id, limit, ...) function should be overriden!')
        return []
    def _get_message_history(self, request: MessageHistoryRequest) -> MessageHistoryResponse:
        """
        Wrapper around get_message_history that expects and returns the WebModels
        """
        messages = self.get_message_history(request.user_id, request.limit, before_ts=request.before_ts, descending=True)
        return MessageHistoryResponse(messages=messages)
    def get_message_to(self, user_id) -> MessageWrapper:
        """
        Initializes and returns a new response message with all of the relevant fields set except for contents.
        """
        return MessageWrapper(sender_id=self.bot_id, recipient_id=user_id)
    def about(self) -> AboutResponse:
        """
        Returns the metadata of the bot AboutResponse(name=self.name, description=self.help(), icon={b64 str})
        """
        icon = None
        if self.icon_path is not None:
            try:
                icon = Image.open(self.icon_path).convert('RGB').resize((64,64))
                icon = img_to_b64_string(icon)
            except Exception as e:
                print(f'{self.name} failed to load icon image at {self.icon_path} with exception:\n\t', e)
                icon = None
                pass
        return AboutResponse(name=self.name, icon=icon, bot_id=self.bot_id, price=self.price)
    def get_root(self):
        return { 'Bot': self.name }

    def _create_homepage(self):
        with open(os.path.join('templates', 'index.html')) as f:
            s = f.read()
        s = s.replace('BaseBot.name', self.name)
        s = s.replace('BaseBot.endpoint', self.endpoint_name)
        s = s.replace('BaseBot.id', self.bot_id)
        with open(os.path.join('templates', f"{self.name}.html"), 'w') as f:
            f.write(s)

    def _get_homepage(self, request:Request=None):
        return self.jinja_templates.TemplateResponse(f"{self.name}.html", { "request": request })
    
    def feedback(self, message_id:str, rating:float) -> None:
        """
        FeedbackRequest: request.message_id and request.rating
        Should update the database for the given message_id.
        """
        if not self._suppress_warnings:
            print(f'{self.name} WARNING: _feedback(self, request:FeedbackRequest) function should be overriden!')
        pass

    def _feedback(self, request:FeedbackRequest) -> dict:
        self.feedback(request.message_id, request.rating)
        return {}
    
    def cache_save(self, key, **kwargs) -> None:
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)
        fn = os.path.join(self.cache_directory, key+'.pkl')
        with open(fn, 'wb') as f:
            pickle.dump(dict(kwargs), f)
    
    def cache_load(self, key) -> Any:
        fn = os.path.join(self.cache_directory, key+'.pkl')
        if os.path.exists(fn):
            with open(fn, 'rb') as f:
                obj = pickle.load(f)
            return obj
        return None
    
    def timer(self):
        if not self._suppress_warnings:
            print(f'{self.name} WARNING: timer(self) function should be overriden!')
        pass

    def set_endpoint_name(self, name):
        self.endpoint_name = name
    def add_endpoints(self, app:FastAPI):
        """
        Adds the routing for the endpoints and corresponding functions
        """
        print('\tAdding: ', f'/bots/{self.endpoint_name}')
        self.endpoint_interface_params = f'/bots/{self.endpoint_name}/interface_params'
        if self.jinja_templates:
            self._create_homepage()
            app.add_api_route(f'/bots/{self.endpoint_name}', self._get_homepage, methods=['GET'])
        else: 
            app.add_api_route(f'/bots/{self.endpoint_name}', self.get_root, methods=['GET'])
        app.add_api_route(f'/bots/{self.endpoint_name}/respond', self._respond,  methods=["POST"], response_model=TheMessage)
        app.add_api_route(f'/bots/{self.endpoint_name}/about', self.about,  methods=["GET"])
        app.add_api_route(f'/bots/{self.endpoint_name}/history', self._get_message_history,  methods=["POST"], response_model=MessageHistoryResponse)
        app.add_api_route(f'/bots/{self.endpoint_name}/templates', self._templates, methods=['GET','POST'], response_model=TemplateResponse)
        app.add_api_route(f'/bots/{self.endpoint_name}/clear_message_history', self.clear_message_history, methods=['POST'])
        app.add_api_route(f'/bots/{self.endpoint_name}/interface_params', self._interface_params, methods=['GET','POST'])
        app.add_api_route(f'/bots/{self.endpoint_name}/feedback', self._feedback, methods=['POST'])





class BaseBotWithLocalDb(BaseBot):
    def __init__(self, db_util: DbUtil = None, json_directory='conversations', **kwargs):
        super().__init__(**kwargs)
        if db_util:
            self.db_util = db_util
        else:
            if 'MONGO_URI' in os.environ:
                self.db_util = MongoUtil()
                try:
                    self.db_util.create_index_if_not_exists(self.bot_id, 'sender_id')
                    self.db_util.create_index_if_not_exists(self.bot_id, 'recipient_id')
                except Exception as e:
                    print('Failed to create indexes with exception: ', e)
                
            else:
                self.db_util = JsonUtil(bot_id=self.bot_id, json_directory=json_directory)
    
    def clear_message_history(self, request: ClearMessageHistoryRequest):
        self.db_util.clear_chat_history(self.bot_id, request.user_id)
    def save_chat_message(self, message: TheMessage):
        self.db_util.save_chat_message(self.bot_id, message)
        return

    def feedback(self, message_id: str, rating: float) -> None:
        self.db_util.rate_message(self.bot_id, message_id, rating)
        pass

    def get_message_history(self, user_id:str, limit:int=10, before_ts:float=None, descending:bool=True) -> List[TheMessage]:
        messages = self.db_util.get_chat_messages(bot=self.bot_id, user_id=user_id,limit=limit, before_ts=before_ts)
        if not descending:
            messages = list(reversed(messages))
        return messages


class RegisteredBaseBot(BaseBot):
    def __init__(self, bot_id, bot_token, price: int = 0, icon_path: str = None, **kwargs):
        super().__init__(price, icon_path, bot_id, **kwargs)
        self.bot_token = bot_token
        self.url = os.environ['FRIENDLY_BACKEND_ENDPOINT']
        self.registered = True

    def charge_credits(self, message_id:str) -> bool:
        url = self.url + '/bots/charge_credits'
        d = { 'message_id': message_id }
        headers = {"Authorization": f"Bearer {self.bot_token}" }
        resp = requests.post(url, json=d, headers=headers)
        if resp.status_code == 200:
            return True
        else:
            return False

    def get_message_history(self, user_id:str, limit:int=10, before_ts:float=None, descending:bool=True) -> List[TheMessage]:
        url = self.url + '/messages/get_message_history'
        d = {
            'user_id': user_id,
            'bot_id': self.bot_id,
            'before_ts': before_ts,
            'limit': limit,
        }
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        resp = requests.post(url, json=d, headers=headers)
        assert resp.status_code < 300, f'Error retrieving messages with status code {resp.status_code}'
        messages = resp.json().get('messages', [])
        if not descending:
            messages = list(reversed(messages))
        messages = [TheMessage.parse_obj(msg) for msg in messages]
        return messages
    def save_chat_message(self, message: TheMessage):
        url = self.url + '/messages/add_message'
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        resp = requests.post(url, json=message.dict(), headers=headers)
        assert resp.status_code < 300, f'Error saving message with status code {resp.status_code}'
        pass

    def clear_message_history(self, request: ClearMessageHistoryRequest):
        url = self.url + '/messages/clear_message_history'
        headers = {"Authorization": f"Bearer {self.bot_token}"}
        resp = requests.post(url, json=request.dict(), headers=headers)
        assert resp.status_code < 300, f'Error saving message with status code {resp.status_code}'
        return {}


