"""This file contains the main function for the stock_scraper package."""

import os
from time import perf_counter
from base64 import b64decode
from datetime import datetime
import json

import pandas as pd
import pandas_gbq

from yahooquery import Ticker

PROJECT_ID = os.environ.get("PROJECT_ID")
URL = os.environ.get("LISTED_COMPANIES_URL")
COMPANIES_TABLE = os.environ.get("COMPANIES_TABLE")
HOURLY_PRICES_TABLE = os.environ.get("HOURLY_PRICES_TABLE")
MINUTELY_PRICES_TABLE = os.environ.get("MINUTELY_PRICES_TABLE")
BUCKET = os.environ.get("BUCKET")

##################
## Main Handler ##
##################


def main(event=None, context=None):
    """GCF handler function to decoed the event data and route to different method"""

    print("Fetching register of listed ASX companies")
    listed_companies = get_listed_companies(URL)
    print(f"Fetching complete! Found {listed_companies.symbol.nunique()} companies.")

    tickers = [f"{ii}.ax" for ii in listed_companies["symbol"]]

    if set(event.keys()) == {"method"}:  # Invoked manually.
        pass
    else:  # Invoked via pubsub.
        event = json.loads(b64decode(event["data"]).decode("utf-8"))

    if event["method"] == "ingest-minutely":
        scrape_prices(
            tickers, table=MINUTELY_PRICES_TABLE, interval="1m", gcs_save=True
        )

    if event["method"] == "ingest-hourly":
        load_to_bg(listed_companies, COMPANIES_TABLE, "replace")
        scrape_prices(tickers, table=HOURLY_PRICES_TABLE, interval="1h")


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
        SELECT MAX(timestamp) as timestamp
        FROM {table}
    """
    latest_prices = pd.read_gbq(query, project_id=PROJECT_ID, dialect="standard")
    latest_timestamp = latest_prices["timestamp"].iloc[0].tz_localize(None)

    if latest_timestamp is not pd.NaT:
        print(f"Last timestamp found in {table} is {latest_timestamp}")
        period = "1d" if interval == "1m" else "1w"

    else:
        print(f"No latest timestamp found in {table}")
        period = "1d" if interval == "1m" else "2y"

    print(
        f"Fetching prices for listed companies in period {period} (interval {interval})"
    )
    stock_data = get_stock_data(tickers, period, interval)

    if latest_timestamp is not pd.NaT:
        stock_data = stock_data[stock_data["timestamp"] > latest_timestamp]

    if len(stock_data) > 0:
        print(f"Success! Returned {len(stock_data)} rows.")

        load_to_bg(stock_data, table, bq_mode)

        if gcs_save:
            save_data_to_gcs(
                stock_data,
                f"gs://{BUCKET}/prices/ingest_timestamp={int(datetime.now().timestamp())}.jsonlines",
            )

    else:
        print("No price data found!")


###############
## Utilities ##
###############


def get_listed_companies(url: str) -> pd.DataFrame:
    """Get a list of all companies currently listed on the ASX."""

    df = pd.read_csv(url)
    df["Listing date"] = pd.to_datetime(df["Listing date"], format="%d/%m/%Y")
    df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors="coerce")
    columns_renamed = {
        "ASX code": "symbol",
        "Company name": "name",
        "GICs industry group": "GIC",
        "Listing date": "listing_date",
        "Market Cap": "market_cap",
    }
    return df.rename(columns=columns_renamed)


def get_stock_data(tickers: list, period: str, interval: str):
    """Get stock data for a list of tickers."""

    client = Ticker(tickers, asynchronous=True)
    df = client.history(period=period, interval=interval).reset_index()

    numeric_cols = ["open", "close", "low", "high", "volume"]
    df[numeric_cols] = df[numeric_cols].round(3).astype("string")

    df = df.rename(columns={"date": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)

    df["symbol"] = df["symbol"].str.replace(".ax", "", regex=False)

    return df[["symbol", "timestamp", "open", "high", "low", "close", "volume"]]


def load_to_bg(df: pd.DataFrame, table: str, mode: str, api_method="load_csv"):
    """Load data to BQ."""

    print(f"Loading to {table} with mode={mode}")
    pandas_gbq.to_gbq(
        df,
        table,
        project_id=PROJECT_ID,
        if_exists=mode,
        progress_bar=False,
        api_method=api_method,
    )
    print("Loaded data to BQ successfully.")


def save_data_to_gcs(df: pd.DataFrame, uri: str):
    """Saves data to GCS."""

    print(f"Loading to {uri}...")
    df.to_json(uri, orient="records", lines=True)
    print("Saved data to GCS successfully.")


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
