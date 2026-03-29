import requests

CHANNEL_ACCESS_TOKEN = "c93ada9fc0998b711795598148326345"
USER_ID = "2009633631"

def send_line(msg):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_ID,
        "messages": [
            {
                "type": "text",
                "text": msg
            }
        ]
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    send_line("📊 今日股票報告已產生")
