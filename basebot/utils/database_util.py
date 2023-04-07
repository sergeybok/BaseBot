import os 
import pymongo
from bson import ObjectId
from typing import Optional, List
import json, time

from basebot.models.the_message import TheMessage

USER_ID = 'user_id'
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
        criteria = { USER_ID: { CONTAINS: [name, user_id] }}
        if before_ts is not None:
            criteria[TS] = { LESS_THAN: before_ts }
        messages = []
        for msg_dict in self.mongo.db[name].find(criteria).sort(TS, pymongo.DESCENDING).limit(limit):
            messages.append(TheMessage.parse_obj(msg_dict))
        return messages

