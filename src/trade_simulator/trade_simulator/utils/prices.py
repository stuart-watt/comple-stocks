"""Utilities for importing price data into the service"""

from datetime import datetime
import pandas as pd


def create_timestamp_spine(start_date: str):
    """Creates a complete timestamp spine between trading hours"""

    index = pd.date_range(start=start_date, end=str(datetime.today()), freq="T")

    filtered_index = index[
        (index.strftime("%H:%M:%S") >= "00:00:00")
        & (index.strftime("%H:%M:%S") <= "06:00:00")
    ]

    filtered_index = filtered_index[filtered_index.weekday < 5]

    return pd.DataFrame({"timestamp": filtered_index})


def create_price_spine(messages: pd.DataFrame, prices: pd.DataFrame):
    """Craetes a spine for all symbols and timestamps"""
    times = create_timestamp_spine(str(messages["timestamp"].dt.date.min()))
    symbols = messages[["author_name", "symbol"]].drop_duplicates()

    spine = symbols.merge(times, how="cross")

    spine = spine.merge(prices, how="left", on=["symbol", "timestamp"])
    spine = spine.sort_values(by="timestamp")
    spine["price"] = spine.groupby(["author_name", "symbol"])["price"].ffill()
    spine["price"] = spine.groupby(["author_name", "symbol"])["price"].bfill()
    spine["price"] = spine["price"].fillna(1)

    return spine.sort_values(by=["timestamp", "symbol", "author_name"])


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
            close as price 
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

    df = df.drop_duplicates()

    return create_price_spine(trades, df)
