# birdeye

"""
STRATEGY

1. Pull all data from birdeye API and get the volume, tvl, 24h trade, 24h vies, market cap (under 500k)
    - List of fresh tokens
    - Get their contract address
    - Get their market cap
    - Get their volume
    - Get their price
    - Get their 24h trades
    - Get their tvl == total value locked (liquidity in output)
    - Check recent sells and buys to make sure there is vol
        lastTradeUnixTime == the time last trade, make sure there are trades
        v24hUSD == volume in the last 24 hours
        mc == market cap
2. Analyze that data to decide which is best to buy.
    - Use llms
    - use gpt vision
3. Buy 5 top memes of the day after data analysis.

IDEAS
- Follow traders profiles, especially other bots

API
- Endpoints: https://docs.birdeye.so/reference/get_defi-price

"""
import requests
import pandas as pd
from decouple import config
import pprint as pp

volume_tokes = ("https://public-api.birdeye.so/defi/tokenlist?sort_by=v24hUSD&sort_type=desc&offset=0&limit=50"
                "&min_liquidity=100")
percent_change = ("https://public-api.birdeye.so/defi/tokenlist?sort_by=v24hChangePercent&sort_type=desc&offset=0"
                  "&limit=50&min_liquidity=100")
market_cap = ("https://public-api.birdeye.so/defi/tokenlist?sort_by=mc&sort_type=desc&offset=0&limit=50&min_liquidity"
              "=100")
min_volume = 10000
BIRDEYE_API_KEY = config("BIRDEYE_API_KEY")

url = percent_change

headers = {
    "accept": "application/json",
    "x-chain": "solana",
    "X-API-KEY": BIRDEYE_API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()["data"]

    # Filtering out tokens with mc over 10k
    filtered_data = [token for token in data["tokens"] if token["mc"] > 10000]

    pp.pprint(filtered_data)

    # Create a dataframe from the data
    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    csv_file_path = "bird.csv"
    df.to_csv(csv_file_path)
    print(f"Data saved to {csv_file_path}")
else:
    print("Failed to retrieve data", response.status_code)

# CONNECT TO BIRDEYE API

# List of fresh tokens

# - Get their contract address

# - Get their market cap

# - Get their volume

# - Get their price

# - Get their 24h trades

# - Get their 24h tvl
