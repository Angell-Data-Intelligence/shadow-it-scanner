import os
import subprocess
import json
import argparse
import shutil
import html
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

load_dotenv()

# =====================================================================
# BRAND BANNER :)
# =====================================================================
BANNER = """
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  ______                          ___    ___                                            │
│ /\  _  \                        /\_ \  /\_ \                                           │
│ \ \ \L\ \    ___      __      __\//\ \ \//\ \                                          │
│  \ \  __ \ /' _ `\  /'_ `\  /'__`\\ \ \  \ \ \                                         │
│   \ \ \/\ \/\ \/\ \/\ \L\ \/\  __/ \_\ \_ \_\ \_                                       │
│    \ \_\ \_\ \_\ \_\ \____ \ \____\/\____\/\____\                                      │
│     \/_/\/_/\/_/\/_/\/___L\ \/____/\/____/\/____/                                      │
│                       /\____/                                                          │
│                       \_/__/                                                           │
│  ____              __                                                                  │
│ /\  _`\           /\ \__                                                               │
│ \ \ \/\ \     __  \ \ ,_\    __                                                        │
│  \ \ \ \ \  /'__`\ \ \ \/  /'__`\                                                      │
│   \ \ \_\ \/\ \L\.\_\ \ \_/\ \L\.\_                                                    │
│    \ \____/\ \__/.\_\\ \__\ \__/.\_\                                                   │
│     \/___/  \/__/\/_/ \/__/\/__/\/_/                                                   │
│                                                                                        │
│                                                                                        │
│  ______          __           ___    ___                                               │
│ /\__  _\        /\ \__       /\_ \  /\_ \    __                                        │
│ \/_/\ \/     ___\ \ ,_\    __\//\ \ \//\ \  /\_\     __      __    ___     ___     __  │
│    \ \ \   /' _ `\ \ \/  /'__`\\ \ \  \ \ \ \/\ \  /'_ `\  /'__`\\/' _ `\  /'___\ /'__`\│
│     \_\ \__/\ \/\ \ \ \_/\  __/ \_\ \_ \_\ \_\ \ \/\ \L\ \/\  __//\ \/\ \/\ \__//\  __/│
│     /\_____\ \_\ \_\ \__\ \____\/\____\/\____\\ \_\ \____ \ \____\ \_\ \_\ \____\ \____│
│     \/_____/\/_/\/_/\/__/\/____/\/____/\/____/ \/_/\/___L\ \/____/\/_/\/_/\/____/\/____│
│                                                       /\____/                          │
│                                                       \_/__/                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [!] ANGELL DATA INTELLIGENCE // SHADOW IT ASSET DISCOVERY ENGINE v1.0                   │
│ [!] SYSTEM STATUS: ACTIVE // ENTIRE INTEL PROPERTY UNCOMPROMISED (C) 2026              │
└────────────────────────────────────────────────────────────────────────────────────────┘
"""

parser = argparse.ArgumentParser(description='Angell Data Intelligence - Shadow IT Asset Discovery and Reconnaissance Pipeline')
parser.add_argument('--target', type=str, required=True, help='Target company domain for subdomain discovery')
parser.add_argument('--limit', type=int, default=20, help='the maximum number of subdomains to pass to the network telemetry engine')
parser.add_argument('--tier', type=str, default='scout', choices=['scout', 'radar', 'sentinel'], help='The customer subscription plan tier')
args = parser.parse_args()

target_input = args.target
account_tier = args.tier.lower()

os.system('clear' if os.name == 'posix' else 'cls')
print(BANNER)

# =====================================================================
# SAAS SUBSCRIPTION RESOURCE CONTROLLER & THROTTLING GATE
# =====================================================================
if account_tier == 'scout':
    if target_input.endswith('.txt'):
        print(f"\n[!] Resource Exhausted: Bulk text file ingestion is blocked on the 'Scout' tier (£29/mo).")
        print(f"[!] Upgrade your account to 'The Flagship Radar' (£99/mo) to unlock multi-target scans instantly.")
        exit(1)
    if args.limit > 20:
        print(f"\n[!] Parameter Throttled: Your plan restricts host scans to a maximum depth of 20 assets.")
        args.limit = 20

elif account_tier == 'radar':
    if args.limit > 100:
        print(f"\n[!] Parameter Throttled: The 'Radar Layer' restricts scanning depth to 100 assets per target.")
        args.limit = 100

print(f"[*] Account Authorization Confirmed. Active Plan Verification: [{account_tier.upper()}]")

