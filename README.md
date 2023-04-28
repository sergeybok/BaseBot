# BaseBot


## What is Friendly AI + BaseBot

Friendly AI is an app that sends and receives messages using the protocol defined in this library. What this means is that once you download the app, you can launch your own instance of a BaseBot bot and be able to communicate with your computer very easily from your phone by just providing the URL of your bot (which is just your local IP address unless you have your own domain). You can also modify the respond() function of the bot such that it does whatever you want. You can hook it up to ChatGPT (code available in scripts). You can hook it up to open source LLMs such as Alpaca, that you are able to run locally or through some other API. You can hook it up to a local instance of Stable Diffusion and generate photos using stable diffusion from your phone. You can easily create wrappers around ChatGPT such as doing some sort of retrieval step or conditioning the ChatGPT conversation with relevant or personal info for your exact needs. You can automate tasks that are specific to you and your machine, and not worry about sharing sensitive or private data because it's all hosted on your own machine.

Basically what Friendly AI and BaseBot allow you to do is easily develop and customize bots that are easily accessible to you, are highly private, and customized exactly to your needs -- without dealing with a lot of the frontend dev, backend dev, App Store/Play Store review process, etc. You can concentrate solely on the interesting problem of what your bot actually does!


To install 

```
pip install git+https://github.com/sergeybok/BaseBot.git
```

### Experimental Quickstart

This currently only has been tested on Mac and Ubuntu Linux. It asks for your bot name and creates bot project directory with a virtualenv, asks for OpenAI key if not present (but this is optional), and ngrok key (also optional), and depending on if you gave an openai key or not, it starts you off with a simple ChatGPT bot, or a WhyBot that has no LLM and just repeats what you said skeptically. Also provides helpful scripts to start and stop bots in the background.

```
curl -sSL "https://raw.githubusercontent.com/sergeybok/BaseBot/main/scripts/basebot_install.sh" >> basebot_install.sh && sh basebot_install.sh
```

## To download mobile app

