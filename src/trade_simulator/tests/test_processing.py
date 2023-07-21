"""Test the trade simulator processing functions"""

import pandas as pd

from trade_simulator.utils.processing import round_timestamps_up_to_next_market_hour


def test_round_timestamps_up_to_next_market_hour():
    """Test that timestamps are rounded correctly to appropriate market hours"""

    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2023-06-21 23:45:00",
                    "2023-06-22 01:30:00",
                    "2023-06-22 05:15:00",
                    "2023-06-23 02:30:00",
                    "2023-06-23 07:45:00",
                    "2023-06-24 03:30:00",
                    "2023-06-25 16:00:00",
                    "2023-06-25 16:00:00",
                    "2023-06-26 03:00:00",
                ]
            )
        }
    )
    df["timestamp_exact"] = df["timestamp"]
    print("df", df)

    rounded_df = round_timestamps_up_to_next_market_hour(df)

    expected_df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2023-06-22 00:00:00",
                    "2023-06-22 01:30:00",
                    "2023-06-22 05:15:00",
                    "2023-06-23 02:30:00",
                    "2023-06-26 00:00:00",
                    "2023-06-26 00:00:00",
                    "2023-06-26 00:00:00",
                    "2023-06-26 00:00:00",
                    "2023-06-26 03:00:00",
                ]
            )
        }
    )

    expected_df["timestamp_exact"] = df["timestamp_exact"]

    print("rounded_df", rounded_df)
    print("expected_df", expected_df)

    pd.testing.assert_frame_equal(rounded_df, expected_df)
