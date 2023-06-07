import fire
import pandas as pd

URL = "https://asx.api.markitdigital.com/asx-research/1.0/companies/directory/file"


def get_listed_companies():
    """Get a list of all companies currently listed on the ASX."""

    df = pd.read_csv(URL)
    df["Listing date"] = pd.to_datetime(df["Listing date"], format="%d/%m/%Y")
    df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors="coerce")
    columns_renamed = {
        "ASX code": "symbol",
        "Company name": "name",
        "GICs industry group": "GIC",
        "Listing date": "listing_date",
        "Market Cap": "market_cap",
    }
    print(df.rename(columns=columns_renamed))


if __name__ == "__main__":
    fire.Fire(get_listed_companies)