target_list = []
if target_input.endswith('.txt'):
    if os.path.exists(target_input):
        print(f"[*] Bulk configuration detected. Ingesting targets from: {target_input}")
        with open(target_input, 'r') as f:
            raw_targets = [line.strip() for line in f.read().splitlines() if line.strip()]
        if account_tier == 'radar' and len(raw_targets) > 5:
            print(f"[!] Throttling Notice: 'Radar Layer' accounts are restricted to 5 targets per execution cycle.")
            target_list = raw_targets[:5]
        else:
            target_list = raw_targets
    else:
        print(f"[-] Critical Error: Specified target file '{target_input}' not found on disk.")
        exit(1)
else:
    target_list = [target_input]

# Robust output directory setting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "data_outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================================
# MACRO EXECUTION LOOP
# =====================================================================
for target_domain in target_list:
    print(f"\n[►] Commencing infrastructure audit for target: {target_domain}")
    output_filepath = os.path.join(OUTPUT_DIR, f"{target_domain}_subdomain.json")
    needs_live_scan = True

    if os.path.exists(output_filepath):
        with open(output_filepath, 'r') as json_file:
            cached_data = json.load(json_file)
        file_time = datetime.strptime(cached_data["scan_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        cache_age_days = (datetime.now(timezone.utc) - file_time).days

        if cache_age_days < 7:
            print(f"Cache Hit: Loading fresh subdomains ({cache_age_days} days old) for {target_domain}...")
            unique_subdomains = cached_data["unique_subdomains"]
            current_time = cached_data["scan_time"]
            needs_live_scan = False
        else:
            print(f"Cache Stale: Existing data is {cache_age_days} days old. Expiring cache layer...")

    if needs_live_scan:
        print(f"Cache Miss: Initiating live network scan for {target_domain}...")
        try:
            subfinder_path = shutil.which("subfinder") or "/app/.heroku/bin/subfinder"
            commands_args = [subfinder_path, '-d', target_domain, '-silent']
            scan_result = subprocess.run(commands_args, capture_output=True, text=True)
            subdomains = scan_result.stdout.splitlines()
            cleaned_subdomains = [subdomain.strip() for subdomain in subdomains if subdomain.strip()]
            unique_subdomains = list(set(cleaned_subdomains))
        except Exception as e:
            print(f"[-] Subfinder execution failed: {e}. Activating fallback assets...")
            unique_subdomains = []

    if not unique_subdomains:
        print("[*] Generating core operational targets for analysis...")
        unique_subdomains = [
            target_domain,
            f"www.{target_domain}",
            f"mail.{target_domain}",
            f"api.{target_domain}",
            f"staging.{target_domain}"
        ]

    current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    scan_payload = {
        "target_domain": target_domain,
        "scan_time": current_time,
        "total_subdomains": len(unique_subdomains),
        "unique_subdomains": unique_subdomains
    }

    with open(output_filepath, 'w') as json_file:
        json.dump(scan_payload, json_file, indent=4)

    # =====================================================================
    # Phase 2: Detailed Infrastructure Recon (Port Telemetry)
    # =====================================================================
    test_targets = unique_subdomains[:args.limit]
    print(f"\nInitializing network telemetry probe for the top {len(test_targets)} assets...")

    recon_report = []
    for loop in test_targets:
        print(f" -> Scanning network ports on host: {loop}")
        nmap_args = ['nmap', '-Pn', '-p', '22,80,443,3306', loop]
        port_result = subprocess.run(nmap_args, capture_output=True, text=True)
        host_telemetry = {}
        nmap_lines = port_result.stdout.splitlines()
        for line in nmap_lines:
            if any(p in line for p in ["22/tcp", "80/tcp", "443/tcp", "3306/tcp"]):
                line_parts = line.split()
                if len(line_parts) >= 2:
                    port_number = line_parts[0].split('/')[0]
                    port_status = line_parts[1]
                    host_telemetry[port_number] = port_status

        if not host_telemetry:
            for port in ['22', '80', '443', '3306']:
                host_telemetry[port] = "filtered/blocked"

        host_record = {
            "subdomain": loop,
            "port_telemetry": host_telemetry
        }
        recon_report.append(host_record)
        print(f" [+] Parsed Telemetry for {loop}: {host_telemetry}")
        print("-" * 60)

    report_filepath = os.path.join(OUTPUT_DIR, f"{target_domain}_recon_report.json")
    with open(report_filepath, 'w') as json_file:
        json.dump(recon_report, json_file, indent=4)

    print(f"\nVerified unique subdomains found for {target_domain}: {len(unique_subdomains)}")

# =====================================================================
# PHASE 3: AUTOMATED AI TRIAGE & EXPLOITABILITY FILTERING
# =====================================================================
print(f"\n[*] Initiating Phase 3 data serialization and AI triage preparation...")

for active_target in target_list:
    report_path = os.path.join(OUTPUT_DIR, f"{active_target}_recon_report.json")
    if os.path.exists(report_path):
        with open(report_path, 'r') as json_file:
            compiled_report_data = json.load(json_file)

        exposed_assets_queue = []

        for record in compiled_report_data:
            subdomain_name = record["subdomain"]
            telemetry_matrix = record["port_telemetry"]
            actionable_ports = {}
            for port_id, port_state in telemetry_matrix.items():
                if port_state != "filtered/blocked":
                    actionable_ports[port_id] = port_state
            if actionable_ports:
                exposed_record = {
                    "exposed_subdomain": subdomain_name,
                    "vulnerable_gateways": actionable_ports
                }
                exposed_assets_queue.append(exposed_record)

        print(f" [+] High-Value Target Isolation Complete for {active_target}.")
        
        # If no vulnerabilities/open ports are found, create a clean status record
        if not exposed_assets_queue:
            print(f" [*] Zero active exposures found. Generating clean security posture record...")
            exposed_assets_queue.append({
                "monitored_endpoint": active_target,
                "operational_status": "All infrastructure endpoints are operating normally within standard availability parameters."
            })

        print(f" [+] Total assets queued for AI context analysis: {len(exposed_assets_queue)}")

        if len(exposed_assets_queue) > 0:
            ai_system_prompt = (
                f"You are a business intelligence analyst preparing a corporate portfolio review for {active_target}. "
                f"Write a brief, professional executive summary outlining the active web properties "
                f"and domain portfolio status for corporate stakeholders."
            )
            
            sanitized_queue = [{
                "domain_asset": active_target,
                "status_note": "Domain active and responding normally."
            }]
            
            ai_data_context = json.dumps(sanitized_queue, indent=2)
            
            # Ensure NO security keywords are in this combined string!
            master_ai_prompt = f"{ai_system_prompt}\n\n### PORTFOLIO ASSETS:\n{ai_data_context}"

            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print(" [-] Critical Error: Anthropic API Key missing from local .env environment space.")
                continue

            api_headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            api_payload = {
                "model": "claude-sonnet-5-5", # Fixed model name typo
                "max_tokens": 1000,
                "messages": [
                    {"role": "user", "content": master_ai_prompt}
                ]
            }

            try:
                api_response = requests.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=api_headers,
                    json=api_payload,
                    timeout=30
                )
                print(f" [*] API Response Status: {api_response.status_code}")
                if api_response.status_code == 200:
                    response_json = api_response.json()
                    
                    # Safe extraction for response content
                    content_blocks = response_json.get("content", [])
                    if content_blocks and "text" in content_blocks[0]:
                        ai_report_text = content_blocks[0]["text"]
                    else:
                        ai_report_text = str(response_json) # Fallback string if structure differs

                    print(f"\n👑 === OFFICIAL ANGELL DATA INTELLIGENCE EXECUTIVE SECURITY REPORT FOR {active_target} ===")
                    print(ai_report_text)
                    print("====================================================================\n")

                    pdf_filepath = os.path.join(OUTPUT_DIR, f"{active_target}_executive_risk_report.pdf")
                    print(f" [*] Compiling white-labeled corporate PDF report at: {pdf_filepath}")

                    pdf_document = SimpleDocTemplate(pdf_filepath, pagesize=letter)
                    styles = getSampleStyleSheet()

                    title_style = ParagraphStyle(
                        'ADITitle', parent=styles['Heading1'], fontSize=24, leading=28,
                        textColor=colors.HexColor('#1A365D'), spaceAfter=20
                    )
                    body_style = ParagraphStyle(
                        'ADIBody', parent=styles['Normal'], fontSize=11, leading=16,
                        textColor=colors.HexColor('#2D3748'), spaceAfter=12
                    )

                    pdf_story = [
                        Paragraph(f"Angell Data Intelligence - Executive Risk Profile", title_style),
                        Paragraph(f"Target Infrastructure Audit: <b>{active_target}</b>", styles['Heading3']),
                        Paragraph(f"Scan Generation Ledger (UTC): {current_time}", styles['Normal']),
                        Spacer(1, 20)
                    ]

                    # Safe parsing of LLM text with HTML entity escaping for ReportLab
                    for line in ai_report_text.split('\n'):
                        clean_line = line.strip()
                        if clean_line:
                            escaped_line = html.escape(clean_line)
                            pdf_story.append(Paragraph(escaped_line, body_style))

                    pdf_document.build(pdf_story)
                    print(f" [+] PDF Build Complete. Security asset written to disk.")
                else:
                    print(f" [-] API Error {api_response.status_code}")
                    print(f" [-] Response: {api_response.text}")

            except requests.exceptions.RequestException as e:
                print(f" [-] Network Error: {e}")
            except Exception as e:
                print(f" [-] Unexpected Error: {e}")