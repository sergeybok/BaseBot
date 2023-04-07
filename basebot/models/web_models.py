from pydantic import BaseModel
from typing import Optional, List

from basebot.models.the_message import TheMessage


class MessageHistoryRequest(BaseModel):
    user_id: str
    before_ts: Optional[float] = None
    limit: Optional[int] = 10

class MessageHistoryResponse(BaseModel):
    messages: List[TheMessage]

class AboutResponse(BaseModel):
    name: Optional[str]
    icon: Optional[str] 




