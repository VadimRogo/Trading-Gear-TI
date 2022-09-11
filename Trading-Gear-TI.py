import logging
import requests
import json, time, math, random
import re


from binance.client import Client
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
key = 'T4ZfheSMEw9zpet4HrDWg5NXoL7j4WrOdLl9pEObwByXYVslFK2Yman9cbAVIxwt'
secret = '7aHcuPBXfrqbIJ6AYe3ckav1Rh1G9GY59g0BBzJ6rjIZ7smvcwDi327CSdvy9IYg'
logger = logging.getLogger(__name__)
client = Client(key, secret)
tikets = []
class Processes():

    def TiketProcess(price, quantity, symbol, type):
        time = datetime.now().strftime("%H:%M:%S")
        global Tikets
        x = {
            'time' : time,
            'price' : price,
            'symbol' : symbol,
            'quantity' : quantity,
            'type' : type,
            'sold' : False
        }
        tikets.append(x)

    def SellProcess(price, quantity, symbol):
        #Making Sell and check if system make error
        try:    
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity = quantity
                )

            Processes.TiketProcess(price, quantity, symbol, 'Sell')
        except Exception as inst:
            print(inst)

    def BuyProcess(price, quantity, symbol):
        #Making Buy and check if system give error
        try:
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
                )
            
            Processes.TiketProcess(price, quantity, symbol, 'Buy')
            print("Was bouth {}".format(symbol))
        except Exception as inst:
            print(inst)

                
                





KEY = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
Coins = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "KNCUSDT", "DOGEUSDT", "USDT", "BTC", "ETH", "LTC", "KNC", "DOGE"]
class MainProcesses():
    
    def CollectData(self, KEY):
        global price
        data = requests.get(KEY).json()
        price = float(data['price'])

def OperationWithCoins(update, context):
    global KEY
    global UserText, ReplyText
    UserText = update.message.text
    ReplyText = update.message.reply_text
    x = MainProcesses()
    if any(ext in UserText for ext in Coins):
        for Coin in Coins:
            if  "Check price" in UserText and Coin in UserText:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(Coin)
                x.CollectData(KEY)
                ReplyText("Price of {} equal {}".format(Coin, price))
            
            if  "Buy" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[-1]) >= 10:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(Coin)
                x.CollectData(KEY)
                quantity = round(float(re.findall(r'\d+', UserText)[-1]) / price, 5)
                symbol = Coin
                Processes.BuyProcess(price, quantity, symbol)

            if  "Sell" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[-1]) >= 10:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(Coin)
                x.CollectData(KEY)
                quantity = round(float(re.findall(r'\d+', UserText)[-1]) / price, 5)
                symbol = Coin
                Processes.SellProcess(price, quantity, symbol)
            
            if "Balance" in UserText and Coin in UserText:
                Balance = float(client.get_asset_balance(asset=Coin)['free'])
                ReplyText("Your balance {} is {}".format(Coin, Balance))

    if "Something" in UserText:
        ReplyText("Something")

            
            



def main():
    global dp
    updater = Updater("5567192758:AAHfxhHudP5fpGQj6DtmvBgVIwnW4Q9bQpI", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, OperationWithCoins))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()