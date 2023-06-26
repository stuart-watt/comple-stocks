"""Utility functions for interacting with Yahoo Finance"""

import pandas as pd
from yahooquery import Ticker


def get_stock_prices(tickers: list) -> pd.DataFrame:
    """Get stock price for a list of tickers."""

    print("Fetching current stock prices...")
    client = Ticker(tickers, asynchronous=True)

    df = pd.DataFrame(client.financial_data).T.reset_index(names=["symbol"])
    print(
        f"Yahoo client returned prices for {df.symbol.nunique()} symbols. Cleaning data..."
    )

    df = df[["symbol", "currentPrice"]]

    invalid_prices = ~pd.to_numeric(df["currentPrice"], errors="coerce").notnull()
    print(f"Invalid prices found: {df[invalid_prices]}")
    df = df[~invalid_prices]

    df["symbol"] = df["symbol"].str.replace(".ax", "", regex=False)
    df["currentPrice"] = pd.to_numeric(df["currentPrice"], errors="coerce")

    return df[["symbol", "currentPrice"]]
