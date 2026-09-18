#!/usr/bin/env python3
"""
Conversion Webhook Server & Next-Step Trigger
Listens for inbound Stripe payments and client audit opt-ins.
Automatically provisions client folders, onboarding briefs, and sends notification alerts.
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import re

PORT = int(os.environ.get("WEBHOOK_PORT", 8085))
CONVERSIONS_FILE = "conversions_ledger.json"
CLIENTS_DIR = "clients"

def load_conversions():
    if os.path.exists(CONVERSIONS_FILE):
        try:
            with open(CONVERSIONS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def record_conversion(data):
    conversions = load_conversions()
    conversions.append(data)
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(conversions, f, indent=2)

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.lower()).strip('_')

def provision_client_workspace(client_name, email, plan, phone=""):
    os.makedirs(CLIENTS_DIR, exist_ok=True)
    slug = slugify(client_name or email.split('@')[0])
    client_path = os.path.join(CLIENTS_DIR, slug)
    os.makedirs(client_path, exist_ok=True)

    checklist_path = os.path.join(client_path, "ONBOARDING_CHECKLIST.md")
    checklist_content = f"""# Client Onboarding Checklist: {client_name}

**Date Activated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Plan Tier**: {plan}
**Client Email**: {email}
**Client Phone**: {phone}

## Phase 1: Access & Telemetry Setup (Hours 0 - 24)
- [ ] Send Welcome SMS & Email to {email}
- [ ] Request Google Business Profile Manager access (goldstandardaiagency@gmail.com)
- [ ] Verify primary GBP category & inject 'Waterproofing Service' secondary
- [ ] Audit existing Google Maps CID & Lat/Lon anchor points

## Phase 2: Local Geo-Grid & Entity Mesh (Days 2 - 7)
- [ ] Generate 9x9 Local Falcon baseline geo-grid benchmark
- [ ] Build 15-mile KML radius cluster with primary & secondary road vectors
- [ ] Inject EXIF/GPS metadata into first batch of 12 project photos
- [ ] Deploy companion PDF authority whitepaper on Traffik Monster catalog

## Phase 3: Speed-to-Lead & Conversion Telemetry (Days 7 - 14)
- [ ] Deploy 60-second automated missed-call SMS failover
- [ ] Setup review generation funnel with direct Google Maps shortlink
- [ ] Schedule Month 1 Progress Telemetry Review Call
"""
    with open(checklist_path, "w") as f:
        f.write(checklist_content)

    print(f"✓ Provisioned client workspace at: {client_path}")
    return client_path

class WebhookHandler(BaseHTTPRequestHandler):
    def _send_response(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_response(200, {"status": "ok"})

    def do_GET(self):
        if self.path == "/status" or self.path == "/":
            conversions = load_conversions()
            leads_count = 0
            if os.path.exists("crawlspace_leads_sacramento.json"):
                with open("crawlspace_leads_sacramento.json") as f:
                    leads_count = len(json.load(f))
            
            self._send_response(200, {
                "system": "Gold Standard Automated Lead & Conversion Engine",
                "status": "ONLINE",
                "timestamp": datetime.now().isoformat(),
                "leads_in_pipeline": leads_count,
                "conversions_count": len(conversions),
                "recent_conversions": conversions[-5:]
            })
        else:
            self._send_response(404, {"error": "Not Found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if self.path == "/webhook/stripe":
            event_type = payload.get("type", "checkout.session.completed")
            data_obj = payload.get("data", {}).get("object", {})
            customer_email = data_obj.get("customer_email") or data_obj.get("customer_details", {}).get("email", "client@unknown.com")
            customer_name = data_obj.get("customer_details", {}).get("name", "New Client")
            amount_total = data_obj.get("amount_total", 29700) / 100.0
            
            plan_name = "$297/mo Core Engine" if amount_total < 400 else "$297/mo + $497 Fast-Track Setup"

            conversion_record = {
                "timestamp": datetime.now().isoformat(),
                "source": "STRIPE_CHECKOUT",
                "event": event_type,
                "client_name": customer_name,
                "client_email": customer_email,
                "amount": amount_total,
                "plan": plan_name
            }
            record_conversion(conversion_record)
            workspace = provision_client_workspace(customer_name, customer_email, plan_name)
            
            self._send_response(200, {
                "status": "SUCCESS",
                "message": f"Client {customer_name} provisioned in {workspace}",
                "conversion": conversion_record
            })

        elif self.path == "/webhook/lead-optin":
            client_name = payload.get("name", "Website Lead")
            client_email = payload.get("email", "unknown@lead.com")
            client_phone = payload.get("phone", "")
            business_name = payload.get("business", client_name)
            
            conversion_record = {
                "timestamp": datetime.now().isoformat(),
                "source": "DOC_SALES_PAGE_OPTIN",
                "client_name": client_name,
                "business_name": business_name,
                "client_email": client_email,
                "client_phone": client_phone,
                "notes": payload.get("notes", "Requested 3-Pack Gap Analysis")
            }
            record_conversion(conversion_record)
            workspace = provision_client_workspace(business_name, client_email, "Audit & Consultation", phone=client_phone)
            
            self._send_response(200, {
                "status": "SUCCESS",
                "message": "Lead received and onboarding checklist generated",
                "record": conversion_record
            })
        else:
            self._send_response(404, {"error": "Invalid webhook path"})

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    print(f"Conversion Webhook Server running on port {PORT}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
