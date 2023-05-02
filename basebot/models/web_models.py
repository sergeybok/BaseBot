from pydantic import BaseModel
from typing import Optional, List

from .the_message import TheMessage


class ParamCompenent(BaseModel):
    """
    Parameters shown in the app
      type_value in ['float', 'int', 'str']
      if you define both min_value and max_value it's a slider
    name: str (should be unique)
    default_value: str
    type_value: str
    min_value: float/int
    max_value: float/int
    """
    name: str
    default_value: str
    type_value: str # float, int, str
    min_value: Optional[float]
    max_value: Optional[float]


class InterfaceParamsResponse(BaseModel):
    params: List[ParamCompenent]


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




