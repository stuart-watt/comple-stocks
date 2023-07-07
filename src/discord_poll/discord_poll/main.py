"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter

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

    print("Importing messages from Discord...")
    commands = scrape_messages_from_discord_channel(CHANNEL_ID, AUTH_TOKEN)
    print("Message ingestion success! Converting to trade information...")

    print("Commands found:", commands)


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
