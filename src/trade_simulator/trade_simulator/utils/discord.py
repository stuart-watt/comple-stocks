"""Utility functions for interacting with Discord"""
import requests
import pandas as pd

from discord_webhook import DiscordWebhook, DiscordEmbed

# pylint: disable=import-error
from .figures import make_report_figure


def scrape_messages_from_discord_channel(channel_id: str, token: str) -> pd.DataFrame:
    """Scrapes all messages from a discord channel and returns a pandas dataframe"""

    headers = {"authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?"

    r = requests.get(url, headers=headers, timeout=10)

    return pd.DataFrame(r.json())


def create_discord_report(webhook: str, df: pd.DataFrame):
    """Create a Discord report as a Discrod embed"""
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(title="Simulated Trading Results", color="03b2f8",)
    embed.set_timestamp()

    embed.add_embed_field(
        name=":crown: Traders", value="\n".join(df.author_name.unique()), inline=False,
    )

    figure = make_report_figure(df)

    with open("/tmp/" + figure, "rb") as f:
        webhook.add_file(file=f.read(), filename=figure)

    embed.set_image(url="attachment://" + figure)

    # Execute
    webhook.add_embed(embed)
    webhook.execute()
    print("Discord report created and sent successfully!")

    return
