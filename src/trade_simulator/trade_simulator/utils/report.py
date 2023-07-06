"""Utilities for creating the trading report in Discord"""

from datetime import datetime, timedelta
import pytz

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt


def make_report_figure(df: pd.DataFrame) -> str:
    """Creates and saves a summary figure of the trading results"""

    fig = plt.figure(figsize=(10, 8))
    plt.subplots_adjust(wspace=0.05, hspace=0.25)
    ax1 = fig.add_subplot(111)

    df_trunc = df[df["timestamp"] >= datetime.now() - timedelta(7)]

    authors = df_trunc.display_name.unique()

    for author_name in authors:
        data = df_trunc[df_trunc["display_name"] == author_name]

        data = data.set_index("timestamp")

        ax1.plot(
            range(len(data)), data["total_change"], label=author_name,
        )

        ax1.fill_between(
            range(len(data)),
            data["total_change"],
            0,
            where=data["total_change"] > 0,
            color="g",
            alpha=0.2,
        )
        ax1.fill_between(
            range(len(data)),
            data["total_change"],
            0,
            where=data["total_change"] < 0,
            color="r",
            alpha=0.2,
        )

    ax1.axhline(0, color="gray", linestyle="--")

    # Figure formatting
    ticks_date = data.index.indexer_at_time("00:00")
    ticks_time = np.arange(data.index.size)[data.index.minute == 1][::1]
    ax1.set_xticks(ticks_date)
    ax1.set_xticks(ticks_time, minor=True)

    timezone = pytz.timezone("Australia/Perth")
    data.index = data.index.tz_localize("UTC").tz_convert(timezone)

    labels_date = [
        maj_tick.strftime("\n%d-%b").replace("\n0", "\n")
        for maj_tick in data.index[ticks_date]
    ]
    labels_time = [
        min_tick.strftime("%H").lstrip("0").lower()
        for min_tick in data.index[ticks_time]
    ]
    ax1.set_xticklabels(labels_date)
    ax1.set_xticklabels(labels_time, minor=True)
    ax1.figure.autofmt_xdate(rotation=0, ha="center", which="both")

    ax1.legend(
        fontsize=20, bbox_to_anchor=(0.5, -0.27), loc="lower center", ncols=len(authors)
    )

    ax1.tick_params(labelsize=15)

    ax1.set_xlim(0, len(data))

    ax1.set_title("Total Returns", fontsize=20)

    filename = "simulated_trading_results.png"
    plt.savefig("/tmp/" + filename, facecolor="w")

    return filename


def get_current_trader_status(balances: pd.DataFrame) -> pd.DataFrame:
    """Creates a string displaying each traders balances"""

    current_balances = (
        balances[
            [
                "display_name",
                "symbol",
                "timestamp",
                "balance",
                "balance_value",
                "average_buy_price",
            ]
        ]
        .sort_values(by=["timestamp"])
        .groupby(["display_name", "symbol"])
        .last()
        .reset_index()
    )

    stock_balances = current_balances[
        (current_balances["balance"] > 0) & (current_balances["symbol"] != "$AUD")
    ]

    cash_balances = current_balances[(current_balances["symbol"] == "$AUD")]

    standings = []

    for author in stock_balances["display_name"].unique():
        author_cash = cash_balances[cash_balances["display_name"] == author]
        cash = author_cash.balance_value.iloc[0]
        embed_rows = [f"Cash: **${cash:.2f}**"]

        author_balances = stock_balances[stock_balances["display_name"] == author]

        for _, row in author_balances.iterrows():
            ROI = (row.balance_value - row.balance * row.average_buy_price) / (
                row.balance * row.average_buy_price
            )
            embed_rows.append(
                f"{row.symbol}: {int(row.balance)} "
                + f"(**${row.balance_value:.2f}**) ("
                + ("+" if ROI >= 0 else "-")
                + f"{abs(ROI)*100:.2f}%)"
            )

        total_investment = cash + author_balances.balance_value.sum()
        embed_rows.append(f"**__Total: ${total_investment:.2f}__**")

        standings.append(
            {
                "author": author,
                "total": total_investment,
                "string": "\n".join(embed_rows),
            }
        )

    return (
        pd.DataFrame(standings)
        .sort_values(by="total", ascending=False)
        .reset_index(drop=True)
    )
