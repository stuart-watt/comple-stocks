"""Utility functions for interacting with Discord"""
import requests
import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed

# pylint: disable=import-error
from .report import make_report_figure, get_current_trader_status


def scrape_messages_from_discord_channel(channel_id: str, token: str) -> pd.DataFrame:
    """Scrapes all messages from a discord channel and returns a pandas dataframe"""

    headers = {"authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=100"

    r = requests.get(url, headers=headers, timeout=10)

    return pd.DataFrame(r.json())


def create_discord_report(webhook: str, balances: pd.DataFrame):
    """Create a Discord report as a Discrod embed"""
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title="Simulated Trading Results", color="03b2f8")
    embed.set_timestamp()

    numeric_cols = ["balance", "balance_value", "cash_input_balance"]
    balances[numeric_cols] = balances[numeric_cols].astype(float)
    balances["timestamp"] = (
        balances["timestamp"].dt.tz_convert("UTC").dt.tz_localize(None)
    )

    standings = get_current_trader_status(balances)

    total_balance = balances.groupby(["author_name", "timestamp"]).sum().reset_index()
    total_balance["total_change"] = (
        total_balance["balance_value"] - total_balance["cash_input_balance"]
    )
    total_balance["pct_change"] = (
        (total_balance["balance_value"] - total_balance["cash_input_balance"])
        / total_balance["cash_input_balance"]
        * 100
    )

    emojis = [":crown:", ":second_place:", ":poop:"]

    for i, row in standings.iterrows():

        embed.add_embed_field(
            name=f"{emojis[i]} {row.author}", value=row.string, inline=False,
        )

    figure = make_report_figure(total_balance)

    with open("/tmp/" + figure, "rb") as f:
        webhook.add_file(file=f.read(), filename=figure)

    embed.set_image(url="attachment://" + figure)

    # Execute
    webhook.add_embed(embed)
    webhook.execute()
    print("Discord report created and sent successfully!")

    return
