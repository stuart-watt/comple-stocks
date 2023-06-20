import requests
import pandas as pd


CHANNEL_ID = 

def scrape_messages_from_discord_channel(channel_id: str) -> pd.DataFrame:
    """Scrapes all messages from a discord channel and returns a pandas dataframe"""

    headers = {
        'authorization': 'auth header here'
    }

    r = requests.get(f"https://discord.com/api/v9/channels/{channel_id}/messages?", headers=headers)

    print(r.json())

    return

    # df = pd.DataFrame(r.json())

    
    # return df

scrape_messages_from_discord_channel(CHANNEL_ID)
