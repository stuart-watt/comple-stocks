"""Some utilities for processing the data"""

import pandas as pd


def round_timestamps_up_to_next_market_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Sets any trades outside of market hours to the opening of the next day"""

    # Check if timestamp falls outside the range 00:00-06:00
    mask = ~df["timestamp_exact"].dt.strftime("%H:%M").between("00:00", "06:00") | (
        df["timestamp_exact"].dt.weekday >= 5
    )

    # Adjust timestamps for each day outside the range 00:00-06:00
    df.loc[mask & (df["timestamp_exact"].dt.weekday < 4), "timestamp"] += pd.DateOffset(
        days=1
    )  # Mon-Thur
    df.loc[
        mask & (df["timestamp_exact"].dt.weekday == 4), "timestamp"
    ] += pd.DateOffset(
        days=3
    )  # Fri
    df.loc[(df["timestamp_exact"].dt.weekday == 5), "timestamp"] += pd.DateOffset(
        days=2
    )  # Sat
    df.loc[(df["timestamp_exact"].dt.weekday == 6), "timestamp"] += pd.DateOffset(
        days=1
    )  # Sun
    df.loc[mask, "timestamp"] = df.loc[mask, "timestamp"].dt.floor("D")

    return df


def process_discord_messages(messages: pd.DataFrame):
    """A utility to convert the Discrod messages into ASX trades"""

    df = messages[["id", "timestamp", "content", "author"]].reset_index(drop=True)

    authors = df["author"].apply(pd.Series)[["id", "username"]]

    df["author_id"] = authors["id"].values
    df["author_name"] = authors["username"].values

    df = df.drop(columns=["author"])

    df["content"] = df["content"].str.lower()

    df = df[df["content"].str.startswith(("buy", "sell", "add", "subtract"))]

    df[["action", "volume", "symbol"]] = df["content"].str.split(" ", expand=True)

    df["volume"] = pd.to_numeric(df["volume"])

    df.loc[df["action"].isin(["sell", "subtract"]), "volume"] *= -1

    df["stock_volume"] = df["volume"]
    df["cash_volume"] = df["volume"]
    df["brokerage"] = 0
    df.loc[~df["action"].isin(["sell", "buy"]), "stock_volume"] = 0
    df.loc[df["action"].isin(["sell", "buy"]), "cash_volume"] = 0
    df.loc[df["action"].isin(["sell", "buy"]), "brokerage"] = 10

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)
    df["timestamp_exact"] = df["timestamp"]
    df["timestamp"] = df["timestamp"].dt.round("min")

    df = round_timestamps_up_to_next_market_hour(df)

    return df
