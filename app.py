import os
import re
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import streamlit as st
from twilio.rest import Client

MOUNTAIN_URL = "https://www.bigbearmountainresort.com/mountain-information"

# Optional fallback (often more scrape-friendly than BBMR's JS page)
FALLBACK_URL = "https://www.onthesnow.com/california/bear-mountain/skireport"

E164_RE = re.compile(r"^\+[1-9]\d{1,14}$")

SNOW_PATTERNS = [
    r"\bsnow\b.*\b(inches|inch|in|accumulation|snowfall)\b",
    r"\bsnow (showers|expected|likely)\b",
    r"\bflurries\b",
]

SUB_FILE = Path("subscribers.json")


# -------------------------
# Storage (local JSON)
# -------------------------
def load_subscribers() -> list[str]:
    if not SUB_FILE.exists():
        return []
    try:
        data = json.loads(SUB_FILE.read_text())
        if isinstance(data, list):
            return [x for x in data if isinstance(x, str)]
    except Exception:
        pass
    return []


def save_subscribers(nums: list[str]) -> None:
    SUB_FILE.write_text(json.dumps(sorted(set(nums)), indent=2))


# -------------------------
# Snow check (Playwright-first)
# -------------------------
def _text_trips_snow(text: str) -> Optional[str]:
    t = " ".join(text.lower().split())
    for pat in SNOW_PATTERNS:
        if re.search(pat, t):
            return f"Matched: {pat}"
    return None


def fetch_rendered_text_playwright(url: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        text = page.inner_text("body")
        browser.close()
        return text


def fetch_plain_text_httpx(url: str) -> str:
    import httpx

    with httpx.Client(timeout=15, headers={"User-Agent": "Mozilla/5.0"}) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.text


def check_snow_signal() -> dict:
    now = datetime.now(timezone.utc).isoformat()

    # 1) Official page via headless browser
    try:
        text = fetch_rendered_text_playwright(MOUNTAIN_URL)
        hit = _text_trips_snow(text)
        if hit:
            return {
                "is_snow_likely": True,
                "reason": f"Official page signal. {hit}",
                "source_url": MOUNTAIN_URL,
                "checked_at_utc": now,
            }
        return {
            "is_snow_likely": False,
            "reason": "No snow signal found on official page text.",
            "source_url": MOUNTAIN_URL,
            "checked_at_utc": now,
        }
    except Exception as e:
        # 2) Fallback to a more scrape-friendly page
        try:
            html = fetch_plain_text_httpx(FALLBACK_URL)
            hit = _text_trips_snow(html)
            if hit:
                return {
                    "is_snow_likely": True,
                    "reason": f"Fallback signal. {hit}",
                    "source_url": FALLBACK_URL,
                    "checked_at_utc": now,
                }
            return {
                "is_snow_likely": False,
                "reason": "No snow signal found on fallback page.",
                "source_url": FALLBACK_URL,
                "checked_at_utc": now,
            }
        except Exception as e2:
            return {
                "is_snow_likely": False,
                "reason": f"Failed to check pages: {e} / {e2}",
                "source_url": FALLBACK_URL,
                "checked_at_utc": now,
            }


# -------------------------
# Twilio
# -------------------------
def send_sms(to_phone: str, body: str) -> None:
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_phone = os.environ["TWILIO_FROM_NUMBER"]

    client = Client(account_sid, auth_token)
    client.messages.create(to=to_phone, from_=from_phone, body=body)


# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Big Bear Snow Alerts (Local)", page_icon="❄️")
st.title("❄️ Big Bear Snow Alerts (Local)")

st.write("Official report page:")
st.write(MOUNTAIN_URL)

if "subscribers" not in st.session_state:
    st.session_state.subscribers = load_subscribers()

if "last_alert_hash" not in st.session_state:
    st.session_state.last_alert_hash = None

phone = st.text_input("Add phone number (E.164)", placeholder="+14155552671")
col1, col2 = st.columns(2)

with col1:
    if st.button("Add"):
        p = phone.strip()
        if not E164_RE.match(p):
            st.error("Invalid phone format. Use E.164 like +14155552671")
        else:
            st.session_state.subscribers = sorted(set(st.session_state.subscribers + [p]))
            save_subscribers(st.session_state.subscribers)
            st.success(f"Added {p}")

with col2:
    if st.button("Clear all"):
        st.session_state.subscribers = []
        save_subscribers([])
        st.warning("Cleared subscriber list.")

st.subheader("Subscribers")
if st.session_state.subscribers:
    st.code("\n".join(st.session_state.subscribers))
else:
    st.info("No subscribers yet.")

st.divider()

st.subheader("Snow check")
cooldown_hours = st.slider("Cooldown between alerts (hours)", 1, 48, 12)
auto_check = st.checkbox("Auto-check while this page is open")
interval_min = st.slider("Auto-check interval (minutes)", 5, 180, 60)

def maybe_send_alert(result: dict):
    if not result["is_snow_likely"]:
        return False

    # Simple dedupe: if reason+source didn't change, don't keep texting
    alert_fingerprint = f"{result['source_url']}|{result['reason']}"
    now_ts = time.time()

    # cooldown gate
    last_sent_ts = st.session_state.get("last_sent_ts", 0)
    if now_ts - last_sent_ts < cooldown_hours * 3600:
        return False

    msg = (
        "❄️ Snow may be on the way at Big Bear.\n"
        f"Check the latest mountain report: {MOUNTAIN_URL}\n"
        f"(Signal source: {result['source_url']})"
    )

    if not st.session_state.subscribers:
        st.warning("Snow signal detected, but there are no subscribers.")
        return False

    sent_any = False
    for num in st.session_state.subscribers:
        send_sms(num, msg)
        sent_any = True

    if sent_any:
        st.session_state.last_sent_ts = now_ts
        st.session_state.last_alert_hash = alert_fingerprint

    return sent_any

if st.button("Run check now"):
    res = check_snow_signal()
    st.json(res)
    if maybe_send_alert(res):
        st.success("Alert sent!")
    else:
        st.info("No alert sent (no snow signal, or cooldown/dedupe).")

if auto_check:
    st.info("Auto-check is ON. Keep this Streamlit tab open.")
    placeholder = st.empty()
    while True:
        res = check_snow_signal()
        with placeholder.container():
            st.write("Last check:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.json(res)
            if maybe_send_alert(res):
                st.success("Alert sent!")
            else:
                st.write("No alert sent.")
        time.sleep(interval_min * 60)
