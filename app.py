from flask import Flask, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json
    domain = data.get('domain')
    tier = data.get('tier', 'scout')
   
    limits = {'scout': 20, 'radar': 100, 'sentinel': 500}
    limit = limits.get(tier, 20)
   
    cmd = f"python3 /app/recon_pipeline.py --target {domain} --limit {limit} --tier {tier}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
   
    pdf_path = f"/app/data_outputs/{domain}_executive_risk_report.pdf"
   
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        return jsonify({'error': 'Scan failed', 'debug': result.stderr.decode()}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False, port=int(os.environ.get('PORT', 5000)))
