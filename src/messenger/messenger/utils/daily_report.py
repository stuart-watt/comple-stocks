"""Utilities to create a daily discord report"""
import pytz
import math

import pandas as pd
import numpy as np

from discord_webhook import DiscordWebhook, DiscordEmbed

# pylint: disable=import-error
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from .metrics import get_price_change
from .utils import (
    get_last_two_dates,
    get_yesterday_close,
)


def create_discord_report(webhook: str, prices: pd.DataFrame):
    """Create a Discord report"""
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(
        title="Daily Report",
        description="Top-10 performing stocks today!",
        color="03b2f8",
    )
    embed.set_timestamp()

    # filter by shares with value above $0.5
    prices = prices[prices["price"] > 0.5]

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
    result = webhook.execute()
    if result.status_code == 200:
        print("Discord report created and sent successfully!")
    else:
        raise Exception("Report failed to send to Discord")

    return


def make_gainer_string(df: pd.DataFrame):
    """Create a string of the top gainers"""
    return "\n".join(
        [
            symbol.ljust(7, "᲼")
            + ("+" if pct_change > 0 else "-")
            + f"{abs(pct_change):.1%}".ljust(  # uses a unicode character for empty space
                10, "᲼"
            )
            + ("+" if abs_change > 0 else "-")
            + f"${abs(abs_change):,.3f}"
            for symbol, pct_change, abs_change in zip(
                df["symbol"], df["pct_change"], df["abs_change"]
            )
        ]
    )


def make_chart(prices: pd.DataFrame, winner: str, loser: str) -> str:
    """Create a chart of the top gainer and loser"""

    top_gainer = prices[prices["symbol"] == winner]
    top_gainer = top_gainer.set_index("timestamp").sort_index()
    top_gainer_open = get_yesterday_close(prices, winner)
    top_loser = prices[prices["symbol"] == loser]
    top_loser = top_loser.set_index("timestamp").sort_index()
    top_loser_open = get_yesterday_close(prices, loser)

    fig = plt.figure(figsize=(10, 8))
    plt.subplots_adjust(wspace=0.05, hspace=0.25)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    ax1.plot(
        range(len(top_gainer)),
        top_gainer["price"],
        c="g",
        label="Top Gainer: " + winner,
    )
    ax1.axhline(top_gainer_open, color="gray", linestyle="--")
    ax1.fill_between(
        range(len(top_gainer)),
        top_gainer["price"],
        top_gainer_open,
        where=top_gainer["price"] >= top_gainer_open,
        color="g",
        alpha=0.5,
    )
    ax1.fill_between(
        range(len(top_gainer)),
        top_gainer["price"],
        top_gainer_open,
        where=top_gainer["price"] <= top_gainer_open,
        color="r",
        alpha=0.5,
    )

    ax2.plot(
        range(len(top_loser)), top_loser["price"], c="r", label="Top Loser: " + loser
    )
    ax2.axhline(top_loser_open, color="gray", linestyle="--")
    ax2.fill_between(
        range(len(top_loser)),
        top_loser["price"],
        top_loser_open,
        where=top_loser["price"] >= top_loser_open,
        color="g",
        alpha=0.5,
    )
    ax2.fill_between(
        range(len(top_loser)),
        top_loser["price"],
        top_loser_open,
        where=top_loser["price"] <= top_loser_open,
        color="r",
        alpha=0.5,
    )

    # Figure formatting

    ax1 = format_time_axis(ax1, top_gainer)
    ax2 = format_time_axis(ax2, top_loser)

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


def format_time_axis(ax, data):
    """Format the time axis to continuously vary from one market day to the next"""
    timezone = pytz.timezone("Australia/Perth")

    ticks_date = data.index.indexer_at_time("00:00")
    ticks_time = np.arange(data.index.size)[data.index.minute == 0]
    ax.set_xticks(ticks_date)
    ax.set_xticks(ticks_time, minor=True)

    data.index = data.index.tz_convert(timezone)

    labels_date = [
        maj_tick.strftime("\n%d-%b").replace("\n0", "\n")
        for maj_tick in data.index[ticks_date]
    ]
    labels_time = [
        min_tick.strftime("%I").lstrip("0").lower()
        for min_tick in data.index[ticks_time]
    ]
    ax.set_xticklabels(labels_date)
    ax.set_xticklabels(labels_time, minor=True)
    ax.figure.autofmt_xdate(rotation=0, ha="center", which="both")

    ax.set_xlim(0, len(data))

    return ax
