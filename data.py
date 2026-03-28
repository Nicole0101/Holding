import requests
import pandas as pd

def get_stock_data(stock_id):
    url = f"https://query1.finance.yahoo.com/v7/finance/chart/{stock_id}.TW"
    res = requests.get(url).json()

    result = res['chart']['result'][0]

    close = result['indicators']['quote'][0]['close']
    high = result['indicators']['quote'][0]['high']
    low = result['indicators']['quote'][0]['low']

    df = pd.DataFrame({
        "close": close,
        "high": high,
        "low": low
    })

    return df.dropna()
