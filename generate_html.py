import pandas as pd
from data import get_stock_data
from indicator import add_indicators
from jinja2 import Template
from datetime import datetime, timedelta

# ===== 讀CSV =====
def load_stock_list():
    df = pd.read_csv("stocks.csv", sep="\t", encoding="utf-8-sig")
    df = df.rename(columns={"Ticker": "stock_id", "Name": "name"})
    return df.to_dict(orient="records")

# ===== 工具 =====
def calc_bias(price, ma):
    if ma is None or ma == 0:
        return 0
    return round((price - ma) / ma * 100, 2)

def get_signal(k, d):
    if k > 70 and d > 70:
        return "sell"
    elif k < 30 and d < 30:
        return "buy"
    elif k > d:
        return "hold"
    else:
        return "watch"

def get_bb_position(price, upper, lower):
    if price >= upper:
        return "上軌"
    elif price <= lower:
        return "下軌"
    return "中軌"

# ===== 主流程 =====
stock_list = load_stock_list()
results = []

for s in stock_list:
    try:
        df = get_stock_data(str(s["stock_id"]))
        df = add_indicators(df)

        if df is None or len(df) < 20:
            continue

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        # ===== 價格 =====
        chg = latest["close"] - prev["close"]
        chgPct = (chg / prev["close"]) * 100

        # ===== 震幅（正確🔥）=====
        amplitude = ((latest["high"] - latest["low"]) / prev["close"]) * 100

        # ===== 均線 =====
        ma20 = df["close"].rolling(20).mean().iloc[-1] if len(df) >= 20 else None
        ma60 = df["close"].rolling(60).mean().iloc[-1] if len(df) >= 60 else None
        bias20 = calc_bias(latest["close"], ma20)
        bias60 = calc_bias(latest["close"], ma60)
        
        # ===== KD =====
        k = latest["K"]
        d = latest["D"]

        # ===== 策略 =====
        if amplitude > 5 and k < 30:
            strategy = "反彈🔥"
        elif amplitude > 5 and k > 70:
            strategy = "出貨⚠"
        elif amplitude < 2:
            strategy = "整理"
        else:
            strategy = "觀察"

        results.append({
            "name": s["name"],
            "code": s["stock_id"],
            "price": round(latest["close"], 2),
            "chg": round(chg, 2),
            "chgPct": round(chgPct, 2),
            "amp": round(amplitude, 2),
            "bias20": bias20,
            "bias60": bias60,
            "k": round(k, 1),
            "d": round(d, 1),
            "bb": get_bb_position(latest["close"], latest["BB_upper"], latest["BB_lower"]),
            "sig": get_signal(k, d),
            "strategy": strategy
        })

    except Exception as e:
        print(f"錯誤 {s['stock_id']}:", e)

print("結果數量:", len(results))

# ===== 排序 =====
sorted_stocks = sorted(results, key=lambda x: x["chgPct"], reverse=True)
top_names = ", ".join([s["name"] for s in sorted_stocks[:5]])
weak_names = ", ".join([s["name"] for s in sorted_stocks[-5:]])

# ===== 策略統計 =====
rebound_list = [s["name"] for s in results if s["strategy"] == "反彈🔥"]
selloff_list = [s["name"] for s in results if s["strategy"] == "出貨⚠"]

# ===== HTML =====
with open("template.html", "r", encoding="utf-8") as f:
    template = Template(f.read())

html = template.render(
    stocks=results,
    top_stocks=top_names,
    weak_stocks=weak_names,
    rebound_list=", ".join(rebound_list[:5]),
    selloff_list=", ".join(selloff_list[:5])
)

# ===== 存檔 =====
now = (datetime.utcnow() + timedelta(hours=8)).strftime("%m%d%H%M")
filename = f"持股_{now}.html"

with open(filename, "w", encoding="utf-8") as f:
    f.write(html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("輸出:", filename)

# ===== LINE =====
from line_push import send_line

msg = f"""
📊 台股個股策略

🔥 強勢股：
{top_names}

⚠ 弱勢股：
{weak_names}

📌 反彈機會：
{", ".join(rebound_list[:5])}

📌 出貨警示：
{", ".join(selloff_list[:5])}

👉 https://nicole0101.github.io/StockHolding-report/
"""

send_line(msg)
