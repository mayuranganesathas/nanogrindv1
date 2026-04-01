#!/usr/bin/env python3
"""
System cron script — runs every minute via crontab.
Checks timer_queue.json and sends a Telegram ping when the timer expires.
Completely bypasses nanobot/LLM.
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

TIMER_FILE  = Path("/home/mayu/.nanobot/workspace/interview-prep/data/timer_queue.json")
BOT_TOKEN   = "REDACTED_TELEGRAM_BOT_TOKEN"
CHAT_ID     = "1851230297"


def send_message(text: str) -> None:
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    body = json.dumps({"chat_id": CHAT_ID, "text": text}).encode()
    req  = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)


def main() -> None:
    if not TIMER_FILE.exists():
        return

    try:
        entry = json.loads(TIMER_FILE.read_text())
    except Exception:
        return

    expires_at = datetime.fromisoformat(entry["expires_at"])
    if datetime.now(timezone.utc) < expires_at:
        return

    label = entry.get("label", "⏱️ Time's up!")
    TIMER_FILE.unlink(missing_ok=True)

    try:
        send_message(label)
    except Exception as e:
        print(f"Failed to send timer ping: {e}")


if __name__ == "__main__":
    main()
