"""Utility functions for interacting with the ASX website"""

import pandas as pd


def get_listed_companies(url: str) -> pd.DataFrame:
    """Get a list of all companies currently listed on the ASX."""

    df = pd.read_csv(url)
    df["Listing date"] = pd.to_datetime(df["Listing date"], format="%d/%m/%Y")
    df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors="coerce")
    columns_renamed = {
        "ASX code": "symbol",
        "Company name": "name",
        "GICs industry group": "GIC",
        "Listing date": "listing_date",
        "Market Cap": "market_cap",
    }
    return df.rename(columns=columns_renamed)
