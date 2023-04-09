import os 
import pymongo
from bson import ObjectId
from typing import Optional, List
import json, time

from ..models.the_message import TheMessage

USER_ID = 'user_id'
TO_USER_ID = 'user_id'
TS = 'timestamp'
MESSAGE_ID = 'message_id'

SET = '$set'
LESS_THAN = '$le'
CONTAINS = '$in'

class MongoUtil:
    def __init__(self):
        self.mongo = pymongo.MongoClient(os.environ['MONGO_URI'], retryWrites=False, connect=False)
        pass

    def save_chat_message(self, name:str, message:TheMessage) -> None:
        self.mongo.db[name].update_one({ MESSAGE_ID: message.message_id }, { SET: message.dict()}, upsert=True)

    def get_chat_messages(self, name:str, user_id:str, limit:int=5, before_ts=None) -> List[TheMessage]:
        from_criteria = { USER_ID: user_id }
        to_criteria = { TO_USER_ID: user_id }
        if before_ts is not None:
            from_criteria[TS] = { LESS_THAN: before_ts }
            to_criteria[TS] = { LESS_THAN: before_ts }
        messages = []
        for msg_dict in self.mongo.db[name].find(from_criteria).sort(TS, pymongo.DESCENDING).limit(limit):
            messages.append(TheMessage.parse_obj(msg_dict))
        for msg_dict in self.mongo.db[name].find(to_criteria).sort(TS, pymongo.DESCENDING).limit(limit):
            messages.append(TheMessage.parse_obj(msg_dict))
        messages = sorted(messages, key=lambda m: m.timestamp, reverse=True)[:limit]
        return messages

