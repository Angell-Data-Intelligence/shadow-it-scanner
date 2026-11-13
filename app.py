import os
import subprocess
from flask import Flask, request, jsonify, send_file
import stripe
import base64

app = Flask(__name__)

# =====================================================================
# HEALTH CHECK ROUTE
# =====================================================================

@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Angell Data Intelligence API"}), 200


# =====================================================================
# SCAN ROUTE
# =====================================================================

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
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=25)
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Scan execution timed out on the server.'}), 504
   
    pdf_filename = f"{domain}_executive_risk_report.pdf"
    pdf_path = os.path.join(base_dir, "core_engine", "data_outputs", pdf_filename)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, mimetype='application/pdf', as_attachment=True, download_name=pdf_filename)
    else:
        print(f"SUBPROCESS FAILED:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        return jsonify({
            'error': 'Scan failed to generate PDF',
            'stdout': result.stdout,
            'debug': result.stderr
        }), 500


# =====================================================================
# DOWNLOAD ROUTE
# =====================================================================

@app.route('/download', methods=['GET', 'POST'])
def download():
    domain = request.args.get('domain') or (request.json or {}).get('domain')
    
    if not domain:
        return jsonify({'error': 'Missing required parameter: domain'}), 400
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(base_dir, "core_engine", "data_outputs")
    
    if not os.path.exists(outputs_dir):
        return jsonify({'error': 'Data outputs directory not found'}), 504
    
    matched_filename = f"{domain}_executive_risk_report.pdf"
    pdf_path = os.path.join(outputs_dir, matched_filename)
    
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            encoded_pdf = base64.b64encode(f.read()).decode('utf-8')
            
        return jsonify({
            'data': encoded_pdf,
            'contentType': 'application/pdf',
            'filename': matched_filename
        }), 200
    else:
        return jsonify({'error': f'Report PDF for {domain} not found. Please run a scan first.'}), 404


# =====================================================================
# STRIPE CONFIGURATION & CHECKOUT SESSION ROUTE
# =====================================================================

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
live_webhook_secret = os.getenv("LIVE_STRIPE_WEBHOOK_SECRET")
test_webhook_secret = os.getenv("TEST_STRIPE_WEBHOOK_SECRET")

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.json or {}
    tier = data.get('tier', 'scout')
    customer_email = data.get('email')

    price_mapping = {
        "scout": os.getenv("STRIPE_PRICE_SCOUT"),
        "radar": os.getenv("STRIPE_PRICE_RADAR"),
        "sentinel": os.getenv("STRIPE_PRICE_SENTINEL")
    }

    price_id = price_mapping.get(tier)
    if not price_id:
        return jsonify({'error': f'Stripe Price ID for tier "{tier}" is not configured in Heroku environment variables.'}), 500

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=customer_email if customer_email else None,
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://angelldataintelligence--shadow-scanner.retool.app/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://angelldataintelligence--shadow-scanner.retool.app/pricing',
        )
        return jsonify({'url': checkout_session.url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =====================================================================
# STRIPE WEBHOOK ROUTE
# =====================================================================

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=False)
    sig_header = request.headers.get('Stripe-Signature')

    event = None
    secrets = [s for s in [live_webhook_secret, test_webhook_secret] if s]
    
    for secret in secrets:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
            break
        except stripe.error.SignatureVerificationError:
            continue
        except ValueError:
            return jsonify({"error": "Invalid payload"}), 400

    if not event:
        return jsonify({"error": "Invalid signature"}), 400

    event_type = event['type']
    data_object = event['data']['object']

    if event_type == 'checkout.session.completed':
        customer_email = data_object.get('customer_email') or data_object.get('customer_details', {}).get('email')
        print(f" [+] Successful checkout for: {customer_email}")
        
    elif event_type == 'customer.subscription.updated':
        print(f" [+] Subscription updated: {data_object.get('id')}")
        
    elif event_type == 'customer.subscription.deleted':
        print(f" [+] Subscription deleted/cancelled: {data_object.get('id')}")

    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))