#!/usr/bin/env python3
"""
Outbound Lead Communicator & Dispatch Engine
Autonomous cold outbound dispatcher for Gold Standard Local SEO.
Supports Resend API, direct SMTP, dry-run previews, test-sends, and Instantly CSV export.
"""

import os
import sys
import json
import csv
import smtplib
import argparse
import time
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load environment variables from .env if present
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)

LEADS_FILE = "crawlspace_leads_sacramento.json"
HISTORY_FILE = "outbound_dispatch_history.json"
DEFAULT_SENDER_NAME = "Justin Davis"
DEFAULT_SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "justin@goldstandard.monster")
DEFAULT_REPLY_TO = os.environ.get("REPLY_TO", "goldstandardaiagency@gmail.com")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.resend.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "resend")
SMTP_PASS = os.environ.get("SMTP_PASS", RESEND_API_KEY)

def load_leads():
    if not os.path.exists(LEADS_FILE):
        print(f"Error: {LEADS_FILE} not found.")
        sys.exit(1)
    with open(LEADS_FILE, "r") as f:
        return json.load(f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def record_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_email_content(lead):
    # Editorial voice: 70% Alex Hormozi (math, margins, clarity) + 30% Stephen Covey (stewardship, win-win)
    owner_first_name = lead.get("owner_name", "there").split()[0]
    if owner_first_name.lower() in ["operations", "client", "commercial", "regional"]:
        greeting = f"Hey {lead.get('business_name')} team,"
    else:
        greeting = f"Hey {owner_first_name},"

    business = lead.get("business_name")
    city = lead.get("city")
    ticket = lead.get("avg_ticket", 8500)
    current_status = lead.get("current_maps_status")
    missed_calls = lead.get("monthly_missed_calls", 5)
    competitor = lead.get("top_competitor_stealing_traffic", "the top 3-pack")
    monthly_bleed = ticket * missed_calls
    flaws = lead.get("missing_gbp_attributes", "missing category optimization")

    subject = f"Quick question regarding {business}'s Google Maps pin on {city} crawl space jobs"

    plain_text = f"""{greeting}

Look at the math:

A standard crawlspace encapsulation or vapor barrier job in {city} averages ${ticket:,}.

Right now, {business} is sitting at {current_status}.

Because you are outside the top 3-Pack, Google is handing roughly {missed_calls} high-intent emergency calls every single month directly to {competitor}.

That is roughly ${monthly_bleed:,} a month in gross revenue walking out the door to a competitor who doesn't do better work than you—they just have a tighter Google Maps geo-grid.

The reason you aren't in the #1 spot isn't because you need more backlinks. {flaws}

I put together a confidential 2-page breakdown showing the exact map cutoff points and how we move {business} into the top 3 spots within 60 to 90 days:

👉 https://www.gslocalseo.com/doc-sales-page

Zero sales pitch. No 45-minute slide deck. Just open the breakdown, look at the math, and see if it makes sense for your business.

Best regards,

Justin Davis
Founder & Lead Telemetry Architect
Gold Standard Local SEO | Folsom HQ
Direct Office: (916) 234-3457
705 Gold Lake Dr, Suite 250, Folsom CA 95630
https://www.gslocalseo.com
"""

    html_content = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; line-height: 1.6; color: #1e293b;">
  <p>{greeting}</p>
  
  <p><strong>Look at the math:</strong></p>
  
  <p>A standard crawlspace encapsulation or vapor barrier job in {city} averages <strong>${ticket:,}</strong>.</p>
  
  <p>Right now, {business} is sitting at <em>{current_status}</em>.</p>
  
  <p>Because you are outside the top 3-Pack, Google is handing roughly <strong>{missed_calls} high-intent emergency calls</strong> every single month directly to <strong>{competitor}</strong>.</p>
  
  <p style="padding: 12px 16px; background-color: #fef2f2; border-left: 4px solid #ef4444; border-radius: 4px; color: #991b1b;">
    That is roughly <strong>${monthly_bleed:,} a month in gross revenue</strong> walking out the door to a competitor who doesn't do better work than you—they just have a tighter Google Maps geo-grid.
  </p>
  
  <p>The reason you aren't in the #1 spot isn't because you need more backlinks. {flaws}</p>
  
  <p>I put together a confidential 2-page breakdown showing the exact map cutoff points and how we move {business} into the top 3 spots within 60 to 90 days:</p>
  
  <p style="margin: 24px 0;">
    <a href="https://www.gslocalseo.com/doc-sales-page" style="background-color: #0f172a; color: #ffffff; padding: 12px 20px; text-decoration: none; border-radius: 6px; font-weight: 600; display: inline-block;">
      👉 View {business} Telemetry Breakdown & SOP
    </a>
  </p>
  
  <p>Zero sales pitch. No 45-minute slide deck. Just open the breakdown, look at the math, and see if it makes sense for your business.</p>
  
  <br>
  <div style="border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 13px; color: #64748b;">
    <strong style="color: #0f172a; font-size: 14px;">Justin Davis</strong><br>
    Founder & Lead Telemetry Architect<br>
    <strong>Gold Standard Local SEO</strong> | Folsom HQ<br>
    Direct Office: <a href="tel:9162343457" style="color: #2563eb; text-decoration: none;">(916) 234-3457</a><br>
    705 Gold Lake Dr, Suite 250, Folsom CA 95630<br>
    <a href="https://www.gslocalseo.com" style="color: #2563eb; text-decoration: none;">https://www.gslocalseo.com</a>
  </div>
</body>
</html>
"""
    return subject, plain_text, html_content

def send_via_resend_api(to_email, to_name, subject, text_body, html_body):
    if not RESEND_API_KEY:
        return False, "RESEND_API_KEY is not configured in .env or environment"

    payload = {
        "from": f"{DEFAULT_SENDER_NAME} <{DEFAULT_SENDER_EMAIL}>",
        "to": [to_email],
        "reply_to": DEFAULT_REPLY_TO,
        "subject": subject,
        "text": text_body,
        "html": html_body
    }

    cmd = [
        "curl", "-s", "-X", "POST", "https://api.resend.com/emails",
        "-H", f"Authorization: Bearer {RESEND_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return False, f"Curl error: {res.stderr}"

    try:
        resp_data = json.loads(res.stdout)
        if "id" in resp_data:
            return True, f"Delivered (Resend ID: {resp_data['id']})"
        else:
            return False, f"Resend API Error: {resp_data.get('message', res.stdout)}"
    except Exception as e:
        return False, f"Response parsing error: {e} ({res.stdout})"

def export_instantly_csv(leads, output_csv="crawlspace_instantly_import.csv"):
    headers = [
        "Email", "First Name", "Last Name", "Company Name", "Phone",
        "Website", "City", "Current Rank", "Competitor", "Average Ticket",
        "Monthly Missed Calls", "Monthly Revenue Bleed", "Missing Attributes", "Sales Doc URL"
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for lead in leads:
            names = lead.get("owner_name", "Team").split()
            first = names[0]
            last = " ".join(names[1:]) if len(names) > 1 else ""
            ticket = lead.get("avg_ticket", 8500)
            missed = lead.get("monthly_missed_calls", 5)
            bleed = ticket * missed
            writer.writerow([
                lead.get("email"), first, last, lead.get("business_name"),
                lead.get("phone"), lead.get("website"), lead.get("city"),
                lead.get("current_maps_status"), lead.get("top_competitor_stealing_traffic"),
                f"${ticket:,}", missed, f"${bleed:,}", lead.get("missing_gbp_attributes"),
                "https://www.gslocalseo.com/doc-sales-page"
            ])
    print(f"Exported {len(leads)} leads to Instantly/Smartlead format: {output_csv}")

def preview_campaign(leads):
    print("=" * 70)
    print("GOLD STANDARD COLD OUTBOUND DISPATCH PREVIEW")
    print(f"Sender: {DEFAULT_SENDER_NAME} <{DEFAULT_SENDER_EMAIL}>")
    print(f"Reply-To: {DEFAULT_REPLY_TO}")
    print("=" * 70)
    for idx, lead in enumerate(leads, 1):
        subject, text, _ = generate_email_content(lead)
        print(f"\n--- PROSPECT #{idx}: {lead.get('business_name')} ({lead.get('city')}) ---")
        print(f"To: {lead.get('owner_name')} <{lead.get('email')}> | Tel: {lead.get('phone')}")
        print(f"Subject: {subject}\n")
        print(text)
        print("-" * 70)

def main():
    parser = argparse.ArgumentParser(description="Gold Standard Cold Outbound Dispatcher (Resend API Engine)")
    parser.add_argument("--preview", action="store_true", help="Preview generated email copy for all leads")
    parser.add_argument("--export-csv", action="store_true", help="Export to Instantly/Smartlead CSV")
    parser.add_argument("--test-send", type=str, help="Send a single test email to a specified recipient")
    parser.add_argument("--send-lead", type=str, help="Send email to a specific business by name")
    parser.add_argument("--send-all", action="store_true", help="Dispatch live emails to all leads via Resend")
    parser.add_argument("--throttle", type=int, default=15, help="Seconds delay between emails (default 15s)")

    args = parser.parse_args()
    leads = load_leads()

    if args.export_csv:
        export_instantly_csv(leads)
        return

    if args.preview or (not args.test_send and not args.send_lead and not args.send_all):
        preview_campaign(leads)
        export_instantly_csv(leads)
        print("\n[NEXT STEPS FOR DISPATCH]")
        print("1. To send a live test to yourself: python3 outbound_lead_communicator.py --test-send goldstandardaiagency@gmail.com")
        print("2. To dispatch a specific contractor: python3 outbound_lead_communicator.py --send-lead 'Critter Bros'")
        print("3. To dispatch the full batch: python3 outbound_lead_communicator.py --send-all")
        return

    if args.test_send:
        sample_lead = leads[0]
        subject, text_body, html_body = generate_email_content(sample_lead)
        subject = f"[TEST PREVIEW - {sample_lead['business_name']}] " + subject
        print(f"Sending test email from '{DEFAULT_SENDER_NAME} <{DEFAULT_SENDER_EMAIL}>' to: {args.test_send}...")
        success, reason = send_via_resend_api(args.test_send, "Justin Davis", subject, text_body, html_body)
        if success:
            print(f"✓ {reason}")
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "test_send",
                "recipient": args.test_send,
                "sender": DEFAULT_SENDER_EMAIL,
                "business": sample_lead["business_name"],
                "status": "SENT",
                "details": reason
            })
        else:
            print(f"✗ Dispatch failed: {reason}")
        return

    if args.send_lead:
        target = next((l for l in leads if args.send_lead.lower() in l["business_name"].lower()), None)
        if not target:
            print(f"Could not find lead matching: {args.send_lead}")
            return
        subject, text_body, html_body = generate_email_content(target)
        print(f"Sending live email to {target['business_name']} ({target['email']}) from {DEFAULT_SENDER_EMAIL}...")
        success, reason = send_via_resend_api(target["email"], target["owner_name"], subject, text_body, html_body)
        if success:
            print(f"✓ Email delivered to {target['email']} ({reason})")
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "live_single",
                "recipient": target["email"],
                "sender": DEFAULT_SENDER_EMAIL,
                "business": target["business_name"],
                "status": "SENT",
                "details": reason
            })
        else:
            print(f"✗ Dispatch failed: {reason}")
        return

    if args.send_all:
        print(f"Starting automated outbound batch for {len(leads)} leads via Resend (delay: {args.throttle}s)...")
        for idx, lead in enumerate(leads, 1):
            subject, text_body, html_body = generate_email_content(lead)
            print(f"[{idx}/{len(leads)}] Dispatching to {lead['business_name']} ({lead['email']})...")
            success, reason = send_via_resend_api(lead["email"], lead["owner_name"], subject, text_body, html_body)
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "live_batch",
                "recipient": lead["email"],
                "sender": DEFAULT_SENDER_EMAIL,
                "business": lead["business_name"],
                "status": "SENT" if success else f"FAILED: {reason}",
                "details": reason
            })
            if success:
                print(f"  ✓ Sent successfully ({reason})")
            else:
                print(f"  ✗ Failed: {reason}")
            if idx < len(leads):
                time.sleep(args.throttle)
        print("Batch execution completed. Check outbound_dispatch_history.json for audit log.")

if __name__ == "__main__":
    main()
