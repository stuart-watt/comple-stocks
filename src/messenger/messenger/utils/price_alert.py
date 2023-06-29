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
        (prices["currentPrice"] > 1)
        & (prices["currentPrice"] < prices["mean_price"] * 0.95)
        & (prices["currentPrice"] < prices["min_price"])
    ]

    sales = prices[
        (prices["currentPrice"] > 1)
        & (prices["currentPrice"] > prices["mean_price"] * 1.05)
        & (prices["currentPrice"] > prices["max_price"])
    ]

    webhook = DiscordWebhook(url=webhook)
    embed = DiscordEmbed(
        title="Buy Alert",
        description="These stocks are 5% off their 5 day average:",
        color="03b2f8",
    )

    print(f"Found {len(buys)} stocks to buy and {len(sales)} to sell")

    if len(buys) > 0:

        for s in list_stocks_in_embed_field(buys):
            embed.add_embed_field(
                name=":arrow_up: Buy:", value=s, inline=False,
            )

    if len(sales) > 0:

        for s in list_stocks_in_embed_field(sales):
            embed.add_embed_field(
                name=":arrow_down: Sell:", value=s, inline=False,
            )
    embed.set_timestamp()

    # Execute
    webhook.add_embed(embed)
    if len(buys) > 0 or len(sales) > 0:
        result = webhook.execute()
        if result.status_code == 200:
            print("Price alert sent to Discord")
        else:
            raise Exception(f"Price alert failed to send to Discord: {result.json()}")

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


def list_stocks_in_embed_field(df: pd.DataFrame) -> list:
    """Creates a string that can be passed to an embed field
    This function handles the case where the embed field value has more than
    1024 characters. In which case, a new string is created.
    """
    fields = []
    s = []
    for symbol, name in zip(df["symbol"], df["name"]):
        temp_s = [f"{name.title()} (**{symbol}**)"]

        if len("\n".join(s + temp_s)) > 1024:
            fields.append("\n".join(s))
            s = temp_s

        else:
            s += temp_s

    fields.append("\n".join(s))

    return fields
