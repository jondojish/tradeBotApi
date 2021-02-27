import oandapyV20
import oandapyV20.endpoints.orders as orders
import requests
import json
import sys
import os
import boto3
import pytz
from dotenv import load_dotenv
from time import sleep
from datetime import datetime
from order import create_order
from checker import check_orders

load_dotenv()

API_TOKEN = os.environ.get("API_TOKEN")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID")

AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")


is_tradable = {
    "GBP_USD": True,  # applies to EUR_USD as well
    "USD_JPY": True,
    "EUR_JPY": True,
    "US30_USD": True,
    "XAU_USD": True,
}


def create_correct_order(curr_time):

    if curr_time != "00:00":
        is_tradable["XAU_USD"] = True
    if curr_time != "06:00":
        is_tradable["GBP_USD"] = True
    if curr_time != "07:00":
        is_tradable["EUR_JPY"] = True
    if curr_time != "12:00":
        is_tradable["USD_JPY"] = True
    if curr_time != "14:30":
        is_tradable["US30_USD"] = True

    if curr_time == "00:00" and is_tradable["XAU_USD"]:
        create_order("XAU_USD")
        is_tradable["XAU_USD"] = False
    if curr_time == "06:00" and is_tradable["GBP_USD"]:
        create_order("GBP_USD")
        create_order("EUR_USD")
        is_tradable["GBP_USD"] = False
    if curr_time == "07:00" and is_tradable["EUR_JPY"]:
        create_order("EUR_JPY")
        is_tradable["EUR_JPY"] = False
    if curr_time == "12:00" and is_tradable["USD_JPY"]:
        create_order("USD_JPY")
        is_tradable["USD_JPY"] = False
    if curr_time == "14:30" and is_tradable["US30_USD"]:
        create_order("US30_USD")
        is_tradable["US30_USD"] = False


# While loop runs every interval seconds
interval = 3
# Check orders every check interval seconds
check_interval = 600
# Aids check interval
time_count = 0

# chech time every inverval secs but checks orders every check interval seconds
while True:
    time_count += interval
    London_time = datetime.now(pytz.timezone("Europe/London"))
    curr_time = London_time.strftime("%H:%M")
    day = London_time.today().weekday()
    hour = int(London_time.strftime("%H"))
    if (
        (day == 4 and hour < 22) or (day == 6 and hour >= 22) or (day < 4 and day >= 0)
    ):  # checks if market is open
        create_correct_order(curr_time)
        if time_count % check_interval == 0:
            check_orders()
            print("Orders Checked")
    else:
        # reset time count for when market opens
        time_count = 0
        print("Markets closed, Nothing to check")
    sleep(interval)
