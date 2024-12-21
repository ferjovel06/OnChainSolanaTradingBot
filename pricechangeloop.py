import requests
import pandas as pd
from decouple import config
import pprint as pp

url = (
    "https://public-api.birdeye.so/defi/tokenlist"
)
BIRDEYE_API_KEY = config("BIRDEYE_API_KEY")

headers = {
    "accept": "application/json",
    "x-chain": "solana",
    "X-API-KEY": BIRDEYE_API_KEY,
}

tokens = []
offset = 0
limit = 50
total_tokens = 0
num_tokens = 1000

while total_tokens < num_tokens:
    print("looping...")
    params = {
        "sort_by": "v24hChangePercent",
        "sort_type": "desc",
        "offset": offset,
        "limit": limit,
        "min_liquidity": 100,
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        response_data = response.json()
        new_tokens = response_data.get("data", {}).get("tokens", [])
        tokens.extend(new_tokens)
        total_tokens += len(new_tokens)
        offset += limit
    else:
        print("Failed to retrieve data", response.status_code)
        break

min_mc = 1000
max_mc = 20000

filtered_tokens = [token for token in tokens if token.get('mc') is not None and min_mc <= token['mc'] <= max_mc]

# Create a DataFrame from the filtered tokens
df = pd.DataFrame(filtered_tokens)

# Set minimum liquidity and minimum 24-hour volume
min_liquidity = 2000
min_volume_24h = 2000

# Drop rows with less than minimum liquidity and 24-hour volume
df = df.dropna(subset=['liquidity', 'v24hUSD'])
df = df[(df["liquidity"] >= min_liquidity) & (df["v24hUSD"] >= min_volume_24h)]

# Drop columns that are not needed
drop_columns = ['logoURI']
df = df.drop(columns=drop_columns)

# Convert lastTradeUnixTime to EST tie and create a new column
df['lastTradeUnixTime'] = pd.to_datetime(df['lastTradeUnixTime'], unit='s')
df['lastTradeTime_EST'] = df['lastTradeUnixTime'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')

# Set lastTradeUnixTime as the index, keeping it in the DataFrame
df.set_index('lastTradeTime_EST', inplace=True)

# Move lastTradeUnixTime to the first column
df = df[[col for col in df if col != 'lastTradeUnixTime'] + ['lastTradeUnixTime']]

# Save the DataFrame to a CSV file
df.to_csv("filtered_pricechange.csv")

# Pretty-print the DataFrame
pd.set_option('display.max_columns', None)
pp.pprint(df)
