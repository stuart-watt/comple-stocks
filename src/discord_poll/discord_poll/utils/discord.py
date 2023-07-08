"""Utility functions for interacting with Discord"""

import os
from datetime import datetime, timedelta, timezone
import requests

POLLING_PERIOD = os.environ["POLLING_PERIOD"]


def scrape_messages_from_discord_channel(channel_id: str, token: str) -> dict:
    """Scrapes all commands from a discord channel"""

    headers = {"authorization": f"Bot {token}"}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=50"

    r = requests.get(url, headers=headers, timeout=10)

    threshold = datetime.now(timezone.utc) - timedelta(minutes=int(POLLING_PERIOD))

    return {
        i.get("content", "")
        for i in r.json()
        if datetime.fromisoformat(i["timestamp"]).replace(tzinfo=timezone.utc)
        >= threshold
    }
