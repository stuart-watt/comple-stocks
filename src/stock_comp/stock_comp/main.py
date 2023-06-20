"""The main handler function which sends a stock report to discord"""

import os
from base64 import b64decode
from time import perf_counter
import json
from random import random


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

    


##########
## Main ##
##########

if __name__ == "__main__":
    start = perf_counter()
    main()
    print(f"Execution time: {perf_counter() - start:.2f} seconds")
