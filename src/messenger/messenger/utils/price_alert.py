"""Utilities to create a daily discord report"""

import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed


def create_price_alert(webhook: str, prices: pd.DataFrame):
    """Create a Discord buy alert"""

    prices = get_price_stats_for_symbol(prices)

    prices = prices.merge(get_listed_companies(), how="left", on="symbol")

    print("Filtering for stocks to buy or sell...")

    buys = prices[
        (prices["last_close"] > 1)
        & (prices["last_close"] < prices["mean_close"] * 0.95)
        & (prices["last_close"] == prices["min_close"])
    ]

    sales = prices[
        (prices["last_close"] > 1)
        & (prices["last_close"] > prices["mean_close"] * 1.05)
        & (prices["last_close"] == prices["max_close"])
    ]

    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(
        title="Buy Alert",
        description="These stocks are 5% off their 5 day average:",
        color="03b2f8",
    )

    if len(buys) > 0:

        symbols = [
            f"{name.title()} (**{symbol}**)"
            for symbol, name in zip(buys["symbol"], buys["name"])
        ]

        embed.add_embed_field(
            name=":arrow_up: Buy:", value="\n".join(symbols), inline=False,
        )
    if len(sales) > 0:

        symbols = [
            f"{name.title()} (**{symbol}**)"
            for symbol, name in zip(sales["symbol"], sales["name"])
        ]

        embed.add_embed_field(
            name=":arrow_down: Sell:", value="\n".join(symbols), inline=False,
        )
    embed.set_timestamp()

    # Execute
    webhook.add_embed(embed)
    if len(buys) > 0 or len(sales) > 0:
        webhook.execute()
        print("Price alert sent to Discord")

    return


def get_price_stats_for_symbol(df: pd.DataFrame) -> pd.DataFrame:
    """Get the price stats for each symbol"""

    df = (
        df.sort_values(by="timestamp")[["symbol", "close"]]
        .groupby("symbol")
        .agg(
            min_close=("close", "min"),
            max_close=("close", "max"),
            mean_close=("close", "mean"),
            last_close=("close", "last"),
        )
    )

    return df.reset_index()


def get_listed_companies():
    """Get the list of listed companies"""

    return pd.read_gbq(
        query="SELECT * FROM `stocks.listed_companies`",
        project_id="comple-389703",
        dialect="standard",
        use_bqstorage_api=True,
    )
