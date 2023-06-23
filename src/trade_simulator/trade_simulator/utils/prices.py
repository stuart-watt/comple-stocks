"""Utilities for importing price data into the service"""

import pandas as pd


def import_prices_from_bigquery(
    project_id: str, table: str, trades: pd.DataFrame
) -> pd.DataFrame:
    """Import the prices table from BigQuery"""

    symbols = '", "'.join(trades["symbol"].unique())
    timestamp = trades["timestamp"].min().date()

    query = f"""
        SELECT 
            LOWER(symbol) as symbol, 
            timestamp, 
            price 
        FROM `{table}` 
        WHERE LOWER(symbol) in ("{symbols}")
        AND timestamp >= "{timestamp}"
    """

    df = pd.read_gbq(
        query=query, project_id=project_id, dialect="standard", use_bqstorage_api=True
    )

    df["timestamp"] = df["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)
    df["timestamp"] = df["timestamp"].dt.round("min")

    df["price"] = df["price"].astype(float)

    symbols = trades[["author_name", "symbol"]].drop_duplicates()

    return df.merge(symbols, how="left", on=["symbol"]).sort_values(
        by=["timestamp", "author_name", "symbol"]
    )
