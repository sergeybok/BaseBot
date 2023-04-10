
from typing import Optional, List
from pydantic import BaseModel
from ..utils.image_utils import b64_string_to_img, img_to_b64_string
from PIL import Image
import uuid, time



class MessageContents(BaseModel):
    text: Optional[str] = None
    image: Optional[List[str]] = [] 


class TheMessage(BaseModel):
    contents: MessageContents
    timestamp: float
    sender_id: str
    recipient_id: str
    message_id: str
    extras: Optional[dict] = {}


class MessageWrapper:
    def __init__(self, message:TheMessage = None, sender_id:str ='', recipient_id:str=''):
        if message:
            self.message = message
        else:
            assert sender_id is not None and sender_id != '', 'Make sure to provide sender_id for new message'
            assert recipient_id is not None and recipient_id != '', 'Make sure to provide recipient_id for new message'
            self.message = TheMessage(contents=MessageContents(), timestamp=time.time(), sender_id=sender_id, recipient_id=recipient_id, message_id=str(uuid.uuid4()))

    def get_message(self) -> TheMessage:
        return self.message
    def get_text(self) -> str:
        return self.message.contents.text
    def set_text(self, text):
        self.message.contents.text = text
    def get_images_pil(self) -> list:
        if self.message.contents.image:
            return [b64_string_to_img(img_str) for img_str in self.message.contents.image]
        return None
    def get_images_b64(self) -> list:
        return self.message.contents.image
    def set_images_pil(self, images):
        self.message.contents.image = [img_to_b64_string(img) for img in images]
    def set_images_b64(self, images:list):
        self.message.contents.image = images
    def get_sender_id(self):
        return self.message.sender_id
    def set_sender_id(self, user_id:str):
        self.message.sender_id = user_id
    def get_recipient_id(self):
        return self.message.recipient_id
    def set_recipient_id(self, user_id:str):
        self.message.recipient_id = user_id
    def get_message_id(self):
        return self.message.message_id
    def set_message_id(self, msg_id:str):
        self.message.message_id = msg_id
    def get_extras(self) -> dict:
        return self.message.extras
    def get_from_extras(self, key:str):
        return self.message.extras.get(key)
    def set_extras(self, extras:dict):
        self.message.extras = extras
    def set_extra_property(self, key:str, value:str):
        self.message.extras[key] = value





