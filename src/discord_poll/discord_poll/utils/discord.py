"""Utility functions for interacting with Discord"""
import requests


def scrape_messages_from_discord_channel(channel_id: str, token: str) -> dict:
    """Scrapes all messages from a discord channel and returns a pandas dataframe"""

    headers = {"authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=3"

    r = requests.get(url, headers=headers, timeout=10)

    return {i["content"] for i in r.json() if i.get("content", "").startswith("!")}
