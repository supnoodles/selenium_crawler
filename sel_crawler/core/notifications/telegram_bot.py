import telegram

class TelegramBot:
    """
    Uses the python-telegram-bot API
    https://github.com/python-telegram-bot/python-telegram-bot
    """
    def __init__(self, bot_token: str, chat_id: int):
        """
        bot_token : the token bound to your telegram bot
        chat_id : the chat that the bot will use to send messages.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=self.bot_token)
    
    def send_notif(self, product, url):
        """
        As soon as stock becomes available, sends message.
        """
        self.bot.sendMessage(chat_id=self.chat_id,text='{} available at {}'.format(product,url))

    def send_final_notif(self):
        """
        Right before the final payment button, another notification is sent.
        """
        self.bot.sendMessage(chat_id=self.chat_id,text='Filling out Final Details Page')
