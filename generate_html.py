import pandas as pd
import requests
from jinja2 import Template
from datetime import datetime, timedelta
import os

FINMIND_TOKEN = os.getenv("FINMIND_TOKEN")

# =========================
# 抓股價（FinMind）
# =========================
def get_stock_data(stock_id):
    url = "https://api.finmindtrade.com/api/v4/data"

    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": "2024-01-01",
        "token": FINMIND_TOKEN
    }

    res = requests.get(url, params=params)
    data = res.json().get("data", [])

    df = pd.DataFrame(data)
    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    return df


# =========================
# 指標
# =========================
def add_indicators(df):

    # KD
    low_min = df["min"].rolling(9).min()
    high_max = df["max"].rolling(9).max()
    rsv = (df["close"] - low_min) / (high_max - low_min) * 100

    df["K"] = rsv.ewm(com=2).mean()
    df["D"] = df["K"].ewm(com=2).mean()

    # 布林
    ma20 = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()

    df["BB_upper"] = ma20 + 2 * std
    df["BB_lower"] = ma20 - 2 * std

    return df


# =========================
# 距離
# =========================
def calc_dist(price, ma):
    if ma == 0 or pd.isna(ma):
        return None
    return round((price - ma) / ma * 100, 2)


# =========================
# 單股處理🔥
# =========================
def process_stock(s):

    try:
        df = get_stock_data(str(s["stock_id"]))
        if df is None or len(df) < 60:
            return
