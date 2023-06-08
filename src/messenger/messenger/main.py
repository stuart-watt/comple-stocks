"""The main handler function which sends a stock report to discord"""

import os
from base64 import b64decode
from time import perf_counter
import json

# pylint: disable=import-error
from utils.daily_report import create_discord_report
from utils.price_alert import create_price_alert
from utils.utils import import_prices_from_bigquery

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

    if event["method"] == "daily-report":
        print("Importing prices from BigQuery...")
        prices = import_prices_from_bigquery(PROJECT_ID, PRICES, n_days=4)
        print("Data import success! Creating Discord report...")
        create_discord_report(WEBHOOK, prices)
        print("Discord report created and sent successfully!")

    if event["method"] == "price-check":
        print("Sending price check...")
        create_price_alert(WEBHOOK)

##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
