#!/usr/bin/env python3
"""
Outbound Lead Communicator & Dispatch Engine
Autonomous cold outbound dispatcher for Gold Standard Local SEO.
Supports dry-run preview, test-sends, full SMTP dispatch, and Instantly/Smartlead CSV export.
"""

import os
import sys
import json
import csv
import smtplib
import argparse
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

LEADS_FILE = "crawlspace_leads_sacramento.json"
HISTORY_FILE = "outbound_dispatch_history.json"
DEFAULT_SENDER_NAME = "Justin Davis"
DEFAULT_SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "goldstandardaiagency@gmail.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

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
    if owner_first_name.lower() in ["operations", "client"]:
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

def export_instantly_csv(leads, output_csv="crawlspace_instantly_import.csv"):
    headers = [
        "Email",
        "First Name",
        "Last Name",
        "Company Name",
        "Phone",
        "Website",
        "City",
        "Current Rank",
        "Competitor",
        "Average Ticket",
        "Monthly Missed Calls",
        "Monthly Revenue Bleed",
        "Missing Attributes",
        "Sales Doc URL"
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
                lead.get("email"),
                first,
                last,
                lead.get("business_name"),
                lead.get("phone"),
                lead.get("website"),
                lead.get("city"),
                lead.get("current_maps_status"),
                lead.get("top_competitor_stealing_traffic"),
                f"${ticket:,}",
                missed,
                f"${bleed:,}",
                lead.get("missing_gbp_attributes"),
                "https://www.gslocalseo.com/doc-sales-page"
            ])
    print(f"Exported {len(leads)} leads to Instantly/Smartlead format: {output_csv}")

def preview_campaign(leads):
    print("=" * 70)
    print("GOLD STANDARD COLD OUTBOUND DISPATCH PREVIEW")
    print("=" * 70)
    for idx, lead in enumerate(leads, 1):
        subject, text, _ = generate_email_content(lead)
        print(f"\n--- PROSPECT #{idx}: {lead.get('business_name')} ({lead.get('city')}) ---")
        print(f"To: {lead.get('owner_name')} <{lead.get('email')}> | Tel: {lead.get('phone')}")
        print(f"Subject: {subject}\n")
        print(text)
        print("-" * 70)

def send_email_smtp(to_email, to_name, subject, text_body, html_body):
    if not SMTP_USER or not SMTP_PASS:
        print("[WARNING] SMTP_USER or SMTP_PASS environment variables not set.")
        print("To send live emails, export SMTP_USER and SMTP_PASS (e.g. Gmail App Password).")
        return False, "Missing SMTP credentials"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{DEFAULT_SENDER_NAME} <{DEFAULT_SENDER_EMAIL}>"
    msg["To"] = f"{to_name} <{to_email}>"
    msg["Reply-To"] = DEFAULT_SENDER_EMAIL

    part1 = MIMEText(text_body, "plain")
    part2 = MIMEText(html_body, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(DEFAULT_SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True, "Delivered successfully"
    except Exception as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Gold Standard Cold Outbound Dispatcher")
    parser.add_argument("--preview", action="store_true", help="Preview generated email copy for all leads")
    parser.add_argument("--export-csv", action="store_true", help="Export to Instantly/Smartlead CSV")
    parser.add_argument("--test-send", type=str, help="Send a single test email to a specified recipient")
    parser.add_argument("--send-lead", type=str, help="Send email to a specific business by name")
    parser.add_argument("--send-all", action="store_true", help="Dispatch live emails to all leads (requires SMTP)")
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
        print("1. To send a live test to yourself: python3 outbound_lead_communicator.py --test-send your-email@gmail.com")
        print("2. To dispatch live via Gmail/SMTP: set SMTP_USER and SMTP_PASS, then run with --send-all")
        print("3. Or import crawlspace_instantly_import.csv directly into Instantly.ai / Apollo / HubSpot")
        return

    if args.test_send:
        sample_lead = leads[0]
        subject, text_body, html_body = generate_email_content(sample_lead)
        subject = f"[TEST SEND - {sample_lead['business_name']}] " + subject
        print(f"Sending test email for '{sample_lead['business_name']}' to: {args.test_send}...")
        success, reason = send_email_smtp(args.test_send, "Test Recipient", subject, text_body, html_body)
        if success:
            print("✓ Test email sent successfully!")
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "test_send",
                "recipient": args.test_send,
                "business": sample_lead["business_name"],
                "status": "SENT"
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
        print(f"Sending live email to {target['business_name']} ({target['email']})...")
        success, reason = send_email_smtp(target["email"], target["owner_name"], subject, text_body, html_body)
        if success:
            print(f"✓ Email delivered to {target['email']}")
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "live_single",
                "recipient": target["email"],
                "business": target["business_name"],
                "status": "SENT"
            })
        else:
            print(f"✗ Dispatch failed: {reason}")
        return

    if args.send_all:
        print(f"Starting automated outbound batch for {len(leads)} leads (delay: {args.throttle}s)...")
        for idx, lead in enumerate(leads, 1):
            subject, text_body, html_body = generate_email_content(lead)
            print(f"[{idx}/{len(leads)}] Dispatching to {lead['business_name']} ({lead['email']})...")
            success, reason = send_email_smtp(lead["email"], lead["owner_name"], subject, text_body, html_body)
            record_history({
                "timestamp": datetime.now().isoformat(),
                "mode": "live_batch",
                "recipient": lead["email"],
                "business": lead["business_name"],
                "status": "SENT" if success else f"FAILED: {reason}"
            })
            if success:
                print(f"  ✓ Sent successfully.")
            else:
                print(f"  ✗ Failed: {reason}")
            if idx < len(leads):
                time.sleep(args.throttle)
        print("Batch execution completed. Check outbound_dispatch_history.json for audit log.")

if __name__ == "__main__":
    main()
