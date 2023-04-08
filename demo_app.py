from basebot import BaseBot, BaseBotWithLocalDb
from basebot import TheMessage, MessageWrapper


## define bot and override necessary functions
class SkepticalBot(BaseBot):
    def receive_message(self, message: TheMessage):
        msg = MessageWrapper(message=message)
        # gets most recent messages if you are using BaseBotWithDb, BaseBotWithLocalDb, or you overrode your own get_message_history function
        #    this version gets empty list
        previous_messages = self.get_message_history(msg.get_user_id(), limit=5)
        response_text = 'Really? You think ' + msg.get_text() + '?'
        response_msg = MessageWrapper(user_id=self.name)
        response_msg.set_text(response_text)
        self.save_chat_message(response_msg.get_message())
        return response_msg.get_message()


# initialize the bot, or bots
bot = SkepticalBot()

# Start the bot 
app = BaseBot.start_app(bot)

# you can provide as many bots as you'd like as arguments
#    to this function as long as they are all different classes
# example:
# app = BaseBot.start_app(bot, other_bot, other_other_bot)

