import requests
import os
import json

TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]

STATE_FILE = "state.json"

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
    print("LINE:", res.status_code, res.text)


# โหลด state (กัน spam)
if os.path.exists(STATE_FILE):
    state = json.load(open(STATE_FILE))
else:
    state = {
        "gbp_alerted": False,
        "usd_alerted": False,
        "jpy_alerted": False
    }

# ดึงค่าเงิน
url = "https://api.exchangerate-api.com/v4/latest/THB"
data = requests.get(url).json()

gbp = 1 / data["rates"]["GBP"]
usd = 1 / data["rates"]["USD"]
jpy_100 = (1 / data["rates"]["JPY"]) * 100

print("GBP:", gbp)
print("USD:", usd)
print("JPY100:", jpy_100)

# =========================
# GBP > 41
# =========================
if gbp > 41:
    if not state["gbp_alerted"]:
        send_line(f"📈 GBP ข้าม 41: {gbp:.2f}")
        state["gbp_alerted"] = True
else:
    state["gbp_alerted"] = False


# =========================
# USD > 35
# =========================
if usd > 35:
    if not state["usd_alerted"]:
        send_line(f"📈 USD ข้าม 35: {usd:.2f}")
        state["usd_alerted"] = True
else:
    state["usd_alerted"] = False


# =========================
# JPY <= 20 (100 yen)
# =========================
if jpy_100 <= 20:
    if not state["jpy_alerted"]:
        send_line(f"📉 100 เยน ต่ำกว่าหรือเท่ากับ 20: {jpy_100:.2f}")
        state["jpy_alerted"] = True
else:
    state["jpy_alerted"] = False


# save state
with open(STATE_FILE, "w") as f:
    json.dump(state, f)
