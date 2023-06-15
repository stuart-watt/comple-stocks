"""This file contains the main function for the stock_scraper package."""

import os
from time import perf_counter
from base64 import b64decode
from datetime import datetime
import json

import pandas as pd

# pylint: disable=import-error
from utils.utils import read_from_bg, load_to_bg, save_data_to_gcs
from utils.asx import get_listed_companies
from utils.yahoo import get_stock_data

PROJECT_ID = os.environ.get("PROJECT_ID")
URL = os.environ.get("LISTED_COMPANIES_URL")
COMPANIES_TABLE = os.environ.get("COMPANIES_TABLE")
INDICES_TABLE = os.environ.get("INDICES_TABLE")
HOURLY_PRICES_TABLE = os.environ.get("HOURLY_PRICES_TABLE")
MINUTELY_PRICES_TABLE = os.environ.get("MINUTELY_PRICES_TABLE")
HOURLY_INDEX_TABLE = os.environ.get("HOURLY_INDEX_TABLE")
BUCKET = os.environ.get("BUCKET")

##################
## Main Handler ##
##################


def main(event=None, context=None):
    """GCF handler function to decoed the event data and route to different method"""

    if set(event.keys()) == {"method", "interval"}:  # Invoked manually.
        pass
    else:  # Invoked via pubsub.
        event = json.loads(b64decode(event["data"]).decode("utf-8"))

    method = event["method"]
    interval = event["interval"]

    print("Function started, method:", method, "interval:", interval)

    # Fetch symbols
    symbols = fetch_symbols(method)

    # Ingest data
    if method == "index":

        scrape_prices(
            symbols, table=HOURLY_INDEX_TABLE, interval="1h",
        )

    if method == "stock":
        if interval == "1m":
            scrape_prices(
                symbols, table=MINUTELY_PRICES_TABLE, interval="1m", gcs_save=True
            )

        if interval == "1h":
            scrape_prices(symbols, table=HOURLY_PRICES_TABLE, interval="1h")


##################
## Sub-Handlers ##
##################


def fetch_symbols(method: str) -> list:
    """Fetches the symbols to ingest"""
    if method == "listed_companies":
        print("Fetching register of listed ASX companies from ASX")
        listed_entities = get_listed_companies(URL)
        load_to_bg(PROJECT_ID, listed_entities, COMPANIES_TABLE, "replace")
        symbols = [f"{ii}.ax" for ii in listed_entities["symbol"]]

    if method == "index":
        print("Fetching list of ASX indices from BQ")
        listed_entities = read_from_bg(PROJECT_ID, INDICES_TABLE)
        symbols = [f"^A{ii}" for ii in listed_entities["symbol"]]

    if method == "stock":
        print("Fetching register of listed ASX companies from BQ")
        listed_entities = read_from_bg(PROJECT_ID, COMPANIES_TABLE)
        symbols = [f"{ii}.ax" for ii in listed_entities["symbol"]]

    print(f"Fetching complete! Found {len(symbols)} symbols.")

    return symbols


#############
## Scraper ##
#############


def scrape_prices(
    tickers: list, table: str, interval: str = "1h", bq_mode="append", gcs_save=False
):
    """
    Ingests the ASX stock data with a "interval" granularity.
    This function ingests all price data in a certain period
    and writes to BQ with mode="bq_mode".
    If "gcs_save" is True, save data to GCS.
    """

    print(f"Importing latest timestamp from {table} in BQ...")
    query = f"""
        SELECT symbol, MAX(timestamp) as latest_timestamp
        FROM {table} GROUP BY symbol ORDER BY latest_timestamp desc
    """
    latest_prices = pd.read_gbq(query, project_id=PROJECT_ID, dialect="standard")
    if len(latest_prices) > 0:
        latest_prices["latest_timestamp"] = latest_prices[
            "latest_timestamp"
        ].dt.tz_localize(None)
        print(
            f"Last timestamp found in {table} is {latest_prices.latest_timestamp.iloc[0]}"
        )
        period = "1d" if interval == "1m" else "1w"

    else:
        print(f"No latest timestamp found in {table}")
        period = "1d" if interval == "1m" else "2y"

    print(
        f"Fetching prices for listed companies in period {period} (interval {interval})"
    )
    stock_data = get_stock_data(tickers, period, interval)

    if len(stock_data) > 0:
        stock_data = stock_data.merge(latest_prices, on="symbol", how="left")
        stock_data["latest_timestamp"] = stock_data["latest_timestamp"].fillna(
            datetime(2020, 1, 1)
        )
        stock_data = stock_data[
            stock_data["timestamp"] > stock_data["latest_timestamp"]
        ]

        print(f"Success! Returned {len(stock_data)} rows.")

        load_to_bg(
            PROJECT_ID, stock_data.drop(columns="latest_timestamp"), table, bq_mode
        )

        if gcs_save:
            now = int(datetime.now().timestamp())
            save_data_to_gcs(
                stock_data, f"gs://{BUCKET}/prices/ingest_timestamp={now}.jsonlines"
            )

    else:
        print("No price data found!")


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
