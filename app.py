import os
import subprocess
from flask import Flask, request, jsonify, send_file

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
   
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure headless terminal environment is present
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
   
    cmd = [
        "python3",
        "core_engine/recon_pipeline.py",
        "--target", str(domain),
        "--limit", str(limit),
        "--tier", str(tier)
    ]
   
    try:
        # Run synchronously with a 25s safeguard to stay under Heroku's 30s limit
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=25)
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Scan execution timed out on the server.'}), 504
   
    pdf_path = os.path.join(base_dir, "core_engine", "data_outputs", "production_scan.pdf")
    
    if os.path.exists(pdf_path):
        # Stream the PDF binary directly back to Make.com and Retool
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        print(f"SUBPROCESS FAILED:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        return jsonify({
            'error': 'Scan failed to generate PDF',
            'stdout': result.stdout,
            'debug': result.stderr
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))