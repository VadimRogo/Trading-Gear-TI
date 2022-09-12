from ast import While
import logging
import requests
import json, time, math, random
import re
import asyncio
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
TakeProfitStopLossTikets = []
TakeProfitTikets = []
StopLossTikets = []

class TiketProcesses():

    def TiketProcess(price, quantity, symbol, type):
        time = datetime.now().strftime("%H:%M:%S")
        global tikets
        order = {
            'time' : time,
            'price' : price,
            'symbol' : symbol,
            'quantity' : quantity,
            'type' : type,
            'sold' : False
        }
        tikets.append(order)

    def TiketProcessTakeProfit(price, quantity, symbol, TakeProfitPercent):
        global TakeProfitTikets
        time = datetime.now().strftime('%H:%M:%S')
        endprice = price + price / 100 * TakeProfitPercent
        order = {
            'time' : time,
            'symbol' : symbol,
            'quantity' : quantity,
            'price' : price,
            'endprice' : endprice,
            'percent' : TakeProfitPercent,
            'sold' : False
        }
        TakeProfitTikets.append(order)

    def TiketProcessTakeProfitStopLoss(price, quantity, symbol, TakeProfitPercent, StopLossPercent):
        global TakeProfitStopLossTikets
        time = datetime.now().strftime('%H:%M:%S')
        TakeProfitEndPrice = price + price / 100 * TakeProfitPercent
        StopLossEndPrice = price - price / 100 * StopLossPercent
        order = {
            'time' : time,
            'symbol' : symbol,
            'quantity' : quantity,
            'price' : price,
            'TakeProfitEndPrice' : TakeProfitEndPrice,
            'TakeProfitPercent' : TakeProfitPercent,
            'StopLossEndPrice' : StopLossEndPrice,
            'StopLossPercent' : StopLossPercent,
            'sold' : False
        }
        TakeProfitStopLossTikets.append(order)
        print("ALL WORK")
    
    def TiketProcessStopLoss(price, quantity, symbol, StopLossPercent):
        global StopLossTikets
        time = datetime.now().strftime('%H:%M:%S')
        StopLossEndPrice = price - price / 100 * StopLossPercent
        order = {
            'time' : time,
            'symbol' : symbol,
            'quantity' : quantity,
            'price' : price,
            'StopLossEndPrice' : StopLossEndPrice,
            'StopLossPercent' : StopLossPercent,
            'sold' : False
        }
        StopLossTikets.append(order)

class BuyAndSellProcesses():

    def SellProcessTiket(price, quantity, symbol, tiket):
        #Making Sell and check if system make error
        global TakeProfitStopLossTikets, TakeProfitTikets, StopLossTikets
        try:    
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity = quantity
                )
            tiket['sold'] = True
        except Exception as inst:
            print(inst)
        
    def SellProcess(price, quantity, symbol):
        #Making Sell and check if system make error
        global TakeProfitStopLossTikets, TakeProfitTikets, StopLossTikets
        try:    
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity = quantity
                )
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
        except Exception as inst:
            print(inst)
    
    def BuyProcessWithTakeProfit(price, quantity, symbol, TakeProfitPercent):
        try:
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
                )
            TiketProcesses.TiketProcessTakeProfit(price, quantity, symbol, TakeProfitPercent)
        except Exception as inst:
            print(inst)
    
    def BuyProcessWithStopLoss(price, quantity, symbol, StopLossPercent):
        try:
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
                )
            TiketProcesses.TiketProcessStopLoss(price, quantity, symbol, StopLossPercent)
        except Exception as inst:
            print(inst)
    

    def BuyProcessWithTakeProfitAndStopLoss(price, quantity, symbol, StopLossPercent, TakeProfitPercent):
        try:
            order = client.create_order(
                symbol = symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
                )
            TiketProcesses.TiketProcessTakeProfitStopLoss(price, quantity, symbol, TakeProfitPercent, StopLossPercent)
        except Exception as inst:
            print(inst)

