"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter
import json
from base64 import b64decode

import fire

# pylint: disable=import-error
from utils.discord import (
    scrape_messages_from_discord_channel,
    scrape_members_from_discord_guild,
    create_discord_report,
)
from utils.processing import process_discord_messages
from utils.bigquery import load_to_bg, read_from_bg

PROJECT_ID = os.environ["PROJECT_ID"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
GUILD_ID = os.environ["GUILD_ID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
PRICES_MINUTELY = os.environ["PRICES_MINUTELY"]
TRADES_TABLE = os.environ["TRADES_TABLE"]
TRADE_BALANCES = os.environ["TRADE_BALANCES"]
WEBHOOK = os.environ["WEBHOOK"]

#############
## Handler ##
#############


def main(event=None, context=None):
    """Handler function which sends reports/notifications to discord"""

    if set(event.keys()) == {"method"}:  # Invoked manually.
        pass
    else:  # Invoked via pubsub.
        event = json.loads(b64decode(event["data"]).decode("utf-8"))

    if event["method"] == "scrape-trades":
        scrape_messages()

    if event["method"] == "report":
        send_report()


##################
## Sub-Handlers ##
##################


def scrape_messages():
    """Scrape messages from discord channel"""

    print("Importing messages from Discord...")
    messages = scrape_messages_from_discord_channel(CHANNEL_ID, AUTH_TOKEN)
    print("Message ingestion success! Converting to trade information...")

    trades = process_discord_messages(messages)
    print("Trades processed successfully!")

    ids = read_from_bg(PROJECT_ID, TRADES_TABLE).id.unique()

    trades = trades[~trades["id"].isin(ids)]
    if len(trades) > 0:
        load_to_bg(PROJECT_ID, trades, TRADES_TABLE, "append")
    else:
        print("No new messages found!")


def send_report():
    """Send report to discord"""

    print("Importing trade balances from BigQuery...")
    balances = read_from_bg(PROJECT_ID, TRADE_BALANCES)

    print("Importing guild nicknames")
    names = scrape_members_from_discord_guild(GUILD_ID, AUTH_TOKEN)

    print("Trade balances imported successfully! Creating Discord report...")
    create_discord_report(WEBHOOK, balances, names)


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    fire.Fire(main)
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
