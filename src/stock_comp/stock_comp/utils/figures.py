"""Utilities for creating the trading report figure"""

import pytz

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick

def make_report_figure(df: pd.DataFrame) -> str:
    """Creates and saves a summary figure of the trading results"""

    fig = plt.figure(figsize=(10, 8))
    plt.subplots_adjust(wspace=0.05, hspace=0.25)
    ax1 = fig.add_subplot(111)

    for author_name in df.author_name.unique():
        data = df[df["author_name"] == author_name]

        ax1.plot(
            data["timestamp"],
            data["total_change"],
            label=author_name,
        )

        ax1.fill_between(
            data["timestamp"],
            data["total_change"],
            0,
            where=data["total_change"] > 0,
            color="g",
            alpha=0.2,
        )
        ax1.fill_between(
            data["timestamp"],
            data["total_change"],
            0,
            where=data["total_change"] < 0,
            color="r",
            alpha=0.2,
        )


    ax1.axhline(0, color="gray", linestyle="--")
    ax1.set_xlim(data["timestamp"].min(), data["timestamp"].max())

    date_format = mdates.DateFormatter("%I:%M %p", tz=pytz.timezone("Australia/Perth"))
    ax1.xaxis.set_major_formatter(date_format)

    tick = mtick.StrMethodFormatter("${x:,.2f}")
    ax1.yaxis.set_major_formatter(tick)

    ax1.legend(fontsize=20, loc=3)
    ax1.tick_params(labelsize=15)
    ax1.set_title("Total Returns", fontsize=20)

    filename = "simulated_trading_results.png"
    plt.savefig("/tmp/" + filename, facecolor="w")

    return filename