KEY = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
Coins = ["USDT", "BTC", "ETH", "LTC", "KNC", "DOGE"]
class MainProcesses():
    
    def CollectData(self, KEY):
        global price
        data = requests.get(KEY).json()
        price = float(data['price'])

    async def WalkingForObservTP():
        for i in TakeProfitTikets:
            KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(i['symbol'])
            x = MainProcesses()
            x.CollectData(KEY)
            symbol = i['symbol']
            quantity = i['quantity']
            if i['TakeProfitEndPrice'] <= price and i['sold'] != False:
                BuyAndSellProcesses.SellProcessTiket(price, quantity, symbol, i)
            await asyncio.sleep(10)

    async def WalkingForObservSL():
        if len(StopLossTikets) >= 1:
            for i in StopLossTikets:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(i['symbol'])
                x = MainProcesses()
                x.CollectData(KEY)
                symbol = i['symbol']
                quantity = i['quantity']
                if i['StopLossEndPrice'] >= price and i['sold'] != False:
                    BuyAndSellProcesses.SellProcessTiket(price, quantity, symbol, i)
                await asyncio.sleep(10)

    async def WalkingForObservTPSL():
        if len(TakeProfitStopLossTikets) >= 1:
            for i in TakeProfitStopLossTikets:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}".format(i['symbol'])
                x = MainProcesses()
                x.CollectData(KEY)
                symbol = i['symbol']
                quantity = i['quantity']
                if i['StopLossEndPrice'] >= price and i['sold'] != False:
                    BuyAndSellProcesses.SellProcessTiket(price, quantity, symbol, i)
                elif i['TakeProfitEndPrice'] <= price and i['sold'] != False:
                    BuyAndSellProcesses.SellProcessTiket(price, quantity, symbol, i)
                await asyncio.sleep(10)
                print("TakeProfit ", i['TakeProfitEndPrice'])
                print("StopLOSS ", i['StopLossEndPrice'])
                print("Walking for observ")

def OperationWithCoins(update, context):
    
    global KEY
    global UserText, ReplyText
    UserText = update.message.text
    ReplyText = update.message.reply_text
    x = MainProcesses()
    if any(ext in UserText for ext in Coins):
        for Coin in Coins:
            if  "Check price" in UserText and Coin in UserText:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                ReplyText("Price of {} equal {}".format(Coin, price))
            
            if  "Buy" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[0]) >= 10 and len(UserText) < 13:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                dollars = float(re.findall(r'\d+', UserText)[0])
                quantity = round(dollars / price, 5)
                symbol = Coin + "USDT"
                BuyAndSellProcesses.BuyProcess(price, quantity, symbol)

            if  "Sell" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[0]) >= 10:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                dollars = float(re.findall(r'\d+', UserText)[0])
                quantity = round(dollars / price, 5)
                symbol = Coin + "USDT"
                BuyAndSellProcesses.SellProcess(price, quantity, symbol)
            
            if "Balance" in UserText and Coin in UserText:
                Balance = client.get_asset_balance(asset=Coin)['free']
                ReplyText("Your balance {} is {}".format(Coin, Balance))

            if "Buy" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[0]) >= 10 and "take profit" in UserText and float(re.findall(r'\d+', UserText)[1]) >= 0 and len(UserText) <= 30:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                dollars = float(re.findall(r'\d+', UserText)[0])
                TakeProfitpercent = float(re.findall(r'\d+', UserText)[1])
                quantity = round(dollars / price, 5)
                symbol = Coin + "USDT"
                BuyAndSellProcesses.BuyProcessWithTakeProfit(price, quantity, symbol, TakeProfitpercent)

            if "Buy" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[0]) >= 10 and "stop loss" in UserText and float(re.findall(r'\d+', UserText)[1]) >= 0 and len(UserText) <= 30:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                dollars = float(re.findall(r'\d+', UserText)[0])
                StopLossPercent = float(re.findall(r'\d+', UserText)[1])
                quantity = round(dollars / price, 5)
                symbol = Coin + "USDT"
                BuyAndSellProcesses.BuyProcessWithStopLoss(price, quantity, symbol, StopLossPercent)

            if "Buy" in UserText and Coin in UserText and len(re.findall(r'\d+', UserText)) != 0 and float(re.findall(r'\d+', UserText)[0]) >= 10 and "take profit" in UserText and float(re.findall(r'\d+', UserText)[1]) >= 0 and "stop loss" in UserText and float(re.findall(r'\d+', UserText)[2]) > 0 and len(UserText) <= 42:
                KEY = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT".format(Coin)
                x.CollectData(KEY)
                dollars = float(re.findall(r'\d+', UserText)[0])
                TakeProfitpercent = float(re.findall(r'\d+', UserText)[1])
                StopLossPercent = float(re.findall(r'\d+', UserText)[2])
                quantity = round(dollars / price, 5)
                symbol = Coin + "USDT"
                BuyAndSellProcesses.BuyProcessWithTakeProfitAndStopLoss(price, quantity, symbol, StopLossPercent, TakeProfitpercent)       

    if "Something" in UserText:
        ReplyText("Something")

    if len(TakeProfitTikets) >= 1:
        asyncio.run(MainProcesses.WalkingForObservTP())
    if len(StopLossTikets) >= 1:
        asyncio.run(MainProcesses.WalkingForObservSL())
    if len(TakeProfitStopLossTikets) >= 1:
        asyncio.run(MainProcesses.WalkingForObservTPSL())


def main():
    global dp
    updater = Updater("5567192758:AAHfxhHudP5fpGQj6DtmvBgVIwnW4Q9bQpI", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, OperationWithCoins))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()