import requests
import pandas as pd
from decouple import config
import pprint as pp
from urllib.parse import urlencode
import time

def get_token_list():
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
    num_tokens = 10000

    while total_tokens < num_tokens:
        print("looping...")
        print(total_tokens)
        params = {
            "sort_by": "v24hUSD",
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
        elif response.status_code == 429:
            time.sleep(1)
            continue
        else:
            print("Failed to retrieve data", response.status_code)
            break

    min_mc = 50
    max_mc = 20000

    filtered_tokens = [token for token in tokens if token.get('mc') is not None and min_mc <= token['mc'] <= max_mc]

    # Create a DataFrame from the filtered tokens
    df = pd.DataFrame(filtered_tokens)

    # Set minimum liquidity and minimum 24-hour volume
    min_liquidity = 2000
    min_volume_24h = 2000
    mins_last_trade = 59

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

    # Filter out tokens that have not traded in the last 60 minutes
    current_time = pd.Timestamp.now(tz='US/Eastern')
    df['mins_since_last_trade'] = (current_time - df.index).total_seconds() / 60

    df = df[df['mins_since_last_trade'] <= mins_last_trade]
    df.drop(columns=['mins_since_last_trade'], inplace=True)

    # Add a new column for token url
    params = {
        'chain': 'solana',
    }
    df["token_url"] = df["address"].apply(
        lambda x: f"https://www.birdeye.so/token/{x}?{urlencode(params)}"
    )

    # Save the DataFrame to a CSV file
    df.to_csv("filtered_pricechange.csv")

    # Pretty-print the DataFrame
    pd.set_option('display.max_columns', None)
    pp.pprint(df)

    return df
