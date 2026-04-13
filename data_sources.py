import logging
import os
from datetime import datetime

import pandas as pd
import requests
from FinMind.data import DataLoader
from loguru import logger

API_TOKEN = os.getenv('FINMIND_TOKEN')
API_URL = 'https://api.finmindtrade.com/api/v4/data'
api = DataLoader()

# 停用所有來自 FinMind 的 Log 訊息
logger.remove()
logging.getLogger('FinMind').setLevel(logging.WARNING)


def get_stock_data(stock_id):
    try:
        params = {
            'dataset': 'TaiwanStockPrice',
            'data_id': str(stock_id),
            'start_date': '2023-01-01',
            'token': API_TOKEN,
        }
        res = requests.get(API_URL, params=params, timeout=10)
        data = res.json()

        if 'data' not in data or len(data['data']) == 0:
            return pd.DataFrame()

        df = pd.DataFrame(data['data'])

        volume_col = None
        for c in ['Trading_Volume', 'trading_volume', 'Trading_Volume_1000']:
            if c in df.columns:
                volume_col = c
                break

        required_cols = ['date', 'open', 'close', 'max', 'min']
        if volume_col:
            required_cols.append(volume_col)

        df = df[required_cols].copy()
        df['date'] = pd.to_datetime(df['date'])

        if volume_col:
            df['volume'] = pd.to_numeric(df[volume_col], errors='coerce')
            if df['volume'].max() > 100000:
                df['volume'] = df['volume'] / 1000
        else:
            df['volume'] = None

        df = df.dropna(subset=['open', 'close', 'max',
                       'min']).sort_values('date')
        return df

    except Exception as e:
        print(f'❌ get_stock_data error {stock_id}: {e}')
        return pd.DataFrame()


def get_profit_ratio(stock_id):
    try:
        df = api.taiwan_stock_financial_statement(
            stock_id=stock_id,
            start_date='2022-01-01',
        )
        return df
    except Exception as e:
        print(f'❌ profit source error {stock_id}: {e}')
        return pd.DataFrame()


def get_eps_raw(stock_id):
    try:
        params = {
            'dataset': 'TaiwanStockFinancialStatements',
            'data_id': stock_id,
            'start_date': '2020-01-01',
            'token': API_TOKEN,
        }
        return requests.get(API_URL, params=params, timeout=10).json().get('data', [])
    except Exception as e:
        print(f'❌ EPS source error {stock_id}: {e}')
        return []


def get_dividend_raw(stock_id):
    try:
        params = {
            'dataset': 'TaiwanStockDividend',
            'data_id': stock_id,
            'start_date': '2020-01-01',
            'token': API_TOKEN,
        }
        res = requests.get(API_URL, params=params, timeout=10)
        if res.status_code != 200:
            return []
        return res.json().get('data', [])
    except Exception as e:
        print(f'❌ dividend source error {stock_id}: {e}')
        return []


def get_per_raw(stock_id):
    try:
        params = {
            'dataset': 'TaiwanStockPER',
            'data_id': stock_id,
            'start_date': '2023-01-01',
            'token': API_TOKEN,
        }
        res = requests.get(API_URL, params=params, timeout=10)
        return res.json().get('data', [])
    except Exception:
        return []
