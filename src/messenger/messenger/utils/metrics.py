"""Compute standard metrics based on price data"""
from datetime import datetime
import pandas as pd

from .utils import get_daily_close_price


def get_price_change(
    df: pd.DataFrame, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    """Get the price change between two dates"""

    start_price = get_daily_close_price(df, start_date)
    end_price = get_daily_close_price(df, end_date)

    df = pd.merge(start_price, end_price, on="symbol", suffixes=("_start", "_end"))

    df["abs_change"] = df["close_end"] - df["close_start"]
    df["pct_change"] = df["abs_change"] / df["close_start"]

    return df
