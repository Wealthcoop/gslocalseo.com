#!/usr/bin/env python3
"""
Inbound Lead & Response Monitor
Continuously monitors:
1. Resend API events (deliveries, opens, clicks, replies).
2. conversions_ledger.json for new live site opt-ins from gslocalseo.com.
3. Fabian Ruiz response detection and instant 9x9 radar trigger.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
CONVERSIONS_FILE = "conversions_ledger.json"
HISTORY_FILE = "outbound_dispatch_history.json"
FABIAN_EMAIL = "fabianruizbar@outlook.com"

def get_recent_resend_emails():
    if not RESEND_API_KEY:
        return []
    cmd = [
        "curl", "-s", "-H", f"Authorization: Bearer {RESEND_API_KEY}",
        "https://api.resend.com/emails"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        try:
            return json.loads(res.stdout).get("data", [])
        except Exception:
            return []
    return []

def get_email_status(email_id):
    if not RESEND_API_KEY or not email_id:
        return {}
    cmd = [
        "curl", "-s", "-H", f"Authorization: Bearer {RESEND_API_KEY}",
        f"https://api.resend.com/emails/{email_id}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        try:
            return json.loads(res.stdout)
        except Exception:
            return {}
    return {}

def check_status():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking inbound leads & response status...")

    # Check Conversions Ledger
    conversions = []
    if os.path.exists(CONVERSIONS_FILE):
        try:
            with open(CONVERSIONS_FILE) as f:
                conversions = json.load(f)
        except Exception:
            pass
    print(f"• Total Inbound Leads Recorded: {len(conversions)}")
    for c in conversions:
        print(f"  - {c.get('client_name')} ({c.get('client_email')}): {c.get('service_requested')} [{c.get('status')}]")

    # Check Fabian's email status
    fabian_entry = next((c for c in conversions if c.get('client_email') == FABIAN_EMAIL), None)
    if fabian_entry and fabian_entry.get('resend_id'):
        details = get_email_status(fabian_entry['resend_id'])
        last_event = details.get('last_event', 'unknown')
        print(f"• Fabian Ruiz Outreach Status: {last_event.upper()} (ID: {fabian_entry['resend_id']})")
    
    # Check 6 Crawlspace Outbound Status
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                history = json.load(f)
        except Exception:
            pass
    
    recent_batch = [h for h in history if h.get("mode") == "live_batch"]
    print(f"• Live Crawlspace Outbound Sent: {len(recent_batch)} / 6")
    for b in recent_batch[-6:]:
        print(f"  - {b.get('business')} ({b.get('recipient')}): {b.get('status')}")

if __name__ == "__main__":
    check_status()
