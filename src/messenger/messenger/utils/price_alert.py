"""Utilities to create a daily discord report"""

import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed


def create_price_alert(
    webhook: str, historical_prices: pd.DataFrame, current_prices: pd.DataFrame
):
    """Create a Discord buy alert"""

    prices = get_price_stats_for_symbol(historical_prices)

    prices = prices.merge(get_listed_companies(), how="left", on="symbol")
    prices = prices.merge(current_prices, how="left", on="symbol")

    print("Filtering for stocks to buy or sell...")

    buys = prices[
        (prices["currentPrice"] > 0.5)
        & (prices["currentPrice"] < prices["mean_price"] * 0.95)
        & (prices["currentPrice"] < prices["min_price"])
    ]

    sales = prices[
        (prices["currentPrice"] > 0.5)
        & (prices["currentPrice"] > prices["mean_price"] * 1.05)
        & (prices["currentPrice"] > prices["max_price"])
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
        result = webhook.execute()
        if result.status_code == 200:
            print("Price alert sent to Discord")
        else:
            raise Exception("Price alert failed to send to Discord")

    return


def get_price_stats_for_symbol(df: pd.DataFrame) -> pd.DataFrame:
    """Get the price stats for each symbol"""

    df = (
        df.sort_values(by="timestamp")[["symbol", "price"]]
        .groupby("symbol")
        .agg(
            min_price=("price", "min"),
            max_price=("price", "max"),
            mean_price=("price", "mean"),
        )
    )

    numeric_columns = ["min_price", "max_price", "mean_price"]
    df[numeric_columns] = df[numeric_columns].astype(float)

    return df.reset_index()


def get_listed_companies():
    """Get the list of listed companies"""

    return pd.read_gbq(
        query="SELECT * FROM `stocks.listed_companies`",
        project_id="comple-389703",
        dialect="standard",
        use_bqstorage_api=True,
    )
