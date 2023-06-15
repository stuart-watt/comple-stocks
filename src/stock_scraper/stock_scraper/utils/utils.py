"""Standard utils"""

import pandas as pd
import pandas_gbq


def read_from_bg(
    project_id: str, table: str
) -> pd.DataFrame:
    """Import the prices table from BigQuery"""

    return pd.read_gbq(
        query=f"SELECT * FROM `{table}`", 
        project_id=project_id, 
        dialect="standard", 
        use_bqstorage_api=True
    )


def load_to_bg(project_id: str, df: pd.DataFrame, table: str, mode: str, api_method="load_csv"):
    """Load data to BQ."""

    print(f"Loading to {table} with mode={mode}")
    pandas_gbq.to_gbq(
        df,
        table,
        project_id=project_id,
        if_exists=mode,
        progress_bar=False,
        api_method=api_method,
    )
    print("Loaded data to BQ successfully.")


def save_data_to_gcs(df: pd.DataFrame, uri: str):
    """Saves data to GCS."""

    print(f"Loading to {uri}...")
    df.to_json(uri, orient="records", lines=True)
    print("Saved data to GCS successfully.")
