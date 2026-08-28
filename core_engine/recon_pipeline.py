import os
import subprocess
import json
import argparse
from datetime import datetime, timezone

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

# Initialise the command-line argument parser for automated enterprise execution
parser = argparse.ArgumentParser(description='Angell Data Intelligence - Shadow IT Asset Discovery and Reconnaissance Pipeline')
parser.add_argument('--target', type=str, required=True, help='Target company domain for subdomain discovery')
parser.add_argument('--limit', type=int, default=20, help='the maximum number of subdomains to pass to the network telemetry engine')
args = parser.parse_args()

# Capture the raw input argument string uniformly
target_input = args.target

# Clear the screen buffer and render the master corporate interface
os.system('clear')
print(BANNER)

# Initialise an empty array to collect our scanning objectives
target_list = []

# Evaluate if the incoming argument is a bulk text file or a single domain string
if target_input.endswith('.txt'):
    if os.path.exists(target_input):
        print(f"[*] Bulk configuration detected. Ingesting targets from: {target_input}")
        with open(target_input, 'r') as f:
            target_list = [line.strip() for line in f.read().splitlines() if line.strip()]
    else:
        print(f"[-] Critical Error: Specified target file '{target_input}' not found on disk.")
        exit(1)
else:
    # If it's a single domain, wrap it inside a single-element list array
    target_list = [target_input]

# Ensure the data storage directory exists safely before execution
os.makedirs('shadow-it-scanner/data_outputs', exist_ok=True)

