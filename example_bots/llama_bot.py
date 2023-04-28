from basebot import BaseBotWithLocalDb, TheMessage, MessageWrapper
from llama_cpp import Llama

LLAMA_CONDITONING = "Transcript of a dialog, where the User interacts with an Assistant named Bob. Bob is helpful, kind, honest, good at writing, and never fails to answer the User's requests immediately and with precision.\n\nUser:What's the capital of France?\nBob:The capital of France is Paris.\n"

class LlamaBot(BaseBotWithLocalDb):
    
    def respond(self, message: MessageWrapper) -> TheMessage:
        msg = message
        if msg.get_text():
            context_messages = self.get_message_context(message, limit=5, descending=False)
            # messages in most recent first order 
            txt = LLAMA_CONDITONING
            for msg in context_messages:
                if msg.get_sender_id() == message.get_sender_id():
                    txt += f"User:{msg.get_text()}\n"
                else:
                    txt += f"Bob:{msg.get_text()}\n"
            txt += f"User:{message.get_text()}\n"
            llm = Llama(model_path="path/to/llama/7B/ggml-model-q4_0.bin")
            output = llm(txt, max_tokens=32, stop=["User:", "\n"], echo=True)
            response_text = output['choices'][0]['text']
            response_text = response_text[len(txt):].strip().replace('Bob:', '')
            resp_msg = self.get_message_to(user_id=msg.get_sender_id())
            resp_msg.set_text(response_text)
            return resp_msg.get_message()
        return {}



