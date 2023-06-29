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
    """Loads a dataframe to BigQuery"""

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
