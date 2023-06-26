"""The main handler function which sends a stock report to discord"""

import os
from base64 import b64decode
from time import perf_counter
import json

import fire

# pylint: disable=import-error
from utils.daily_report import create_discord_report
from utils.price_alert import create_price_alert
from utils.utils import import_prices_from_bigquery
from utils.yahoo import get_stock_prices

PROJECT_ID = os.environ.get("PROJECT_ID")
WEBHOOK = os.environ["WEBHOOK"]
PRICES = os.environ["PRICES"]

#############
## Handler ##
#############


def main(event=None, context=None):
    """Handler function which sends reports/notifications to discord"""

    if set(event.keys()) == {"method"}:  # Invoked manually.
        pass
    else:  # Invoked via pubsub.
        event = json.loads(b64decode(event["data"]).decode("utf-8"))

    print("Importing prices from BigQuery...")
    historical_prices = import_prices_from_bigquery(PROJECT_ID, PRICES)
    print("Data import success! Creating Discord report...")

    if event["method"] == "daily-report":
        print("Method called: daily-report")
        create_discord_report(WEBHOOK, historical_prices)

    if event["method"] == "price-check":
        print("Method called: price-check")
        symbols = [f"{ii}.ax" for ii in historical_prices["symbol"].unique()]
        current_prices = get_stock_prices(symbols)
        create_price_alert(WEBHOOK, historical_prices, current_prices)

    return


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    fire.Fire(main)
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
