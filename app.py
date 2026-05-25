import requests
import os
import json
import sys

TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]

STATE_FILE = "state.json"

# =========================
# ส่ง LINE
# =========================
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

    try:
        res = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=15
        )

        print("LINE STATUS:", res.status_code)
        print("LINE RESPONSE:", res.text)

    except Exception as e:
        print("LINE ERROR:", str(e))


# =========================
# TEST MODE
# =========================
if len(sys.argv) > 1 and sys.argv[1] == "test":
    send_line("✅ TEST MESSAGE FROM GITHUB ACTION")
    sys.exit(0)


# =========================
# โหลด state
# =========================
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {
        "gbp_alerted": False,
        "usd_alerted": False,
        "jpy_alerted": False
    }

print("CURRENT STATE:", state)


# =========================
# ดึงค่าเงิน
# =========================
url = "https://api.exchangerate-api.com/v4/latest/THB"

try:
    data = requests.get(url, timeout=15).json()

except Exception as e:
    print("API ERROR:", str(e))
    sys.exit(1)


# =========================
# คำนวณค่าเงิน
# =========================
gbp = 1 / data["rates"]["GBP"]
usd = 1 / data["rates"]["USD"]
jpy_100 = (1 / data["rates"]["JPY"]) * 100

print("GBP:", gbp)
print("USD:", usd)
print("JPY100:", jpy_100)


# =========================
# GBP < 41
# =========================
if gbp < 41:

    print("GBP CONDITION MET")

    if not state["gbp_alerted"]:

        send_line(f"📉 GBP ต่ำกว่า 41: {gbp:.2f}")

        state["gbp_alerted"] = True

else:
    print("GBP RESET")
    state["gbp_alerted"] = False


# =========================
# USD > 35
# =========================
if usd > 35:

    print("USD CONDITION MET")

    if not state["usd_alerted"]:

        send_line(f"📈 USD ข้าม 35: {usd:.2f}")

        state["usd_alerted"] = True

else:
    print("USD RESET")
    state["usd_alerted"] = False


# =========================
# JPY <= 20
# =========================
if jpy_100 <= 20:

    print("JPY CONDITION MET")

    if not state["jpy_alerted"]:

        send_line(
            f"📉 100 เยน ต่ำกว่าหรือเท่ากับ 20: {jpy_100:.2f}"
        )

        state["jpy_alerted"] = True

else:
    print("JPY RESET")
    state["jpy_alerted"] = False


# =========================
# save state
# =========================
with open(STATE_FILE, "w") as f:
    json.dump(state, f)

print("NEW STATE:", state)
