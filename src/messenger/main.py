"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter

import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed

import matplotlib.pyplot as plt

from utils.metrics import get_top_tickers, get_price_change
from utils.utils import import_prices_from_bigquery, get_last_two_dates

PROJECT_ID = os.environ.get("PROJECT_ID")
WEBHOOK = os.environ["WEBHOOK"]
PRICES = os.environ["PRICES"]

#############
## Handler ##
#############


def main(event=None, context=None):
    """Handler function which sends the current date and time to discord"""

    print("Importing prices from BigQuery...")
    prices = import_prices_from_bigquery(PROJECT_ID, PRICES, n_days=3)
    print("Data import success! Creating Discord report...")
    create_discord_report(prices)
    print("Discord report created and sent successfully!")


###############
## Utilities ##
###############


def create_discord_report(prices: pd.DataFrame) -> DiscordEmbed:
    """Create a Discord report"""
    webhook = DiscordWebhook(url=WEBHOOK)

    embed = DiscordEmbed(
        title="Daily Report",
        description="Top-10 performing stocks today!",
        color="03b2f8",
    )
    embed.set_timestamp()

    # filter by shares with value above $0.5
    prices = prices[prices["close"] > 0.5]

    daily_price_changes = get_price_change(prices, *get_last_two_dates(prices))
    top_10_gainers = get_top_tickers(daily_price_changes)
    top_10_losers = get_top_tickers(daily_price_changes, winners=False)

    embed.add_embed_field(
        name=":crown: Top Gainers",
        value=make_gainer_string(top_10_gainers),
        inline=False,
    )
    embed.add_embed_field(
        name=":thumbsdown: Top Losers",
        value=make_gainer_string(top_10_losers),
        inline=False,
    )

    top_gainer = prices[
        prices["symbol"] == top_10_gainers["symbol"].iloc[0]
    ].sort_values(by="timestamp")
    top_loser = prices[prices["symbol"] == top_10_losers["symbol"].iloc[0]].sort_values(
        by="timestamp"
    )

    plt.plot(top_gainer["timestamp"], top_gainer["close"], c="g")
    plt.plot(top_loser["timestamp"], top_loser["close"], c="r")
    plt.savefig("/tmp/test_image.png")
    with open("/tmp/test_image.png", "rb") as f:
        webhook.add_file(file=f.read(), filename="test_image.png")

    embed.set_image(url="attachment://test_image.png")

    webhook.add_embed(embed)
    webhook.execute()


def make_gainer_string(df: pd.DataFrame):
    """Create a string of the top gainers"""
    return "\n".join(
        [
            symbol.ljust(7, "᲼")
            + f"{pct_change:.1%}".ljust(  # uses a unicode character for empty space
                10, "᲼"
            )
            + f"${abs(abs_change):,.3f}"
            for symbol, pct_change, abs_change in zip(
                df["symbol"], df["pct_change"], df["abs_change"]
            )
        ]
    )


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
