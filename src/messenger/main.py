"""The main handler function which sends the current date and time to discord"""

import os

from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK = os.environ["WEBHOOK"]


def create_discord_embed():
    """Create a discord embed object"""
    embed = DiscordEmbed(
        title="Hourly Report", description="Lorem ipsum dolor sit", color="03b2f8"
    )
    embed.set_timestamp()
    embed.add_embed_field(name="Field 1", value="Lorem ipsum")
    embed.add_embed_field(name="Field 2", value="dolor sit")
    return embed


def main(event=None, context=None):  # pylint: disable=unused-argument
    """Handler function which sends the current date and time to discord"""

    webhook = DiscordWebhook(url=WEBHOOK)
    webhook.add_embed(create_discord_embed())
    webhook.execute()
