"""Utility functions for interacting with Yahoo Finance"""

import pandas as pd
from yahooquery import Ticker


def get_stock_data(tickers: list, period: str, interval: str):
    """Get stock data for a list of tickers."""

    client = Ticker(tickers, asynchronous=True)
    df = client.history(period=period, interval=interval).reset_index()
    print(f"Yahoo client returned {len(df)} rows, with {df.symbol.nunique()} symbols. Cleaning data...")

    numeric_cols = ["open", "close", "low", "high", "volume"]
    df[numeric_cols] = df[numeric_cols].round(3).astype("string")

    df = df.rename(columns={"date": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)

    df["symbol"] = df["symbol"].str.replace(".ax", "", regex=False)

    return df[["symbol", "timestamp", "open", "high", "low", "close", "volume"]]
