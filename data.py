import requests
import pandas as pd

def get_stock_data(stock_id):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_id}.TW"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)

    # ⭐ 防呆（超重要）
    if res.status_code != 200:
        raise Exception(f"API錯誤: {res.status_code}")

    try:
        data = res.json()
    except:
        raise Exception("回傳不是JSON（可能被擋）")

    result = data.get('chart', {}).get('result')

    if not result:
        raise Exception("沒有資料（Yahoo擋或股票不存在）")

    quote = result[0]['indicators']['quote'][0]

    df = pd.DataFrame({
        "close": quote['close'],
        "high": quote['high'],
        "low": quote['low']
    })

    return df.dropna()
