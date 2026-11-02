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
   
    # Set up headless execution environment
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
   
    cmd = [
        "python3",
        "core_engine/recon_pipeline.py",
        "--target", str(domain),
        "--limit", str(limit),
        "--tier", str(tier)
    ]
   
    # Pass env to subprocess
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
   
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