# BaseBot

To install 

    pip install git+https://github.com/sergeybok/BaseBot.git


## To download mobile app

Provide links to iOS and Android app.

## To implement a bot

You should probably setup your database first by following the instructions below so that you can actually run the bot. But I'll descrbe how to implement a bot here for visibility. Also don't create and run your bot from inside this repo, it's better to install the library and run it in a separate folder/repo.

This is an example of a `demo_app.py` file that is found in this repo that simply creates an interface between the app, your server, and OpenAI's ChatGPT API. *Warning:* this requires an API key from OpenAI.

``` python
from basebot import BaseBotWithLocalDb, BaseBot
from basebot import TheMessage, MessageWrapper
import openai

class ChatGPTBot(BaseBotWithLocalDb):
    def respond(self, message: MessageWrapper) -> MessageWrapper:
        if message.get_text():
            # get previous messages, oldest message first
            context_messages = self.get_message_context(message, limit=5, descending=False) 
            chatgpt_messages = []
            for msg in context_messages:
                if msg.get_sender_id() == message.get_sender_id() and msg.get_text():
                    chatgpt_messages.append({'role': 'user', 'content': msg.get_text()})
                elif msg.get_text():
                    chatgpt_messages.append({'role': 'assistant', 'content': msg.get_text()})
            # add current message last
            chatgpt_messages.append({'role': 'user', 'content': message.get_text()})
            # Call OpenAI API (this will fail without API key)
            chatgpt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=chatgpt_messages)
            response_text = chatgpt_response['choices'][0]['message']['content']
            resp_message = self.get_message_to(user_id=message.get_sender_id())
            resp_message.set_text(response_text)
            return resp_message
        return {}

app = BaseBot.start_app(ChatGPTBot())
```

If you want to use something other than MongoDB look into overriding `get_message_history()`, or if you want to change for example how the context messages are retrieved (the current implementations just calls `get_message_history()` and makes sure the current message isn't in the batch) you can easily override the methods in your bot implementation, e.g. maybe you want to do search instead of getting most recent. Look at `class Basebot` for more details.

There are also a few functions that are recommended to override for any bot:  

+ help() function which is automatically triggered by sending help on the device
  + this is also customizable but you gotta delve into the BaseBot class more deeply
+ templates() function which defines helpful keywords or phrases in the top view of the chat 
  + e.g. for Stable Diffusion you just hit that text bubble to fill in "High quality, HD, masterpiece, etc..." instead of rewriting it everytime


### To start your bot

Uvicorn or gunicorn 

## To setup local db

Install and launch MongoDB by following the instructions in the [official MongoDB documentation](https://www.mongodb.com/docs/manual/administration/install-community/).

After you start your mongodb server, you have to set the environment variable to point to it. BaseBot expects the variable to be `MONGO_URI`. I recommend appending it to your bash_profile (if on Mac) or bashrc (if on Linux). The following line appends the default mongodb port (27017) to the Linux profile script which is by default `~/.bashrc`. And the `source` line re-runs the bash profile so that you don't need to start a new terminal shell for the environment variable to be present.

```
echo 'export MONGO_URI=mongodb://localhost:27017' >> ~/.bashrc
source ~/.bashrc
```


### Ubuntu Linux (summary of the official documentation)

Run the following commands to install:

```
sudo apt-get update
sudo apt-get install -y mongodb-org
```

Run the following commands to start the server:

```
sudo systemctl start mongod     # You need to run this command each time you reboot your computer
sudo systemctl status mongod    # Check that it's running
```

If there are errors e.g. `Failed to start mongod.service: Unit mongod.service not found.` Run this before re-running the commands above:

```
sudo systemctl daemon-reload
```


## To ngrok your server (Ubuntu Linux)

REFERENCE: https://www.slingacademy.com/article/deploying-fastapi-on-ubuntu-with-nginx-and-lets-encrypt/


