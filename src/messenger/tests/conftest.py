"""Conftest for messenger tests."""

from datetime import datetime

import pandas as pd

import pytest


@pytest.fixture
def prices_dataframe() -> pd.DataFrame:

    dates = [datetime(2020, 1, 1), datetime(2020, 1, 2), datetime(2020, 1, 3), datetime(2020, 1, 4)]
    symbols = ["ABC", "DEF", "GHI", "JKL"]
    return pd.DataFrame(
        {
            "date": dates*4,
            "symbol": symbols*4,
        }
    )
