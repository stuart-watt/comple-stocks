"""Utilities for creating the trading report in Discord"""

import pytz

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt


def make_report_figure(df: pd.DataFrame) -> str:
    """Creates and saves a summary figure of the trading results"""

    fig = plt.figure(figsize=(10, 8))
    plt.subplots_adjust(wspace=0.05, hspace=0.25)
    ax1 = fig.add_subplot(111)

    for author_name in df.author_name.unique():
        data = df[df["author_name"] == author_name]

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
        min_tick.strftime("%I %p").lstrip("0").lower()
        for min_tick in data.index[ticks_time]
    ]
    ax1.set_xticklabels(labels_date)
    ax1.set_xticklabels(labels_time, minor=True)
    ax1.figure.autofmt_xdate(rotation=0, ha="center", which="both")

    ax1.legend(fontsize=20, loc=3)

    ax1.tick_params(labelsize=15)

    ax1.set_xlim(0, len(data))

    ax1.set_title("Total Returns", fontsize=20)

    filename = "simulated_trading_results.png"
    plt.savefig("/tmp/" + filename, facecolor="w")

    return filename


def get_current_trader_status(
    trades: pd.DataFrame, balances: pd.DataFrame
) -> pd.DataFrame:
    """Creates a string displaying each traders balances"""

    stock_balances = (
        trades[["author_name", "symbol", "timestamp", "balance", "stock_balance_value"]]
        .sort_values(by=["timestamp"])
        .groupby(["author_name", "symbol"])
        .last()
        .reset_index()
    )

    stock_balances = stock_balances[
        (stock_balances["balance"] > 0) & (stock_balances["symbol"] != "$aud")
    ]
    stock_balances = stock_balances[
        ["author_name", "symbol", "balance", "stock_balance_value"]
    ]

    cash_balances = (
        balances[["author_name", "timestamp", "cash_balance"]]
        .sort_values(by=["timestamp"])
        .groupby(["author_name"])
        .last()
        .reset_index()
    )
    cash_balances = cash_balances[["author_name", "cash_balance"]]

    standings = []

    for author in stock_balances["author_name"].unique():
        author_cash = cash_balances[cash_balances["author_name"] == author]
        cash = author_cash.cash_balance.iloc[0]
        string = f"Cash: **${cash:.2f}**\n"

        author_balances = stock_balances[stock_balances["author_name"] == author]
        string += "\n".join(
            [
                f"{row.symbol.upper()}: {int(row.balance)} (**${row.stock_balance_value:.2f}**)"
                for _, row in author_balances.iterrows()
            ]
        )

        total = cash + author_balances.stock_balance_value.sum()

        string += f"\nTotal: ${total:.2f}"

        standings.append({"author": author, "total": total, "string": string})

    return (
        pd.DataFrame(standings)
        .sort_values(by="total", ascending=False)
        .reset_index(drop=True)
    )