Available on [iOS App Store](https://apps.apple.com/us/app/friendly-ai/id6447589849). Coming soon to Android Play Store.

## To implement a bot

You should probably setup your database first by [following the instructions below](https://github.com/sergeybok/BaseBot#to-setup-local-db) because without it the bots use json files as storage. But I'll descrbe how to implement a bot here for visibility. Also don't create and run your bot from inside this repo, it's better to install the library and run it in a separate folder/repo.

### The protocol

The main protocol of BaseBot and Friendly AI app is the following class:

``` python
from pydantic import BaseModel
class MessageContents(BaseModel):
    text: Optional[str] = None
    image: Optional[List[str]] = [] 

class TheMessage(BaseModel):
    contents: MessageContents
    timestamp: float
    sender_id: str
    recipient_id: str
    message_id: str
```

Which has the necessary metadata for the communication between the user and the bot. The images are base64 encoded strings. The bot's `id` is by default simply its class name but you can change it if you'd like. However the BaseBot `respond()` function provides you not `TheMessage` but the  `MessageWrapper` class which provides a load of helpful methods. For example, for response messages you use the `self.get_message_to()` method and it initializes all of the metadata and you just need to set the contents only (by calling `set_text` or `set_images`, or both). 

You can, if you so choose, build your own app that receives and sends the same protocol and interface with your BaseBot bot. Or you can build your own version of BaseBot server (in another language for example such as node.js) to interface with the Friendly AI app as long as the `/respond` endpoint both receives and sends back this object:
```
{
    'contents': {'text': 'my text', 'image': []},
    'timestamp': 12456677,
    'sender_id': 'some_id',
    'recipient_id': 'other_id',
    'message_id': 'unique_message_id' 
}
```

Note that in BaseBot as well as Friendly AI app, all IDs are generated with UUID v4.

### The demo app (Vanilla ChatGPT)

This is an example of a `demo_chatgpt.py` file that is found in this repo (in ./scripts) that simply creates an interface between the app, your server, and OpenAI's ChatGPT API. *Warning:* this requires an API key from [OpenAI, see their docs for reference](https://platform.openai.com/docs/api-reference/authentication). You can obviously sub in any other LLM (or any other piece of technology e.g. stable diffusion) whether it's run locally or also an API reference.

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
  + This should provide a helpful message of how to use the bot and what it does.
  + You can remove this functionality by looking into and overriding `_respond()` function. See BaseBot class for more details.
+ templates() function which defines helpful keywords or phrases in the top view of the chat 
  + e.g. for Stable Diffusion you just hit that text bubble to fill in "High quality, HD, masterpiece, etc..." instead of rewriting it everytime

### To add an image

Simply place into your project root directory (same level as your main.py or app.py file) a image with the same name as your bot class name: `ClassName.jpg|png`. BaseBot class also takes `icon_path:str` as a parameter.

### To start your bot

See the scripts `scripts/start_bots.sh`, `scripts/start_bots_background.sh`, and `scripts/stop_bots.sh` for reference. They work with a project started from quickstart and easily allow you to start your bot, and to stop your bot if you started it in the background.

From your directory or repo where you have the above demo_chatgpt.py file, you would start it with the following command:

```
uvicorn demo_chatgpt:app --port 8000 --host 0.0.0.0
```

The uvicorn command expects FILENAME:APPLICATION_VARIABLE_NAME where the FILENAME is without extension and the variable name is the `app = BaseBot.start_app()` variable. See [FastAPI deployment guide for more details](https://fastapi.tiangolo.com/deployment/manually/).

This will now serve your bot on `http://localhost:8000/bots/ChatGPTBot`. In order to get your local address (so that you can connect to it on local network i.e. your phone and computer are on the same wifi) run `python scripts/share_localhost.py` which should print out your local IP address as well as generate a QR code for your local address. You can also pass the `bot_name` to get the exact address of a specific bot, e.g. `python scripts/share_localhost.py --bot_name ChatGPTBot`. If you want to access your bot when you're not on the same network, see the **Ngrok** section below for more details.

## To setup local db

Install and launch MongoDB by following the instructions in the [official MongoDB documentation](https://www.mongodb.com/docs/manual/administration/install-community/).

After you start your mongodb server, you have to set the environment variable to point to it. BaseBot expects the variable to be `MONGO_URI`. I recommend appending it to your bash_profile (if on Mac) or bashrc (if on Linux). The following line appends the default mongodb port (27017) to the Linux profile script which is by default `~/.bashrc`. And the `source` line re-runs the bash profile so that you don't need to start a new terminal shell for the environment variable to be present.

```
echo 'export MONGO_URI=mongodb://localhost:27017' >> ~/.bashrc
source ~/.bashrc
```


### Install & Launch on Ubuntu Linux (summary of docs above)

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

REFERENCE for HTTPS (more secure and so recommended): https://www.slingacademy.com/article/deploying-fastapi-on-ubuntu-with-nginx-and-lets-encrypt/

If you want to access a server running locally on your machine you will need to open up the port on which you are serving your bot. The simplest way to do this is by using ngrok, a tool that creates a secure tunnel to expose your local server to the internet.

1. Download and install ngrok by following the instructions in the [official ngrok documentation.](https://ngrok.com/docs#getting-started-installation) (**Note** that this is done automatically if you say Y in the quickstart, you just need to provide your ngrok key to the script and it sets it up automatically. Alternately, you can also download and run the ./scripts/ngrok_install without running the entire ngrok script but you still need to go to the site and register and get a key)
2. Start your server on any port, we will assume it's port 8000 for commands below
3. Run `ngrok http 8000`
4. Ngrok will generate a unique URL that you can use to access your locally hosted server over the internet. Look for the Forwarding line in the ngrok console output to find the URL. It should look something like this: `Forwarding  http://12345678.ngrok.io -> http://localhost:8000`
5. You can now plug in this URL into the Friendly app and communicate with your bots! **Note** that the URL expected by the app is with the bot class name. So for the demo_app ChatGPTBot it would be something like `http://12345678.ngrok.io/bots/ChatGPTBot`

