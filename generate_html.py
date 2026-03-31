import json
from jinja2 import Template
from datetime import datetime, timedelta

def main():
    # ===== 排序 =====
    priority = {
        "強勢反彈🚀": 5,
        "反彈🔥": 4,
        "觀察": 3,
        "整理": 2,
        "出貨⚠": 1,
        "主力出貨💀": 0
    }

    sorted_stocks = sorted(
        results,
        key=lambda x: (priority.get(x["strategy"], 0), x["chgPct"]),
        reverse=True
    )

    # ===== Top / Weak =====
    top_names = ", ".join([s["name"] for s in sorted_stocks[:5]])
    weak_names = ", ".join([s["name"] for s in sorted_stocks[-5:]])

    rebound_list = [s["name"] for s in results if "反彈" in s["strategy"]]
    selloff_list = [s["name"] for s in results if "出貨" in s["strategy"]]

    # ===== HTML =====
    with open("template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    html = template.render(
        stocks=sorted_stocks,
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


if __name__ == "__main__":
    main()
