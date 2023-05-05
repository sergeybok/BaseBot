import os 
import pymongo
from pymongo import DESCENDING
from bson import ObjectId
from typing import Optional, List
import json, time
import json
import os
from typing import Dict, List

from ..models.the_message import TheMessage

USER_ID = 'sender_id'
TO_USER_ID = 'recipient_id'
TS = 'timestamp'
MESSAGE_ID = 'message_id'

SET = '$set'
LESS_THAN = '$lt'
CONTAINS = '$in'


class DbUtil:
    def __init__(self) -> None:
        pass

    def save_chat_message(self, bot:str, message:TheMessage) -> None:
        raise NotImplementedError("Abstract method")

    def get_chat_messages(self, bot:str, user_id:str, limit:int=5, before_ts=None) -> List[TheMessage]:
        raise NotImplementedError("Abstract method")
    
    def clear_chat_history(self, bot:str, user_id:str) -> None:
        raise NotImplementedError("Abstract method")

class MongoUtil(DbUtil):
    def __init__(self):
        super().__init__()
        self.mongo = pymongo.MongoClient(os.environ['MONGO_URI'], retryWrites=False, connect=False)
        pass

    def save_chat_message(self, bot:str, message:TheMessage) -> None:
        self.mongo.db[bot].update_one({ MESSAGE_ID: message.message_id }, { SET: message.dict()}, upsert=True)
    def clear_chat_history(self, bot: str, user_id: str):
        from_criteria = { USER_ID: user_id }
        to_criteria = { TO_USER_ID: user_id }
        self.mongo.db[bot].delete_many(from_criteria)
        self.mongo.db[bot].delete_many(to_criteria)
    def get_chat_messages(self, bot:str, user_id:str, limit:int=5, before_ts=None) -> List[TheMessage]:
        from_criteria = { USER_ID: user_id }
        to_criteria = { TO_USER_ID: user_id }
        if before_ts is not None:
            from_criteria[TS] = { LESS_THAN: before_ts }
            to_criteria[TS] = { LESS_THAN: before_ts }
        messages = []
        for msg_dict in self.mongo.db[bot].find(from_criteria).sort(TS, pymongo.DESCENDING).limit(limit):
            messages.append(TheMessage.parse_obj(msg_dict))
        for msg_dict in self.mongo.db[bot].find(to_criteria).sort(TS, pymongo.DESCENDING).limit(limit):
            messages.append(TheMessage.parse_obj(msg_dict))
        messages = sorted(messages, key=lambda m: m.timestamp, reverse=True)[:limit]
        return messages

    def create_index_if_not_exists(self, bot:str, field_name:str):

        # # Get a reference to the specified collection
        collection = self.mongo.db[bot]

        # Check if the index already exists
        existing_indexes = collection.index_information()
        if f"{field_name}_-1_timestamp_-1" in existing_indexes:
            print("Index already exists!")
            return

        # Create the index if it doesn't exist
        result = collection.create_index([(field_name, DESCENDING), ("timestamp", DESCENDING)])
        print("Index created successfully!")





class JsonUtil(DbUtil):
    def __init__(self, bot_id:str, json_directory:str):
        super().__init__()
        self.messages: Dict[List[Dict]] = {} # Dictionary user_id -> message list. Each message is a dictionary version of TheMessage
        self.bot_id = bot_id
        if not os.path.exists(json_directory):
            os.makedirs(json_directory)
        filename = bot_id + '_messages.json'
        self.json_name = os.path.join(json_directory, filename)
        self.load_messages()

    def save_messages(self):
        with open(self.json_name, 'w') as f:
            json.dump(self.messages, f)

    def load_messages(self):
        if not os.path.exists(self.json_name):
            data = {}
            with open(self.json_name, 'w') as f:
                json.dump(data, f)
        with open(self.json_name, 'r') as f:
            self.messages = json.load(f)
    def clear_chat_history(self, bot: str, user_id: str) -> None:
        del self.messages[user_id]
        self.save_messages()
    def get_message_history(self,
                            user_id:str,
                            limit=10,
                            before_ts=None,
                            descending:bool=True) -> List[Dict]:
        filtered_messages = []
        if user_id not in self.messages:
            self.messages[user_id] = []
        n = 0
        for message in reversed(self.messages[user_id]):
            if (message['sender_id'] == user_id or message['recipient_id'] == user_id):
                if (before_ts is None or message['timestamp'] < before_ts):
                    filtered_messages.append(message)
                    n += 1
                    if n >= limit:
                        break
        if (descending):
            filtered_messages = sorted(filtered_messages,
                                       key=lambda k: k['timestamp'],
                                       reverse=True)
        else:
            filtered_messages = sorted(filtered_messages, key=lambda k: k['timestamp'])
        return filtered_messages[:limit]
    
    def get_chat_messages(self, bot:str, user_id:str, limit:int=5, before_ts=None) -> List[TheMessage]:
        o = self.get_message_history(user_id, limit, before_ts)
        return [TheMessage.parse_obj(m) for m in o]

    def _save_chat_message(self, bot_name, message: Dict):
        if message['sender_id'] == bot_name:
            user_id = message['recipient_id']
        else:
            user_id = message['sender_id']
        if user_id not in self.messages:
            self.messages[user_id] = []
        self.messages[user_id].append(message)
        self.save_messages()

    def save_chat_message(self, name:str, message:TheMessage) -> None:
        self._save_chat_message(name, message.dict())
