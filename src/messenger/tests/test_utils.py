"""Unit tests for the messenger utilities"""

import pandas as pd

from messenger.utils.utils import get_last_two_dates


def test_get_last_two_dates(prices_dataframe):
    """Test that the function returns the last two dates in the dataframe"""

    first, last = [pd.to_datetime(d).strftime("%Y-%m-%d") for d in get_last_two_dates(prices_dataframe)]

    assert (first, last) == ("2020-01-03", "2020-01-04")

