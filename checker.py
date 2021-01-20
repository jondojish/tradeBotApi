import requests
import json
import os
import boto3
from time import sleep
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("API_TOKEN") or os.getenv("API_TOKEN")
ACCOUNT_ID = os.environ.get("ACCOUNT_ID") or os.getenv("ACCOUNT_ID")

AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME") or os.getenv("AWS_BUCKET_NAME")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.getenv(
    "AWS_SECRET_ACCESS_KEY"
)
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID") or os.getenv(
    "AWS_ACCESS_KEY_ID"
)


def check_orders():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    with open("id_file.txt", "wb") as f:
        s3.download_fileobj(
            AWS_BUCKET_NAME, "id_log.txt", f
        )  # download id_log.txt from s3 to new id_log.txt file
    with requests.Session() as s:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": f"application/json",
        }
        s.headers = headers
        curr_ids = []
        with open("id_file.txt") as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                if len(line) > 0:
                    order_id1, order_id2 = line.split(",")
                    URL = f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT_ID}/orders"
                    r = s.get(URL)
                    for order in r.json()["orders"]:
                        curr_ids.append(order["id"])
                    if order_id1 not in curr_ids and order_id2 in curr_ids:
                        s.put(f"{URL}/{order_id2}/cancel")
                        lines[lines.index(line)] = None
                    elif order_id2 not in curr_ids and order_id1 in curr_ids:
                        s.put(f"{URL}/{order_id1}/cancel")
                        lines[lines.index(line)] = None
                    elif order_id2 not in curr_ids and order_id1 not in curr_ids:
                        lines[lines.index(line)] = None
        new_text = []
        for id_str in lines:
            if id_str is not None:
                new_text.append(id_str)
        new_text = "\n".join(new_text)
        with open("id_file.txt", "w") as f:
            f.write(new_text)
        s3.upload_file(
            "id_file.txt", AWS_BUCKET_NAME, "id_log.txt"
        )  # upload id_file.txt to s3 s id_log.txt which overwrites
    print("succesfully checked orders")


if __name__ == "__main__":
    check_orders()