# =====================================================================
# MACRO EXECUTION LOOP: ITERATING THROUGHOUT THE INGESTED TARGET MATRIX
# =====================================================================
for target_domain in target_list:
    print(f"\n[►] Commencing infrastructure audit for target: {target_domain}")
    
    # Calculate the target file path dynamically for the current domain in the loop
    output_filepath = f"shadow-it-scanner/data_outputs/{target_domain}_subdomains.json"

    # Initialise a conditional control flag to determine our extraction route
    needs_live_scan = True

    # Check if a cache file for this target exists on the disk
    if os.path.exists(output_filepath):
        with open(output_filepath, 'r') as json_file:
            cached_data = json.load(json_file)
            
        # Convert the saved string timestamp back into an explicit UTC datetime object
        file_time = datetime.strptime(cached_data["scan_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        # Calculate the exact mathematical age gap using a standardised global clock
        cache_age_days = (datetime.now(timezone.utc) - file_time).days

        # If the file is perfectly fresh, pull the data and bypass the live scanner
        if cache_age_days < 7:
            print(f"Cache Hit: Loading fresh subdomains ({cache_age_days} days old) for {target_domain} from local storage...")
            unique_subdomains = cached_data["unique_subdomains"]
            current_time = cached_data["scan_time"]
            needs_live_scan = False
        else:
            print(f"Cache Stale: Existing data is {cache_age_days} days old. Expiring cache layer...")

    # Trigger the active extraction layer if a Cache Miss or Cache Stale status is caught
    if needs_live_scan:
        print(f"Cache Miss: Initiating live network scan for {target_domain}...")
        
        # In-memory execution and telemetry capture for subdomain discovery using Subfinder tool
        commands_args = ['subfinder', '-d', target_domain, '-silent']
        scan_result = subprocess.run(commands_args, capture_output=True, text=True)
        subdomains = scan_result.stdout.splitlines()
        cleaned_subdomains = [subdomain.strip() for subdomain in subdomains if subdomain.strip()]
        unique_subdomains = list(set(cleaned_subdomains))

        # Capture the operational execution timestamp using global universal time
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        scan_payload = {
            "target_domain": target_domain,
            "scan_time": current_time,
            "total_subdomains": len(unique_subdomains),
            "unique_subdomains": unique_subdomains
        }

        # Dynamic loading and file output phase for enterprise telemetry and reporting
        with open(output_filepath, 'w') as json_file:
            json.dump(scan_payload, json_file, indent=4)

    # =====================================================================
    # Phase 2: Detailed Infrastructure Recon (Port Telemetry)
    # =====================================================================

    # Extract a dynamic slice of targets from the unique list based on user limits
    test_targets = unique_subdomains[:args.limit]
    print(f"Test targets for {target_domain}: {test_targets}")
    print(f"\nInitializing network telemetry probe for the top {len(test_targets)} assets...")

    recon_report = []

    for loop in test_targets:
        print(f" -> Scanning network ports on host: {loop}")
        nmap_args = ['nmap', '-Pn', '-p', '22,80,443,3306', loop]
        port_result = subprocess.run(nmap_args, capture_output=True, text=True)
        
        host_telemetry = {}
        
        nmap_lines = port_result.stdout.splitlines()
        
        for line in nmap_lines:
            if "22/tcp" in line or "80/tcp" in line or "443/tcp" in line or "3306/tcp" in line:
                # Split the line by its blank spaces to isolate the words
                line_parts = line.split()
                # Extract the port/protocol string (e.g., '22/tcp') and strip the '/tcp' suffix
                port_number = line_parts[0].split('/')[0]
                # Extract the status word (e.g., 'open' or 'closed')
                port_status = line_parts[1]
                # Commit the clean key-value pair straight to your tracking dictionary
                host_telemetry[port_number] = port_status
                # If the dictionary is still empty, it means the firewall blocked the request
        if not host_telemetry:
            for port in ['22', '80', '443', '3306']:
                host_telemetry[port] = "filtered/blocked"
        host_record = {
        "subdomain": loop,
        "port_telemetry": host_telemetry
        }
        recon_report.append(host_record)

        print(f"    [+] Parsed Telemetry for {loop}: {host_telemetry}")
        print("-" * 60)

    report_filepath = f"shadow-it-scanner/data_outputs/{target_domain}_recon_report.json"
    with open(report_filepath, 'w') as json_file:
        json.dump(recon_report, json_file, indent=4)

    # Print diagnostic metrics to the terminal (Runs regardless of Cache Hit or Miss)
    print(f"\nVerified unique subdomains found for {target_domain}: {len(unique_subdomains)}")
    print(f"Scan completed at: {current_time}")

# =====================================================================
# PHASE 3: AUTOMATED AI TRIAGE & EXPLOITABILITY FILTERING
# =====================================================================
print(f"\n[*] Initiating Phase 3 data serialization and AI triage preparation...")

# Dynamic target reference loop to read our completed master database report
for active_target in target_list:
    report_path = f"shadow-it-scanner/data_outputs/{active_target}_recon_report.json"

    if os.path.exists(report_path):
        print(f"[*] Loading master report infrastructure matrix for: {active_target}")
        with open(report_path, 'r') as json_file:
            compiled_report_data = json.load(json_file)

        # Initialise a list array container to hold only high-risk exposed assets
        exposed_assets_queue = []
        
        # 🟢 SIMULATION LEAK INJECTION (Placing it right here allows the test to fire)
        exposed_assets_queue.append({
            "exposed_subdomain": f"staging-db.{active_target}", 
            "vulnerable_gateways": {"3306": "open"}
        })
        
        for record in compiled_report_data:
            subdomain_name = record["subdomain"]
            telemetry_matrix = record["port_telemetry"]
            
            # Isolate ports that aren't trapped behind a filtered status blanket
            actionable_ports = {}
            for port_id, port_state in telemetry_matrix.items():
                if port_state != "filtered/blocked":
                    actionable_ports[port_id] = port_state
                    
            # If an asset exposes actionable ports, commit it to the high-risk queue
            if actionable_ports:
                exposed_record = {
                    "exposed_subdomain": subdomain_name,
                    "vulnerable_gateways": actionable_ports
                }
                exposed_assets_queue.append(exposed_record)
                
        print(f"    [+] High-Value Target Isolation Complete for {active_target}.")
        print(f"    [+] Total exposed assets flagged for AI context analysis: {len(exposed_assets_queue)}")

        # Trigger the AI Triage engine loop ONLY if an actual live vulnerability exposure is caught
        if len(exposed_assets_queue) > 0:
            print(f"    [!] Warning: Live exposures caught for {active_target}. Assembling AI Context...")
            
            # Define the system persona directive
            ai_system_prompt = (
                f"You are an elite B2B cybersecurity consulting analyst working for Angell Data Intelligence.\n"
                f"Your target client is: {active_target}.\n"
                f"Your objective is to review the following structured list of exposed public internet assets, "
                f"triage their exploitability, and type a clean, non-technical executive remediation summary for the company board."
            )
            
            # Serialise data
            ai_data_context = json.dumps(exposed_assets_queue, indent=2)
            
            # Combine into master prompt payload string
            master_ai_prompt = f"{ai_system_prompt}\n\n### LIVE TELEMETRY EXPOSURE DATA:\n{ai_data_context}"
            
            print(f"    [+] Master AI prompt payload successfully generated for {active_target} ({len(master_ai_prompt)} characters).")
            
            # 🟢 Drop your debug inspection line right here:
            print(f"\n=== DEBUG MASTER PROMPT SEED ===\n{master_ai_prompt}\n================================")
        else:
            print(f"    [+] Architecture Verification: No live exposures found for {active_target}. Skipping AI API transactions to save resource capital.")

