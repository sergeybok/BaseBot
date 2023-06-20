# Bot API

Let $URL be your bot url, e.g. 'http://localhost:8000/bots/MyBot'. The following are the available endpoints:

## Required

### $URL/about GET

Is the endpoint the application uses to get information about the bot, including the name and the profile picture. 

The response is the AboutResponse object, defined as below:

```
AboutResponse 
{
    name: str
    bot_id: str
    icon: Optional[str] 
    description: Optional[str]
    registered: Optional[bool] = False 
    price: Optional[int] = 0
}
```

### $URL/respond POST with json payload

Both the expected payload and the output are the same type of object, TheMessage object:

```
TheMessage 
{
    timestamp: float
    sender_id: str
    recipient_id: str
    message_id: str
    extras: Optional[dict] = {}
    contents: {'text': Optional[str], 'image': Optional[List[str]] }
}
```

All IDs are UUIDv4 by default in BaseBot.


### $URL/history POST with json payload

It takes the user_id, the limit number of messages, and the before timestep (to create pagination by passing the timestamp of the oldest message visible on screen). The expected payload json should look like this:

```
MessageHistoryRequest
{
    user_id: str
    before_ts: Optional[float] = None
    limit: Optional[int] = 10
}
```

And the response is a dict containing a list of $limit messages in descending order (most recent message first). It is a json object that looks like this:

```
MessageHistoryResponse
{
    messages: List[TheMessage]
}
```


## Optional

The following endpoints are not necessary for simple chatbot UI, but are helpful for more specific use cases.

### $URL/clear_message_history POST with json payload

The following is the input and it outputs an empty json.

```
ClearMessageHistoryRequest
{
    'user_id': str
}
```


### $URL/templates POST with json payload

The templates are keywords that show up at the top of the app that make it easier so you don't have to retype commonly used phrases. The input looks like this:

```
TemplateRequest
{
    user_id: str
}
```

And the response looks like this:

```
TemplateResponse
{
    templates: [
        { 'preview': str, 'text': str },
        ...
    ]
}
```

### $URL/interface_params GET

The interface params are the bot settings seen in the app in the top right corner of the chat window.

```
InterfaceParamsResponse 
{
    params: List[ParamCompenent]
}

ParamCompenent
{
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
}
```
