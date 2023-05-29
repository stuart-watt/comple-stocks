"""Standard utils"""

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

    return pd.read_gbq(query=query, project_id=project_id, dialect="standard")


def get_daily_close_price(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Get the closing price for a given date"""

    df = df.sort_values("timestamp").drop_duplicates(["symbol", "date"], keep="last")

    return df[df["date"] == date][["symbol", "close"]]


def get_last_two_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Get the maximum two dates in the dataframe"""

    df = df.sort_values("date", ascending=False)
    dates = df["date"].unique()
    return dates[1], dates[0]
