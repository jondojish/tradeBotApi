import requests
import dotenv
import os

dotenv.load_dotenv()
API_TOKEN = os.environ.get("API_TOKEN")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")
market = "US30_USD"
with requests.Session() as s:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    s.headers = headers
    # only lates candle

    # Get current spread
    multipliers = {"EUR_JPY": 100, "USD_JPY": 100, "XAU_USD": 100, "US30_USD": 1}
    params = {"instruments": market}
    URL = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/pricing"
    r = s.get(URL, params=params)
    ask = float(r.json()["prices"][0]["asks"][0]["price"]) * multipliers.get(
        market, 10000
    )
    bid = float(r.json()["prices"][0]["bids"][0]["price"]) * multipliers.get(
        market, 10000
    )
    spread = float(ask) - float(bid)
    spread = round(spread, 1)
    print(spread)

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
    spread = spreads["XAU_USD"]
    print(f"d: {spread}")