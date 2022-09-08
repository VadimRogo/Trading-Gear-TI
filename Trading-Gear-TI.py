import logging
import requests
import json, time, math, random

from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KEY = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

Coins = ["BTCUSDT", "ETHUSDT"]

class MainProcesses():
    
    def CollectData(self, KEY):
        global price
        data = requests.get(KEY).json()
        price = float(data['price'])

def PrintSomethingElse(update, context):
    global KEY
    for i in Coins:
        if  update.message.text == "Check price of {}".format(i):
            
            KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(i)
            x = MainProcesses()
            x.CollectData(KEY)
            update.message.reply_text("Price of {} equal {}".format(i, price))


def main():
    global dp
    updater = Updater("5567192758:AAHfxhHudP5fpGQj6DtmvBgVIwnW4Q9bQpI", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, PrintSomethingElse))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()