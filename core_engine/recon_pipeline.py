# =====================================================================
# PHASE 3: AUTOMATED AI TRIAGE & EXPLOITABILITY FILTERING
# =====================================================================
import datetime
import json
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
OUTPUT_DIR = "/app/data_outputs"
target_list = ["example.com"]

print(f"\n[*] Initiating Phase 3 data serialsation and AI triage preparation...")

for active_target in target_list:
    report_path = os.path.join(OUTPUT_DIR, f"{active_target}_recon_report.json")

    if os.path.exists(report_path):
        print(f"[*] Loading master report infrastructure matrix for: {active_target}")
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
                   
            if actionable_ports or subdomain_name == active_target:
                exposed_record = {
                    "exposed_subdomain": subdomain_name,
                    "vulnerable_gateways": actionable_ports if actionable_ports else {"status": "all monitored ports secure/closed"}
                }
                exposed_assets_queue.append(exposed_record)
               
        print(f"    [+] High-Value Target Isolation Complete for {active_target}.")
        print(f"    [+] Total exposed assets flagged for AI context analysis: {len(exposed_assets_queue)}")

        if len(exposed_assets_queue) > 0:
            print(f"    [*] Assembling AI Context Payload for {active_target}...")
           
            ai_system_prompt = (
                f"You are an elite B2B cybersecurity consulting analyst working for Angell Data Intelligence.\n"
                f"Your target client is: {active_target}.\n"
                f"Your objective is to review the following structured list of exposed public internet assets, "
                f"triage their exploitability, and type a clean, non-technical executive remediation summary for the company board. "
                f"If the data shows all ports are secure/closed, write a highly professional, reassuring 'Clean Bill of Health' statement praising their perimeter controls."
            )
           
            ai_data_context = json.dumps(exposed_assets_queue, indent=2)
            master_ai_prompt = f"{ai_system_prompt}\n\n### TELEMETRY PERIMETER EXPOSURE DATA:\n{ai_data_context}"
           
            print(f"    [*] Transmitting live telemetry context to Anthropic Claude-3.5-Sonnet API...")
            api_key = os.getenv("ANTHROPIC_API_KEY")
           
            if not api_key:
                print("    [-] Critical Error: Anthropic API Key missing from configuration environment vars.")
            else:
                api_headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
               
                api_payload = {
                    "model": "claude-3-5-sonnet-latest",
                    "max_tokens": 1000,
                    "messages": [
                        {"role": "user", "content": master_ai_prompt}
                    ]
                }

                try:
                    api_response = requests.post(
                        "https://anthropic.com",
                        headers=api_headers,
                        json=api_payload,
                        timeout=30
                    )
                   
                    print(f"    [*] API Response Status: {api_response.status_code}")
                   
                    if api_response.status_code == 200:
                        response_json = api_response.json()
                        ai_report_text = response_json["content"][0]["text"]

                        print(f"\n👑 === OFFICIAL ANGELL DATA INTELLIGENCE EXECUTIVE SECURITY REPORT FOR {active_target} ===")
                        print(ai_report_text)
                        print("====================================================================\n")
                       
                        pdf_filepath = f"/app/data_outputs/{active_target}_executive_risk_report.pdf"
                        print(f"    [*] Compiling white-labeled corporate PDF report at: {pdf_filepath}")
                       
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
                       
                        pdf_story = []
                        pdf_story.append(Paragraph(f"Angell Data Intelligence - Executive Risk Profile", title_style))
                        pdf_story.append(Paragraph(f"Target Infrastructure Audit: <b>{active_target}</b>", styles['Heading3']))
                        pdf_story.append(Paragraph(f"Scan Generation Ledger (UTC): {current_time}", styles['Normal']))
                        pdf_story.append(Spacer(1, 20))
                       
                        raw_lines = ai_report_text.split('\n')
                        for line in raw_lines:
                            clean_line = line.strip()
                            if clean_line:
                                pdf_story.append(Paragraph(clean_line, body_style))
                               
                        pdf_document.build(pdf_story)
                        print(f"    [+] PDF Build Complete. Security asset written to disk.")
                       
                    else:
                        print(f"    [-] API Error {api_response.status_code}: {api_response.text}")

                except requests.exceptions.RequestException as e:
                    print(f"    [-] Network Error: {e}")
                except Exception as e:
                    print(f"    [-] Unexpected Error: {e}")
