"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter
import json

from google.cloud import pubsub_v1

# pylint: disable=import-error
from utils.discord import scrape_messages_from_discord_channel

PROJECT_ID = os.environ["PROJECT_ID"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
TOPIC = os.environ["TOPIC"]

#############
## Handler ##
#############


def main(event=None, context=None):
    """Handler function which polls Discord for messages"""

    print("Importing commands from Discord...")
    messages = scrape_messages_from_discord_channel(CHANNEL_ID, AUTH_TOKEN)
    print("Message ingestion success!")

    client = pubsub_v1.PublisherClient()

    trades = [
        i for i in messages if i.lower().startswith(("buy", "sell", "add", "subtract"))
    ]

    commands = [i for i in messages if i.startswith("!")]

    if len(trades) > 0:
        msg = json.dumps({"method": "scrape-trades"}).encode()
        print(f"Publishing message to {TOPIC}: {msg}")
        client.publish(TOPIC, msg).result()

    if "!chart" in commands:
        msg = json.dumps({"method": "report"}).encode()
        print(f"Publishing message to {TOPIC}: {msg}")
        client.publish(TOPIC, msg).result()

    if (len(trades) == 0) & (len(commands) == 0):
        print(("Nothing to do!"))


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
