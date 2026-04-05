import pandas as pd
import json
import os
from datetime import datetime, timedelta
from jinja2 import Template
from data import get_full_stock_analysis


def main():
    # 1. 讀取並分析資料
    df = pd.read_csv("stocks.csv", sep="\t", encoding="utf-8-sig")
    stock_list = df.rename(
        columns={"Ticker": "stock_id", "Name": "name"}).to_dict(orient="records")

    print("🚀 開始分析股票...")
    results = get_full_stock_analysis(stock_list)
    if not results:
        print("⚠️ 無資料")
        return

    # 2. 資料處理 (排序與篩選)
    sorted_stocks = sorted(results, key=lambda x: x["chgPct"], reverse=True)
    rebound_list = [s["name"] for s in results if "反彈" in s["strategy"]]
    selloff_list = [s["name"] for s in results if "出貨" in s["strategy"]]

    # 3. 檔案與 URL 設定
    now_dt = datetime.utcnow() + timedelta(hours=8)
    now_str = now_dt.strftime("%m%d%H%M")
    filename = f"持股_{now_str}.html"

    user = "nicole0101"
    repo_name = "StockHolding-report"
    file_url = f"https://{user}.github.io/{repo_name}/{filename}"

    # 4. 生成 HTML
    with open("template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    html_content = template.render(
        stocks=sorted_stocks,
        top_stocks=", ".join([s["name"] for s in sorted_stocks[:5]]),
        weak_stocks=", ".join([s["name"] for s in sorted_stocks[-5:]]),
        rebound_list=", ".join(rebound_list[:5]),
        selloff_list=", ".join(selloff_list[:5])
    )

    for f_name in [filename, "index.html"]:
        with open(f_name, "w", encoding="utf-8") as f:
            f.write(html_content)

    # 5. LINE 通知
    try:
        from line_push import send_line
        top5_str = "\n".join(
            [f"{s['name']}({s['chgPct']}%)" for s in sorted_stocks[:5]])
        msg = f"📊 台股技術分析\n\n🔥 強勢股\n{top5_str}\n\n📎 報表連結：\n{file_url}"
        send_line(msg.strip())
        print("✅ LINE 通知已發送")
    except Exception as e:
        print("LINE 錯誤:", e)


if __name__ == "__main__":
    main()