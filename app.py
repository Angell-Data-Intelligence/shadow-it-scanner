from flask import Flask, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json or {}
    domain = data.get('domain')
    tier = data.get('tier', 'scout')
   
    if not domain:
        return jsonify({'error': 'Missing required parameter: domain'}), 400
   
    limits = {'scout': 20, 'radar': 100, 'sentinel': 500}
    limit = limits.get(tier, 20)
   
    # ✅ FIX 1: Use relative pathing to target core_engine folder
    # ✅ FIX 2: Switched shell=True string to a secure, injection-proof list array
    cmd = [
        "python3",
        "core_engine/recon_pipeline.py",
        "--target", str(domain),
        "--limit", str(limit),
        "--tier", str(tier)
    ]
   
    # Run the pipeline relative to the project root directory
    result = subprocess.run(cmd, capture_output=True, text=True)
   
    # ✅ FIX 3: Dynamic path calculation for data_outputs folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "data_outputs", f"{domain}_executive_risk_report.pdf")
   
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        return jsonify({
            'error': 'Scan failed',
            'stdout': result.stdout,
            'debug': result.stderr
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Bind to 0.0.0.0 so Heroku can expose the port externally
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', 5000)))