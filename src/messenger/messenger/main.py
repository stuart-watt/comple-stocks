"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter
import pytz

import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed

# pylint: disable=import-error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

from utils.metrics import get_price_change
from utils.utils import (
    import_prices_from_bigquery,
    get_last_two_dates,
    get_yesterday_close,
    get_price_timeseries,
)

PROJECT_ID = os.environ.get("PROJECT_ID")
WEBHOOK = os.environ["WEBHOOK"]
PRICES = os.environ["PRICES"]

#############
## Handler ##
#############


def main(event=None, context=None):
    """Handler function which sends the current date and time to discord"""

    print("Importing prices from BigQuery...")
    prices = import_prices_from_bigquery(PROJECT_ID, PRICES, n_days=4)
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

    daily_price_changes = daily_price_changes.sort_values("pct_change", ascending=False)

    embed.add_embed_field(
        name=":crown: Top Gainers",
        value=make_gainer_string(daily_price_changes.head(10)),
        inline=False,
    )
    embed.add_embed_field(
        name=":thumbsdown: Top Losers",
        value=make_gainer_string(daily_price_changes.tail(10).iloc[::-1]),
        inline=False,
    )

    # Create the chart
    winner, loser = (
        daily_price_changes["symbol"].iloc[0],
        daily_price_changes["symbol"].iloc[-1],
    )

    figure = make_chart(prices, winner, loser)

    with open("/tmp/" + figure, "rb") as f:
        webhook.add_file(file=f.read(), filename=figure)

    embed.set_image(url="attachment://" + figure)

    # Execute
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


def make_chart(prices: pd.DataFrame, winner: str, loser: str) -> str:
    """Create a chart of the top gainer and loser"""

    top_gainer = get_price_timeseries(prices, winner)
    top_gainer_open = get_yesterday_close(prices, winner)
    top_loser = get_price_timeseries(prices, loser)
    top_loser_open = get_yesterday_close(prices, loser)

    fig = plt.figure(figsize=(10, 8))
    plt.subplots_adjust(wspace=0.05, hspace=0.25)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    ax1.plot(
        top_gainer["timestamp"],
        top_gainer["close"],
        c="g",
        label="Top Gainer: " + winner,
    )
    ax1.axhline(top_gainer_open, color="gray", linestyle="--")
    ax1.fill_between(
        top_gainer["timestamp"],
        top_gainer["close"],
        top_gainer_open,
        where=top_gainer["close"] > top_gainer_open,
        color="g",
        alpha=0.5,
    )
    ax1.fill_between(
        top_gainer["timestamp"],
        top_gainer["close"],
        top_gainer_open,
        where=top_gainer["close"] < top_gainer_open,
        color="r",
        alpha=0.5,
    )

    ax2.plot(
        top_loser["timestamp"], top_loser["close"], c="r", label="Top Loser: " + loser
    )
    ax2.axhline(top_loser_open, color="gray", linestyle="--")
    ax2.fill_between(
        top_loser["timestamp"],
        top_loser["close"],
        top_loser_open,
        where=top_loser["close"] > top_loser_open,
        color="g",
        alpha=0.5,
    )
    ax2.fill_between(
        top_loser["timestamp"],
        top_loser["close"],
        top_loser_open,
        where=top_loser["close"] < top_loser_open,
        color="r",
        alpha=0.5,
    )

    # Figure formatting
    ax1.set_xlim(top_gainer["timestamp"].min(), top_gainer["timestamp"].max())
    ax2.set_xlim(top_gainer["timestamp"].min(), top_gainer["timestamp"].max())

    date_format = mdates.DateFormatter("%I:%M %p", tz=pytz.timezone("Australia/Perth"))
    ax1.xaxis.set_major_formatter(date_format)
    ax2.xaxis.set_major_formatter(date_format)

    tick = mtick.StrMethodFormatter("${x:,.2f}")
    ax1.yaxis.set_major_formatter(tick)
    ax2.yaxis.set_major_formatter(tick)

    ax2.legend(fontsize=15, loc=2)
    ax1.legend(fontsize=15, loc=2)

    ax1.tick_params(labelsize=15)
    ax2.tick_params(labelsize=15)

    filename = "test_image.png"
    plt.savefig("/tmp/" + filename)

    return filename


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
