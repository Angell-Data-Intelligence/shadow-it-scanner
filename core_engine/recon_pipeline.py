import os
import subprocess
import json
import argparse
from datetime import datetime

# Initialize the command-line argument parser for automated enterprise execution
parser = argparse.ArgumentParser(description='Angell Data Intelligence - Shadow IT Asset Discovery and Reconnaissance Pipeline')
parser.add_argument('--target', type=str, required=True, help='Target company domain for subdomain discovery')
args = parser.parse_args()
target_domain = args.target

# Ensure the data storage directory exists safely before execution
os.makedirs('shadow-it-scanner/data_outputs', exist_ok=True)

# Calculate the target file path before deciding on the scanning strategy
output_filepath = f"shadow-it-scanner/data_outputs/{target_domain}_subdomains.json"

# Check if a cache file for this target already exists on the disk
if os.path.exists(output_filepath):
    print(f"Cache Hit: Loading existing subdomains for {target_domain} from local storage...")
    
    # Open the existing file and read it back into memory
    with open(output_filepath, 'r') as json_file:
        cached_data = json.load(json_file)
        
    # Extract the unique subdomains straight from the JSON file array
    unique_subdomains = cached_data["unique_subdomains"]
    current_time = cached_data["scan_time"]

else:
    print(f"Cache Miss: Initiating live network scan for {target_domain}...")
    
    # In-memory execution and telemetry capture for subdomain discovery using Subfinder tool
    commands_args = ['subfinder', '-d', target_domain, '-silent']
    scan_result = subprocess.run(commands_args, capture_output=True, text=True)
    subdomains = scan_result.stdout.splitlines()
    cleaned_subdomains = [subdomain.strip() for subdomain in subdomains if subdomain.strip()]
    unique_subdomains = list(set(cleaned_subdomains))

    # Capture operational execution timestamp and prepare telemetry payload for enterprise reporting
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
# PHASE 2: DETAILED INFRASTRUCTURE RECONNAISSANCE (PORT TELEMETRY)
test_targets = unique_subdomains[:5]  # Sample of first 5 unique subdomains for quick verification
print(f"Test targets for {target_domain}: {test_targets}")
print(f"\nInitializing network telemetry probe for the top {len(test_targets)} assets...")

for loop in test_targets:
    print(f"Probing {loop} for network reachability and service enumeration...")
    probe_result = subprocess.run(['ping', '-c', '1', loop], capture_output=True, text=True)
    if probe_result.returncode == 0:
        print(f"    [+] Success: {loop} is reachable.")
    else:
        print(f"    [-] Warning: {loop} is not reachable or blocked by firewall.")

# Print diagnostic metrics to the terminal (Runs regardless of Cache Hit or Miss)
print(f"\nVerified unique subdomains found for {target_domain}: {len(unique_subdomains)}")
print(f"Scan completed at: {current_time}")