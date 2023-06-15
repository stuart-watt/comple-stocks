import pandas as pd
from yahooquery import Ticker


client = Ticker("^AXLD", asynchronous=True)
df = client.history(interval="1m", period="1d").reset_index()

print(df)

# print(client.summary_detail)
