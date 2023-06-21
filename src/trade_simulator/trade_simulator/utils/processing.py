"""Some utilities for processing the data"""

import pandas as pd


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

    df = df.sort_values(by="timestamp")
    df["balance"] = df.groupby(["author_name", "symbol"])["volume"].cumsum()

    return df


def compute_trade_value(trades: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Merge trade data with price data to compute trade value"""

    df = prices.merge(trades, how="left", on=["author_name", "symbol", "timestamp"])

    df[["volume", "cash_volume", "stock_volume", "brokerage"]] = df[
        ["volume", "cash_volume", "stock_volume", "brokerage"]
    ].fillna(0)
    df["balance"] = df.groupby(["author_name", "symbol"])["balance"].ffill()
    df["balance"] = df["balance"].fillna(0)

    df["stock_balance_value"] = df["balance"] * df["price"]
    df["stock_volume_value"] = df["stock_volume"] * df["price"]

    df["cash_flow"] = df["cash_volume"] - df["stock_volume_value"] - df["brokerage"]

    df.loc[df["symbol"] == "$aud", "stock_balance_value"] = 0
    df.loc[df["symbol"] == "$aud", "stock_volume_value"] = 0

    return df


def compute_balances(trades: pd.DataFrame) -> pd.DataFrame:
    """Computes the cash and stock balances for each trader"""

    df = trades[
        [
            "timestamp",
            "author_name",
            "cash_volume",
            "stock_balance_value",
            "stock_volume_value",
            "cash_flow",
        ]
    ].reset_index(drop=True)

    df = df.groupby(["timestamp", "author_name"]).sum().reset_index()
    df["cash_balance"] = (
        df.sort_values(by="timestamp").groupby(["author_name"])["cash_flow"].cumsum()
    )
    df["cash_changes"] = (
        df.sort_values(by="timestamp").groupby(["author_name"])["cash_volume"].cumsum()
    )
    df["total_balance"] = df["cash_balance"] + df["stock_balance_value"]
    df["total_change"] = df["total_balance"] - df["cash_changes"]
    df["pct_change"] = (
        (df["total_balance"] - df["cash_changes"]) / df["cash_changes"] * 100
    )

    return df
