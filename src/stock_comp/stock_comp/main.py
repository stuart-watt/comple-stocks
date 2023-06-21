"""The main handler function which sends a stock report to discord"""

import os
from time import perf_counter

# pylint: disable=import-error
from utils.prices import import_prices_from_bigquery
from utils.discord import scrape_messages_from_discord_channel, create_discord_report
from utils.processing import process_discord_messages, compute_trade_value, compute_balances

PROJECT_ID = os.environ["PROJECT_ID"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
AUTH_TOKEN = os.environ["AUTH_TOKEN"]
PRICES_MINUTELY = os.environ["PRICES_MINUTELY"]
WEBHOOK = os.environ["WEBHOOK"]

#############
## Handler ##
#############

def main(event=None, context=None):
    """Handler function which sends reports/notifications to discord"""

    print("Importing messages from Discord...")
    messages = scrape_messages_from_discord_channel(CHANNEL_ID, AUTH_TOKEN)
    print("Message ingestion success! Converting to trade information...")

    trades = process_discord_messages(messages)
    print("Trades processed successfully! Importing prices from BigQuery...")

    prices = import_prices_from_bigquery(PROJECT_ID, PRICES_MINUTELY, trades)
    print("Price data imported successfully! Computing trade value...")

    trade_value = compute_trade_value(trades, prices)
    print("Trade value computed successfully! Computing balances...")

    balances = compute_balances(trade_value)
    print("Balances computed successfully! Creating Discord report...")

    create_discord_report(WEBHOOK, balances)


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
