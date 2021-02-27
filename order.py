import requests
import json
import sys
import os
import boto3
from dotenv import load_dotenv
from time import sleep
from Trade import Trade
from checker import check_orders

API_TOKEN = os.environ.get("API_TOKEN")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")

AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")


def create_order(market):
    # Gets current spreads
    spreads = {}
    r = requests.get("https://www.live-rates.com/rates")
    rates_data = r.json()
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
    spread = spreads[market]

    # Creates request session (so i dont have to enter headers every time)
    with requests.Session() as s:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        }
        s.headers = headers

        URL = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}"
        r = s.get(URL)
        capital = float(r.json()["account"]["marginAvailable"])

        # only lates candle
        params = {"count": 1}

        # Gets Rate for market requested
        URL = f"https://api-fxpractice.oanda.com/v3/instruments/{market}/candles"
        r = s.get(URL, params=params)
        openP = float(r.json()["candles"][0]["mid"]["c"])

        # Gets USD rate and JPY rate (increases accuracy of Trade)
        URL = f"https://api-fxpractice.oanda.com/v3/instruments/GBP_USD/candles"
        r = s.get(URL, params=params)
        USD_rate = float(r.json()["candles"][0]["mid"]["c"])

        URL = f"https://api-fxpractice.oanda.com/v3/instruments/GBP_JPY/candles"
        r = s.get(URL, params=params)
        JPY_rate = round(float(r.json()["candles"][0]["mid"]["c"]) / 100, 5)

        rates = {"USD": USD_rate, "JPY": JPY_rate}

        trade_info = Trade(market, openP, capital, spread, rates)

        # New url for creating orders
        URL = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/orders"

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

        r = s.post(URL, data=json.dumps(buy_data))
        id_1 = r.json()["orderCreateTransaction"]["id"]

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

        r = s.post(URL, data=json.dumps(sell_data))
        id_2 = r.json()["orderCreateTransaction"]["id"]

    # creates s3 connection
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )

    # download id_log.txt from s3 to new id_log.txt file
    with open("id_file.txt", "wb") as f:
        s3.download_fileobj(AWS_BUCKET_NAME, "id_log.txt", f)

    # new order id's are appended
    with open("id_file.txt", "a") as f:
        f.write(f"\n{id_1},{id_2}")

    # updated log file is uploaded to s3
    s3.upload_file("id_file.txt", AWS_BUCKET_NAME, "id_log.txt")
    print(f"successfully ordered {market}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        raise SystemExit("Must pass a market via the command line")
    markets = sys.argv[1:]
    for market in markets:
        create_order(market)
