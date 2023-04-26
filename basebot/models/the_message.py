
from typing import Optional, List
from pydantic import BaseModel
from ..utils.image_utils import b64_string_to_img, img_to_b64_string
from PIL import Image
import uuid, time



class MessageContents(BaseModel):
    text: Optional[str] = None
    image: Optional[List[str]] = [] 


class TheMessageMetadata(BaseModel):
    timestamp: float
    sender_id: str
    recipient_id: str
    message_id: str

class TheMessage(TheMessageMetadata):
    contents: MessageContents
    extras: Optional[dict] = {}


class MessageWrapper:
    """
    BaseBot is the baseclass to make chatbot APIs. Extend the class with your own bot.

    Attributes
    ----------
    message : TheMessage
        the underlying message that gets sent as a response to the /respond request

    Methods
    -------
    __init__(self, message:TheMessage = None, sender_id:str ='', recipient_id:str='') -> None
        Initializes the MessageWrapper. Takes either a TheMessage as input 
          or the sender and recipient, in which case it initializes the rest of the attributes
          automatically: timestamp and message_id
    get_text(self) -> str
        Returns the text contents of the message
    set_text(self, text:str) -> None
        Sets the text contents of the message
    get_images_pil(self) -> List[PIL.Image]
        Returns the images in the message as PIL.Image types
    get_images_b64(self) -> List[str]
        Returns the images in the message as base64 encoded strings
    set_images_pil(self, images) -> None
        Converts the images to base64 strings and sets them in the image contents
    set_images_b64(self) -> None
        Sets the images in the image contents of the message
    get_message(self) -> TheMessage
        Returns the message
    get_sender_id(self) -> str
        Returns the sender_id of the message
    set_sender_id(self, user_id:str) -> None
        Sets the sender_id of the message
    get_recipient_id(self) -> str
        Returns the recipient_id of the message
    set_recipient_id(self, user_id:str) -> None
        Sets the recipient_id of the message
    get_message_id(self) -> str
        Returns the message_id of the message
    set_message_id(self, msg_id:str) -> None
        Sets the message_id of the message
    get_extras(self) -> dict
        Returns the extras dict of the message that could be used for storing any convenient data about it on the message itself
    get_from_extras(self, key:str)
        Returns the specific key from the extras, else returns None
    set_extras(self, extras:dict)
        Sets the extras dictionary of the message. Must be JSON serializable.
    set_extra_property(self, key:str, value:str)
        Sets key value on the extras dict
    """
    def __init__(self, message:TheMessage = None, sender_id:str ='', recipient_id:str=''):
        """
        Initializes the MessageWrapper. Takes either a TheMessage as input 
          or the sender and recipient, in which case it initializes the rest of the attributes
          automatically: timestamp and message_id
        """
        if message:
            self.message = message
        else:
            assert sender_id is not None and sender_id != '', 'Make sure to provide sender_id for new message'
            assert recipient_id is not None and recipient_id != '', 'Make sure to provide recipient_id for new message'
            self.message = TheMessage(contents=MessageContents(), timestamp=time.time(), sender_id=sender_id, recipient_id=recipient_id, message_id=str(uuid.uuid4()))

    def get_message(self) -> TheMessage:
        """
        Returns the underlying JSON serializable TheMessage that gets sent back as a response to a /respond request
        """
        return self.message
    def get_text(self) -> str:
        """
        Returns the text contents of the message
        """
        return self.message.contents.text
    def set_text(self, text:str):
        """
        Sets the text contents of the message
        """
        self.message.contents.text = text
    def get_images_pil(self) -> list:
        """
        Returns the images in the message as PIL.Image types
        """
        if self.message.contents.image:
            return [b64_string_to_img(img_str) for img_str in self.message.contents.image]
        return None
    def get_images_b64(self) -> list:
        """
        Returns the images in the message as base64 encoded strings
        """
        return self.message.contents.image
    def set_images_pil(self, images):
        """
        Converts the images to base64 strings and sets them in the image contents
        """
        self.message.contents.image = [img_to_b64_string(img) for img in images]
    def set_images_b64(self, images:list):
        """
        Sets the images in the image contents of the message
        """
        self.message.contents.image = images
    def get_sender_id(self) -> str:
        """
        Returns the sender_id of the message
        """
        return self.message.sender_id
    def set_sender_id(self, user_id:str):
        """
        Sets the sender_id of the message
        """
        self.message.sender_id = user_id
    def get_recipient_id(self) -> str:
        """
        Returns the sender_id of the message
        """
        return self.message.recipient_id
    def set_recipient_id(self, user_id:str):
        """
        Returns the recipient_id of the message
        """
        self.message.recipient_id = user_id
    def get_message_id(self) -> str:
        """
        Returns the message_id of the message
        """
        return self.message.message_id
    def set_message_id(self, msg_id:str):
        """
        Sets the message_id of the message
        """
        self.message.message_id = msg_id
    def get_extras(self) -> dict:
        """
        Returns the extras dict of the message that could be used for storing any convenient data about it on the message itself
        """
        return self.message.extras
    def get_from_extras(self, key:str):
        """
        Returns the specific key from the extras, else returns None
        """
        return self.message.extras.get(key)
    def set_extras(self, extras:dict):
        """
        Sets the extras dictionary of the message. Must be JSON serializable.
        """
        self.message.extras = extras
    def set_extra_property(self, key:str, value:str):
        """
        Sets key value on the extras dict
        """
        self.message.extras[key] = value





