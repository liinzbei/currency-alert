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

gbp = data["rates"]["GBP"]
usd = 1 / data["rates"]["USD"]
jpy_100 = (1 / data["rates"]["JPY"]) * 100

# GBP
if gbp > 41:
    send_line(f"📉 GBP ลดลงเหลือ {gbp:.2f}")

# USD
if usd > 35:
    send_line(f"📈 USD สูงขึ้นเกิน 35: {usd:.2f}")

# JPY (100 yen)
if jpy_100 <= 20:
    send_line(f"📉 100 เยน ลดลงเหลือ {jpy_100:.2f}")
