"""Utilities to create a daily discord report"""

from discord_webhook import DiscordWebhook, DiscordEmbed


def create_price_alert(webhook: str) -> DiscordEmbed:
    """Create a Discord buy alert"""
    webhook = DiscordWebhook(url=webhook)

    embed = DiscordEmbed(
        title="Buy Alert",
        description="You should buy APX, all signs are green",
        color="03b2f8",
    )
    embed.set_timestamp()

    # Execute
    webhook.add_embed(embed)
    webhook.execute()
