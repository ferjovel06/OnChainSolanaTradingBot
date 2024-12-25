from pricechangeloop import get_token_list
import pandas as pd
from datetime import datetime

new_data = True

if new_data:
    # run bird eye bot in order to get the meme token data
    data = get_token_list()
else:
    # load the data from the previous run
    data = pd.read_csv("filtered_pricechange.csv")
    print(data)

# in the df if the v24hUSD column has a number in it, drop it from the data and make a new df + save as 'new_launches.csv'
def new_launches(data):
    new_launches = data[data["v24hChangePercent"].isna()]
    timestamp = datetime.now().strftime("%m-%d-%H")
    csv_filename = f"new_launches_{timestamp}.csv"
    new_launches.to_csv(csv_filename, index=False)
    print(new_launches)
    return new_launches

new_launches(data)
