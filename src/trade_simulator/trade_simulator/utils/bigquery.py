"""Utilities for interfacing with BigQuery"""

import pandas_gbq
import pandas as pd


def read_from_bg(project_id: str, table: str) -> pd.DataFrame:
    """Read a table from BigQuery"""
    return pd.read_gbq(
        query=f"SELECT * FROM `{table}`",
        project_id=project_id,
        dialect="standard",
        use_bqstorage_api=True,
    )


def load_to_bg(
    project_id: str, df: pd.DataFrame, table: str, mode: str, api_method="load_csv"
):
    """Append messages to BQ without duplication."""

    print(f"Loading {len(df)} rows to {table} with mode={mode}")
    pandas_gbq.to_gbq(
        df,
        table,
        project_id=project_id,
        if_exists=mode,
        progress_bar=False,
        api_method=api_method,
    )
    print("Loaded data to BQ successfully.")


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
