import requests
import os

# LINE config
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
    
    res = requests.post(url, headers=headers, json=data)
    print("LINE status:", res.status_code, res.text)


# ดึงค่าเงิน (THB เป็น base)
url = "https://api.exchangerate-api.com/v4/latest/THB"
data = requests.get(url).json()

# ค่าเงิน (THB → currency)
gbp = 1 / data["rates"]["GBP"]
usd = 1 / data["rates"]["USD"]
jpy_100 = (1 / data["rates"]["JPY"]) * 100

print("DEBUG GBP:", gbp)
print("DEBUG USD:", usd)
print("DEBUG JPY100:", jpy_100)

# =========================
# TEST CONDITIONS
# =========================

# GBP test (ตามที่คุณขอ)
if gbp > 41:
    send_line(f"📈 TEST GBP เกิน 41: {gbp:.2f}")

# USD
if usd > 35:
    send_line(f"📈 USD เกิน 35: {usd:.2f}")

# JPY (100 yen)
if jpy_100 <= 20.80:
    send_line(f"📉 100 เยน ≤ 20.80: {jpy_100:.2f}")
