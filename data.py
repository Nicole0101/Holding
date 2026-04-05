import requests
import pandas as pd
import os
from FinMind.data import DataLoader
from datetime import datetime

API_TOKEN = os.getenv("FINMIND_TOKEN")
api_url = "https://api.finmindtrade.com/api/v4/data"
api = DataLoader()

def get_stock_data(stock_id):
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": str(stock_id),
        "start_date": "2023-01-01",
        "token": API_TOKEN
    }
    res = requests.get(api_url, params=params)
    data = res.json()
    if "data" not in data or len(data["data"]) == 0:
        return pd.DataFrame()
    df = pd.DataFrame(data["data"])
    df = df.rename(columns={"close": "close", "max": "high", "min": "low"})
    return df[["close", "high", "low"]].dropna()

def get_profit_ratio(stock_id):
    try:
        df = api.taiwan_stock_financial_statement(stock_id=stock_id, start_date="2023-01-01")
        df = df.sort_values("date")
        latest = df.groupby("type").last()["value"]
        revenue = latest.get("Revenue", 0)
        if revenue == 0: return None, None, None
        
        gross_margin = round(latest.get("GrossProfit", 0) / revenue * 100, 2)
        op_margin = round(latest.get("OperatingIncome", 0) / revenue * 100, 2)
        net_margin = round(latest.get("IncomeAfterTaxes", 0) / revenue * 100, 2)
        return gross_margin, op_margin, net_margin
    except:
        return None, None, None

def est_eps_logic(stock_id):
    try:
        eps_df = api.taiwan_stock_eps(stock_id=stock_id).sort_values("date", ascending=False).head(4)
        ttm_eps = eps_df["eps"].sum()
        rev = api.taiwan_stock_month_revenue(stock_id=stock_id)
        rev["YoY"] = rev["revenue"].pct_change(12)
        growth = rev.sort_values("date").tail(3)["YoY"].mean()
        return round(ttm_eps, 2), round(ttm_eps * (1 + growth), 2)
    except:
        return None, None

def add_indicators(df):
    low_min = df["low"].rolling(9).min()
    high_max = df["high"].rolling(9).max()
    rsv = (df["close"] - low_min) / (high_max - low_min) * 100
    df["K"] = rsv.ewm(com=2).mean()
    df["D"] = df["K"].ewm(com=2).mean()
    ma20 = df["close"].rolling(20).mean()
    std = df["close"].rolling(20).std()
    df["BB_upper"] = ma20 + 2 * std
    df["BB_lower"] = ma20 - 2 * std
    return df

def process_stock(s):
    try:
        df = get_stock_data(s["stock_id"])
        if df.empty or len(df) < 60: return None
        df = add_indicators(df)
        latest, prev = df.iloc[-1], df.iloc[-2]

        chgPct = round(((latest["close"] - prev["close"]) / prev["close"]) * 100, 2)
        amp = round(((latest["high"] - latest["low"]) / prev["close"]) * 100, 2)
        gm, om, nm = get_profit_ratio(s["stock_id"])
        ttm_eps, est_eps_val = est_eps_logic(s["stock_id"])

        k, d = latest["K"], latest["D"]
        strategy = "反彈🔥" if amp > 5 and k < 30 else "出貨⚠" if amp > 5 and k > 70 else "整理" if amp < 2 else "觀察"

        return {
            "name": s["name"][:3],
            "code": s["stock_id"],
            "price": round(latest["close"], 2),
            "chgPct": chgPct,
            "amp": amp,
            "gross_margin": gm,
            "net_margin": nm,
            "ttm_eps": ttm_eps,
            "est_eps": est_eps_val,
            "k": round(k, 1),
            "bb": "上軌" if latest["close"] > latest["BB_upper"] else "下軌" if latest["close"] < latest["BB_lower"] else "中軌",
            "strategy": strategy
        }
    except Exception as e:
        print(f"Error processing {s['stock_id']}: {e}")
        return None

def get_full_stock_analysis(stock_list):
    results = []
    for s in stock_list:
        data = process_stock(s)
        if data: results.append(data)
    return results