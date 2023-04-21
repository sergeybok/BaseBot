from basebot import BaseBot, TheMessage, MessageWrapper
from typing import List, Dict


class BaseBotSkeleton(BaseBot):
    def __init__(self, icon_path: str = None) -> None:
        super().__init__(icon_path=icon_path)

    def help(self) -> str:
        raise NotImplementedError("TODO implement this function")

    def get_message_history(self, user_id: str, limit=10, before_ts=None, descending: bool = True) -> List[TheMessage]:
        raise NotImplementedError("TODO implement this function")

    def respond(self, message: MessageWrapper) -> MessageWrapper:
        raise NotImplementedError("TODO implement this function")

    def save_chat_message(self, message: TheMessage) -> None:
        raise NotImplementedError("TODO implement this function")
