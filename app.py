import os
import redis
from rq import Queue
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Connect to Heroku Redis using the automatically injected environment variable
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue(connection=conn)

def run_recon_task(domain, limit, tier):
    """Heavy task executed in background worker"""
    import subprocess
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    env["TERM"] = "xterm-256color"
   
    cmd = [
        "python3",
        "core_engine/recon_pipeline.py",
        "--target", str(domain),
        "--limit", str(limit),
        "--tier", str(tier)
    ]
    subprocess.run(cmd, capture_output=True, text=True, env=env)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json or {}
    domain = data.get('domain')
    tier = data.get('tier', 'scout')
   
    if not domain:
        return jsonify({'error': 'Missing required parameter: domain'}), 400
   
    limits = {'scout': 20, 'radar': 100, 'sentinel': 500}
    limit = limits.get(tier, 20)
   
    # Enqueue the task; returns immediately to prevent Heroku 30s timeouts
    job = q.enqueue(run_recon_task, domain, limit, tier, job_timeout=600)
   
    return jsonify({
        'status': 'queued',
        'job_id': job.get_id(),
        'message': f'Scan initiated for {domain} under tier {tier}.'
    }), 202

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
        return jsonify({'error': 'Report PDF not ready yet.'}), 404