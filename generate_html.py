import pandas as pd
from datetime import datetime, timedelta
from jinja2 import Template
from data import get_full_stock_analysis


# ========================
# 1️⃣ 工具函數
# ========================
def format_output(results):
    sorted_stocks = sorted(results, key=lambda x: x["chgPct"], reverse=True)

    return {
        "stocks": sorted_stocks,
        "top_stocks": sorted_stocks[:5],
        "weak_stocks": sorted_stocks[-5:],
        "rebound_list": [s for s in results if "反彈" in s["strategy"]],
        "selloff_list": [s for s in results if "出貨" in s["strategy"]],
    }


def build_strings(data):
    return {
        "top_str": ", ".join([s["name"] for s in data["top_stocks"]]),
        "weak_str": ", ".join([s["name"] for s in data["weak_stocks"]]),
        "rebound_str": ", ".join([s["name"] for s in data["rebound_list"][:5]]),
        "selloff_str": ", ".join([s["name"] for s in data["selloff_list"][:5]]),
    }


# ========================
# 2️⃣ 主流程
# ========================
def main():
    # 讀股票清單
    df = pd.read_csv("stocks.csv", sep="\t", encoding="utf-8-sig")
    stock_list = df.rename(
        columns={"Ticker": "stock_id", "Name": "name"}
    ).to_dict(orient="records")

    print("🚀 開始分析股票...")
    results = get_full_stock_analysis(stock_list)

    if not results:
        print("⚠️ 無資料")
        return

    # 整理資料
    data = format_output(results)
    text_data = build_strings(data)

    # 檔名
    now_dt = datetime.utcnow() + timedelta(hours=8)
    now_str = now_dt.strftime("%m%d%H%M")
    filename = f"持股_{now_str}.html"

    # URL
    user = "nicole0101"
    repo_name = "StockHolding-report"
    file_url = f"https://{user}.github.io/{repo_name}/{filename}"

    # HTML render
    with open("template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    html_content = template.render(
        stocks=data["stocks"],
        top_stocks=text_data["top_str"],
        weak_stocks=text_data["weak_str"],
        rebound_list=text_data["rebound_str"],
        selloff_list=text_data["selloff_str"],
    )

    # 寫檔
    for f_name in [filename, "index.html"]:
        with open(f_name, "w", encoding="utf-8") as f:
            f.write(html_content)

    print(f"✅ HTML 已生成：{filename}")

    # LINE 通知
    send_line_notify(data, file_url)


# ========================
# 3️⃣ LINE 通知（獨立）
# ========================
def send_line_notify(data, file_url):
    try:
        from line_push import send_line

        top5_str = "\n".join(
            [f"{s['name']}({s['chgPct']}%)" for s in data["top_stocks"]]
        )

        msg = f"""
📊 台股技術分析

🔥 強勢股
{top5_str}

📎 報表連結：
{file_url}
        """

        send_line(msg.strip())
        print("✅ LINE 通知已發送")

    except Exception as e:
        print("LINE 錯誤:", e)


if __name__ == "__main__":
    main()