
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
    user_id: str
    to_user_id: str
    message_id: str


class MessageWrapper:
    def __init__(self, message:TheMessage = None, user_id:str ='', to_user_id:str=''):
        if message:
            self.message = message
        else:
            assert user_id is not None and user_id != '', 'Make sure to provide user_id for new message'
            assert to_user_id is not None and to_user_id != '', 'Make sure to provide to_user_id for new message'
            self.message = TheMessage(contents=MessageContents(), timestamp=time.time(), user_id=user_id, to_user_id=to_user_id, message_id=str(uuid.uuid4()))

    def get_message(self) -> TheMessage:
        return self.message
    def get_text(self) -> str:
        return self.message.contents.text
    def set_text(self, text):
        self.message.contents.text = text
    def get_images_pil(self) -> Image:
        return [b64_string_to_img(img_str) for img_str in self.message.message.get(IMAGE, [])]
    def get_images_b64(self) -> list:
        return self.message.contents.image
    def set_images_pil(self, images):
        self.message.contents.image = [img_to_b64_string(img) for img in images]
    def set_images_b64(self, images:list):
        self.message.contents.image = images
    def get_user_id(self):
        return self.message.user_id
    def set_user_id(self, user_id:str):
        self.message.to_user_id = user_id
    def get_to_user_id(self):
        return self.message.user_id
    def set_to_user_id(self, user_id:str):
        self.message.to_user_id = user_id
    def get_message_id(self):
        return self.message.message_id
    def set_message_id(self, msg_id:str):
        self.message.message_id = msg_id





