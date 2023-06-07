"""Standard utils"""

from datetime import datetime

import pandas as pd


def import_prices_from_bigquery(
    project_id: str, table: str, n_days: int = 7
) -> pd.DataFrame:
    """Import the prices table from BigQuery"""

    query = f"""
        SELECT *, DATE(timestamp) as date 
        FROM `{table}` 
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP, interval {n_days} DAY)
    """

    return pd.read_gbq(
        query=query, project_id=project_id, dialect="standard", use_bqstorage_api=True
    )


def get_daily_close_price(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Get the closing price for a given date"""

    df = df.sort_values("timestamp").drop_duplicates(["symbol", "date"], keep="last")

    return df[df["date"] == date][["symbol", "close"]]


def get_last_two_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Get the maximum two dates in the dataframe"""

    df = df.sort_values("date", ascending=False)
    dates = df["date"].unique()
    return dates[1], dates[0]


def get_minute_date_range():
    """Get a date range for today from 8am to 2pm"""
    today = pd.Timestamp.now(tz="Australia/Perth").date()

    start_time = pd.Timestamp(
        datetime.combine(today, datetime.min.time()), tz="Australia/Perth"
    ) + pd.Timedelta(hours=8)
    end_time = pd.Timestamp(
        datetime.combine(today, datetime.min.time()), tz="Australia/Perth"
    ) + pd.Timedelta(hours=14)

    df = pd.date_range(start=start_time, end=end_time, freq="T")

    return pd.DataFrame({"timestamp": df})


def get_yesterday_close(prices, symbol):
    """Get the closing price for yesterday for a gven symbol"""
    df = prices[prices["date"] < datetime.today().date()]

    df = df[df["symbol"] == symbol].sort_values(by="timestamp")

    return df["close"].iloc[-1]


def get_price_timeseries(prices, symbol):
    """Get a full minute granularity timeseries for a given symbol"""
    timestamps = get_minute_date_range()

    prices_today = prices[prices["date"] == datetime.today().date()]

    df = prices_today[prices_today["symbol"] == symbol].sort_values(by="timestamp")

    df["timestamp"] = df["timestamp"].dt.round("min")
    df = df.drop_duplicates(subset="timestamp")

    df = pd.merge(timestamps, df, on="timestamp", how="left")

    df["close"] = df["close"].ffill()
    df["close"] = df["close"].fillna(get_yesterday_close(prices, symbol))

    return df
