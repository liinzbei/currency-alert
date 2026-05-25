import requests
import os
import json
import sys
from datetime import datetime, timedelta

TOKEN = os.environ["LINE_TOKEN"]
USER_ID = os.environ["USER_ID"]

STATE_FILE = "state.json"

ALERT_COOLDOWN_HOURS = 6


# =========================
# SEND LINE
# =========================
def send_line(msg):

    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {TOKEN}",
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
# LOAD STATE
# =========================
if os.path.exists(STATE_FILE):

    with open(STATE_FILE, "r") as f:

        state = json.load(f)

else:

    state = {
        "last_rates": {
            "usd": None,
            "gbp": None,
            "jpy": None
        },

        "alerts": {},

        "last_summary_date": None
    }


# =========================
# HELPERS
# =========================
def can_alert(key):

    now = datetime.utcnow()

    last_time = state["alerts"].get(key)

    if not last_time:

        return True

    last_dt = datetime.fromisoformat(last_time)

    return (
        now - last_dt
    ) > timedelta(hours=ALERT_COOLDOWN_HOURS)


def mark_alert(key):

    state["alerts"][key] = (
        datetime.utcnow().isoformat()
    )


# =========================
# GET FX DATA
# =========================
url = "https://api.exchangerate-api.com/v4/latest/THB"

try:

    data = requests.get(
        url,
        timeout=15
    ).json()

except Exception as e:

    print("API ERROR:", str(e))

    sys.exit(1)


# =========================
# CALCULATE RATES
# =========================
usd = 1 / data["rates"]["USD"]

gbp = 1 / data["rates"]["GBP"]

jpy_100 = (
    1 / data["rates"]["JPY"]
) * 100


print("USD:", usd)
print("GBP:", gbp)
print("JPY100:", jpy_100)


# =========================
# PREVIOUS VALUES
# =========================
prev_usd = state["last_rates"]["usd"]


# =========================
# USD TREND DETECTION
# =========================
if prev_usd:

    diff = usd - prev_usd

    if abs(diff) >= 0.3:

        if diff > 0:

            send_line(
                f"📈 USD กำลังขึ้นแรง\n"
                f"{prev_usd:.2f} → {usd:.2f}\n"
                f"(+{diff:.2f})"
            )

        else:

            send_line(
                f"📉 USD กำลังลงแรง\n"
                f"{prev_usd:.2f} → {usd:.2f}\n"
                f"({diff:.2f})"
            )


# =========================
# USD BUY ZONES
# =========================
usd_buy_levels = [32, 31, 30, 29]

for level in usd_buy_levels:

    key = f"usd_below_{level}"

    if usd < level and can_alert(key):

        if level == 29:

            send_line(
                f"👑 EXTREME USD BUY ZONE 👑\n"
                f"USD ต่ำกว่า 29 แล้ว\n"
                f"ตอนนี้: {usd:.2f} THB"
            )

        else:

            send_line(
                f"🚨💵 USD BUY SIGNAL 🚨\n"
                f"USD ต่ำกว่า {level}\n"
                f"ตอนนี้: {usd:.2f} THB"
            )

        mark_alert(key)


# =========================
# USD SELL ZONES
# =========================
usd_sell_levels = [34, 35, 36, 37]

for level in usd_sell_levels:

    key = f"usd_above_{level}"

    if usd > level and can_alert(key):

        if level == 37:

            send_line(
                f"☠️ EXTREME USD SELL ZONE ☠️\n"
                f"USD ข้าม 37 แล้ว\n"
                f"ตอนนี้: {usd:.2f} THB"
            )

        else:

            send_line(
                f"🔥💰 USD SELL SIGNAL 🔥\n"
                f"USD ข้าม {level}\n"
                f"ตอนนี้: {usd:.2f} THB"
            )

        mark_alert(key)


# =========================
# GBP TRAVEL ALERT
# =========================
if gbp < 42 and can_alert("gbp_low"):

    send_line(
        f"🇬🇧✈️ GBP ต่ำกว่า 42 แล้ว\n"
        f"ตอนนี้: {gbp:.2f} THB"
    )

    mark_alert("gbp_low")


# =========================
# JPY TRAVEL ALERT
# =========================
if jpy_100 <= 20 and can_alert("jpy_low"):

    send_line(
        f"🇯🇵🛍️ เยนลงแล้ว\n"
        f"100 เยน = {jpy_100:.2f} THB"
    )

    mark_alert("jpy_low")


# =========================
# DAILY SUMMARY 9AM TH
# =========================
now_utc = datetime.utcnow()

thai_hour = (
    now_utc.hour + 7
) % 24

today = now_utc.date().isoformat()

if (
    thai_hour == 9
    and state["last_summary_date"] != today
):

    send_line(
        f"☀️ FX Morning Report\n\n"
        f"USD: {usd:.2f} THB\n"
        f"GBP: {gbp:.2f} THB\n"
        f"100 JPY: {jpy_100:.2f} THB"
    )

    state["last_summary_date"] = today


# =========================
# SAVE CURRENT RATES
# =========================
state["last_rates"]["usd"] = usd

state["last_rates"]["gbp"] = gbp

state["last_rates"]["jpy"] = jpy_100


# =========================
# SAVE STATE
# =========================
with open(STATE_FILE, "w") as f:

    json.dump(state, f)


print("STATE SAVED")
