import oandapyV20
import oandapyV20.endpoints.orders as orders
import requests
import json
import sys
import os
import boto3
from dotenv import load_dotenv
from time import sleep
from Trade import Trade
from checker import check

API_TOKEN = os.environ.get("API_TOKEN") or os.getenv("API_TOKEN")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID") or os.getenv("ACCOUNT_ID")
ACCOUNT_ID = os.environ.get("AWS_BUCKET_NAME") or os.getenv("AWS_BUCKET_NAME")

client = oandapyV20.API(access_token=API_TOKEN)


def create_orders(market):
    s3 = boto3.client("s3")
    spreads = {}
    r = requests.get("https://www.live-rates.com/rates")
    rates_data = r.json()
    print(rates_data)
    for curr in rates_data:
        if curr["currency"] == "EUR/USD":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["EUR_USD"] = round(ask * 10000 - bid * 10000, 5)
        if curr["currency"] == "GBP/USD":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["GBP_USD"] = round(ask * 10000 - bid * 10000, 5)
        if curr["currency"] == "EUR/JPY":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["EUR_JPY"] = round(ask * 100 - bid * 100, 5)
        if curr["currency"] == "USD/JPY":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["USD_JPY"] = round(ask * 100 - bid * 100, 5)
        if curr["currency"] == "XAU/USD":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["XAU_USD"] = round(ask * 10 - bid * 10, 5)
        if curr["currency"] == "US30":
            ask = float(curr["ask"])
            bid = float(curr["bid"])
            spreads["US30_USD"] = round(ask - bid, 5)
    print()
    print(spreads)
    spread = spreads[market]

    with requests.Session() as s:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": f"application/json",
        }
        s.headers = headers

        URL = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}"
        r = s.get(URL)
        print(r)
        capital = float(r.json()["account"]["marginAvailable"])

        params = {"count": 1}

        URL = f"https://api-fxpractice.oanda.com/v3/instruments/{market}/candles"
        r = s.get(URL, params=params)
        print(r)
        print(r.json())
        openP = float(r.json()["candles"][0]["mid"]["c"])

        URL = f"https://api-fxpractice.oanda.com/v3/instruments/GBP_USD/candles"
        r = s.get(URL, params=params)
        print(r)
        print(r.json())
        USD_rate = float(r.json()["candles"][0]["mid"]["c"])

        URL = f"https://api-fxpractice.oanda.com/v3/instruments/GBP_JPY/candles"
        r = s.get(URL, params=params)
        print(r)
        print(r.json())
        JPY_rate = round(float(r.json()["candles"][0]["mid"]["c"]) / 100, 5)

        rates = {"USD": USD_rate, "JPY": JPY_rate}

    trade_info = Trade(market, openP, capital, spread, rates)

    buy_data = {"order": {}}
    order = buy_data["order"]
    order["price"] = str(trade_info.buyP()[0])
    order["stopLossOnFill"] = {"timeInForce": "GTC"}
    order["stopLossOnFill"]["price"] = str(trade_info.buy_sl()[0])
    order["takeProfitOnFill"] = {"price": str(trade_info.buy_tp())}
    order["timeInForce"] = "GTC"
    order["instrument"] = trade_info.market
    order["units"] = str(trade_info.units())
    order["type"] = "MARKET_IF_TOUCHED"
    order["positionFill"] = "DEFAULT"

    print(buy_data)

    r = orders.OrderCreate(ACCOUNT_ID, data=buy_data)
    client.request(r)
    print(r.response)
    print()
    id_1 = r.response["orderCreateTransaction"]["id"]

    sell_data = {"order": {}}
    order = sell_data["order"]
    order["price"] = str(trade_info.sellP())
    order["stopLossOnFill"] = {"TimeInForce": "GTC"}
    order["stopLossOnFill"]["price"] = str(trade_info.sell_sl())
    order["takeProfitOnFill"] = {"price": str(trade_info.sell_tp())}
    order["timeInForce"] = "GTC"
    order["instrument"] = trade_info.market
    order["units"] = str(-1 * trade_info.units())
    order["type"] = "MARKET_IF_TOUCHED"
    order["positionFill"] = "DEFAULT"

    r = orders.OrderCreate(ACCOUNT_ID, data=sell_data)
    client.request(r)
    print(r.response)
    id_2 = r.response["orderCreateTransaction"]["id"]

    with open("id_file.txt", "wb") as f:
        s3.download_fileobj(
            "orderids", "id_log.txt", f
        )  # download id_log.txt from s3 to new id_log.txt file
    with open("id_file.txt", "a") as f:
        f.write(f"\n{id_1},{id_2}")
    s3.upload_file(
        "id_file.txt", "orderids", "id_log.txt"
    )  # upload id_file.txt to s3 s id_log.txt which overwrites


markets = sys.argv[1:]
for market in markets:
    create_orders(market)
