import json
from datetime import datetime, timedelta

# =========================
# 工具函數
# =========================
def fmt(val, digits=2):
    if val in [None, "-", ""]:
        return "-"
    try:
        return f"{float(val):.{digits}f}"
    except:
        return val

def color_class(val):
    try:
        val = float(val)
        if val > 0:
            return "up"
        elif val < 0:
            return "down"
        else:
            return ""
    except:
        return ""

# =========================
# 主程式
# =========================
def main():

    # 讀資料
    with open("data.json", "r", encoding="utf-8") as f:
        stocks = json.load(f)

    if not stocks:
        print("⚠️ 無資料")
        return

    # 排序（漲幅）
    stocks = sorted(stocks, key=lambda x: x.get("chgPct", 0), reverse=True)

    # Top / Weak
    top5 = stocks[:5]
    weak5 = stocks[-5:]

    # HTML
    rows = ""

    for s in stocks:
        chg_class = color_class(s.get("chgPct"))
        yield_class = color_class(s.get("yield"))

        rows += f"""
        <tr>
            <td>{s.get('name')}</td>
            <td>{s.get('code')}</td>
            <td>{fmt(s.get('price'))}</td>
            <td class="{chg_class}">{fmt(s.get('chgPct'))}%</td>
            <td>{s.get('eps')}</td>
            <td>{s.get('div')}</td>
            <td class="{yield_class}">{fmt(s.get('yield'))}%</td>
            <td>{fmt(s.get('per'))}</td>
            <td>{s.get('strategy')}</td>
        </tr>
        """

    # Summary
    def join_names(lst):
        return ", ".join([f"{x['name']}({fmt(x.get('chgPct'))}%)" for x in lst])

    # 時間
    now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>持股報表</title>

<style>
body {{
    font-family: Arial;
    background: #0f172a;
    color: #e2e8f0;
}}

h1 {{
    text-align: center;
}}

.summary {{
    margin: 20px;
    padding: 10px;
    background: #1e293b;
    border-radius: 10px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    padding: 10px;
    text-align: center;
}}

th {{
    background: #1e293b;
}}

tr:nth-child(even) {{
    background: #020617;
}}

.up {{
    color: #ef4444;
}}

.down {{
    color: #22c55e;
}}

</style>
</head>

<body>

<h1>📊 台股持股報表</h1>
<p style="text-align:center;">更新時間：{now}</p>

<div class="summary">
🔥 強勢股：{join_names(top5)}<br>
⚠ 弱勢股：{join_names(weak5)}
</div>

<table>
<tr>
<th>名稱</th>
<th>代號</th>
<th>價格</th>
<th>漲跌%</th>
<th>EPS</th>
<th>股利</th>
<th>殖利率</th>
<th>PER</th>
<th>策略</th>
</tr>

{rows}

</table>

</body>
</html>
"""

    # 存檔
    filename = f"持股_{datetime.now().strftime('%m%d%H%M')}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("輸出:", filename)


if __name__ == "__main__":
    main()
