"""This file contains the main function for the stock_scraper package."""

import os
from time import perf_counter

import pandas as pd
import pandas_gbq

from yahooquery import Ticker

URL = os.environ.get(
    "LISTED_COMPANIES_URL", 
    "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"
)
COMPANIES_TABLE = os.environ.get("COMPANIES_TABLE", "stocks.listed_companies")
PRICES_TABLE = os.environ.get("PRICES_TABLE", "stocks.prices")
START_DATE = os.environ.get("START_DATE", "2023-01-01")
INTERVAL = os.environ.get("INTERVAL", "1h")

#############
## Handler ##
#############

def main(event=None, context=None):
    """GCF handler function"""

    listed_companies = get_listed_companies()
    pandas_gbq.to_gbq(
        listed_companies,
        COMPANIES_TABLE,
        project_id="stuart-project-1",
        if_exists="replace",
        progress_bar=False
    )

    tickers = [f"{ii}.ax" for ii in listed_companies["symbol"]]

    stock_data = get_stock_data(tickers)

    pandas_gbq.to_gbq(
        stock_data,
        PRICES_TABLE,
        project_id="stuart-project-1",
        if_exists="replace",
        progress_bar=False,
        api_method="load_csv"
    )


###############
## Utilities ##
###############

def get_listed_companies():
    """Get a list of all companies currently listed on the ASX."""

    df = pd.read_csv(URL)
    df["Listing date"] = pd.to_datetime(df["Listing date"], format="%d/%m/%Y")
    df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors='coerce')
    columns_renamed = {
        "ASX code": "symbol", 
        "Company name": "name",
        "GICs industry group": "GIC",
        "Listing date": "listing_date",
        "Market Cap": "market_cap"
    }
    return df.rename(columns=columns_renamed)

def get_stock_data(tickers: list):
    """Get stock data for a list of tickers."""

    client = Ticker(tickers, asynchronous=True)
    df = client.history(start=START_DATE, interval=INTERVAL).reset_index()

    numeric_cols = ["open", "close", "low", "high", "volume"]
    df[numeric_cols] = df[numeric_cols].round(3).astype("string")

    df = df.rename(columns={"date": "timestamp"})
    df["symbol"] = df["symbol"].str.replace(".ax", "", regex=False)

    return df[["symbol", "timestamp", "open", "high", "low", "close"]]


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
