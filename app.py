import requests
import os

TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]

def send_line(msg):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_ID,
        "messages": [{"type": "text", "text": msg}]
    }
    requests.post(url, headers=headers, json=data)

# ดึงค่าเงิน
url = "https://api.exchangerate-api.com/v4/latest/THB"
data = requests.get(url).json()

gbp = 1 / data["rates"]["GBP"]
jpy_100 = (1 / data["rates"]["JPY"]) * 100

if gbp < 41:
    send_line(f"📉 GBP ต่ำกว่า 41: {gbp:.2f}")

if jpy_100 <= 20.80:
    send_line(f"📉 100 เยน ต่ำกว่า 20.80: {jpy_100:.2f}")
