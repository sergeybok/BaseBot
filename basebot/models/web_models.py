from pydantic import BaseModel
from typing import Optional, List

from .the_message import TheMessage


class ClearMessageHistoryRequest(BaseModel):
    user_id: str

class MessageHistoryRequest(BaseModel):
    user_id: str
    before_ts: Optional[float] = None
    limit: Optional[int] = 10

class MessageHistoryRequestWithBot(MessageHistoryRequest):
    bot_id: str


class MessageHistoryResponse(BaseModel):
    messages: List[TheMessage]

class AboutResponse(BaseModel):
    name: str
    bot_id: str
    icon: Optional[str] 
    description: Optional[str]
    registered: Optional[bool] = False 
    price: Optional[int] = 0

class TemplateRequest(BaseModel):
    user_id: str

class Template(BaseModel):
    preview: str
    text: str

class TemplateResponse(BaseModel):
    templates: Optional[List[Template]] = None




