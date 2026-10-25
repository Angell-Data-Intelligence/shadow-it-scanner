from flask import Flask, request, jsonify, send_file
import subprocess
import os
import html

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
   
    # Clear old artifacts if they exist
    old_json = os.path.join(base_dir, "core_engine", "data_outputs", f"{domain}_recon_report.json")
    old_pdf = os.path.join(base_dir, "core_engine", "data_outputs", "production_scan.pdf")
   
    if os.path.exists(old_json):
        os.remove(old_json)
    if os.path.exists(old_pdf):
        os.remove(old_pdf)
   
    cmd = [
        "python3",
        "core_engine/recon_pipeline.py",
        "--target", str(domain),
        "--limit", str(limit),
        "--tier", str(tier)
    ]
   
    result = subprocess.run(cmd, capture_output=True, text=True)
   
    # Target the exact filename your pipeline produces
    pdf_path = os.path.join(base_dir, "core_engine", "data_outputs", "production_scan.pdf")
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        print(f"SUBPROCESS FAILED:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        return jsonify({
            'error': 'Scan failed',
            'stdout': result.stdout,
            'debug': result.stderr
        }), 500

@app.route('/report', methods=['POST'])
def report():
    data = request.json or {}
    domain = data.get('domain')

    if not domain:
        return jsonify({'error': 'Missing required parameter: domain'}), 400

    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "core_engine", "data_outputs", "production_scan.pdf")

    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf')
    else:
        return jsonify({'error': f'Report PDF not found. Please run a scan first.'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=int(os.environ.get('PORT', 5000)))