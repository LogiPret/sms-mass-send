#!/usr/bin/env python3
"""
SMS Campaign Launcher v2.1.0
- Shows loading window IMMEDIATELY on launch
- All operations happen in background after window appears
"""

import subprocess
import json
import os
import sys
import tempfile
import zipfile
import time
import traceback
import ssl
import threading
from datetime import datetime
from urllib.request import urlopen, Request
import webview  # Import at top level for PyInstaller

# SSL context for PyInstaller
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ============================================================================
# CONFIG
# ============================================================================

LAUNCHER_VERSION = "2.1.0"
CONFIG = {
    "update_url": "https://gist.githubusercontent.com/hugootth/3e89759cac04be452c935c90b5733eea/raw/version.json",
    "main_app_folder": "SMSCampaignApp",
}

# ============================================================================
# LOGGING (minimal to avoid startup delay)
# ============================================================================

LOG_PATH = None

def get_log_path():
    global LOG_PATH
    if not LOG_PATH:
        log_dir = os.path.expanduser("~/Library/Logs/SMSCampaign")
        os.makedirs(log_dir, exist_ok=True)
        LOG_PATH = os.path.join(log_dir, "launcher.log")
    return LOG_PATH

def log(message):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(get_log_path(), "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except:
        pass

# ============================================================================
# PATH HELPERS
# ============================================================================

def get_app_support_path():
    home = os.path.expanduser("~")
    app_support = os.path.join(home, "Library", "Application Support", "SMSCampaign")
    os.makedirs(app_support, exist_ok=True)
    return app_support

def get_main_app_dir():
    app_dir = os.path.join(get_app_support_path(), CONFIG["main_app_folder"])
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

# ============================================================================
# LOADING WINDOW HTML
# ============================================================================

LOADING_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);color:#fff;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden}
.logo{font-size:64px;margin-bottom:20px;animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.1);opacity:.8}}
.title{font-size:28px;font-weight:600;margin-bottom:8px}
.subtitle{font-size:14px;color:#888;margin-bottom:30px}
.spinner{width:40px;height:40px;border:3px solid rgba(255,255,255,.1);border-top-color:#667eea;border-radius:50%;animation:spin 1s linear infinite;margin-bottom:20px}
@keyframes spin{to{transform:rotate(360deg)}}
.status{font-size:15px;color:#aaa;min-height:24px;text-align:center;padding:0 20px}
</style>
</head>
<body>
<div class="title">Campagne SMS</div>
<div class="subtitle">Chargement...</div>
<div class="spinner"></div>
<div class="status" id="status"></div>
<script>
function setStatus(t){document.getElementById('status').textContent=t}
</script>
</body>
</html>"""

# ============================================================================
# UPDATE LOGIC
# ============================================================================

def get_local_version():
    version_file = os.path.join(get_main_app_dir(), "version.json")
    if os.path.exists(version_file):
        try:
            with open(version_file) as f:
                return json.load(f).get("version", "0.0.0")
        except:
            pass
    return "0.0.0"

def check_for_update():
    try:
        url = CONFIG["update_url"] + "?t=" + str(int(time.time()))
        req = Request(url, headers={"Cache-Control": "no-cache"})
        with urlopen(req, timeout=10, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode('utf-8'))
            remote = data.get("version", "0.0.0")
            download_url = data.get("download_url", "")
            
            local = get_local_version()
            local_parts = tuple(map(int, local.split('.')))
            remote_parts = tuple(map(int, remote.split('.')))
            
            if remote_parts > local_parts:
                return {"available": True, "version": remote, "url": download_url, "local": local}
            return {"available": False, "local": local}
    except Exception as e:
        log(f"Update check error: {e}")
        return {"available": False, "error": str(e), "local": get_local_version()}

def download_update(url):
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "update.zip")
        
        result = subprocess.run(["curl", "-L", "-s", "-o", zip_path, url], capture_output=True)
        
        if result.returncode != 0 or not os.path.exists(zip_path):
            return None, "Download failed"
        
        if os.path.getsize(zip_path) < 1000:
            return None, "File too small"
        
        return zip_path, None
    except Exception as e:
        return None, str(e)

def install_update(zip_path, version):
    try:
        app_dir = get_main_app_dir()
        temp_extract = tempfile.mkdtemp()
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(temp_extract)
        
        # Find .app
        app_name = None
        for item in os.listdir(temp_extract):
            if item.endswith('.app'):
                app_name = item
                break
        
        if not app_name:
            return False, "No .app found"
        
        src = os.path.join(temp_extract, app_name)
        dst = os.path.join(app_dir, "SMSCampaign.app")
        
        subprocess.run(["rm", "-rf", dst], capture_output=True)
        subprocess.run(["ditto", src, dst], capture_output=True)
        subprocess.run(["chmod", "-R", "+x", dst], capture_output=True)
        
        with open(os.path.join(app_dir, "version.json"), 'w') as f:
            json.dump({"version": version}, f)
        
        subprocess.run(["rm", "-rf", temp_extract], capture_output=True)
        subprocess.run(["rm", "-rf", os.path.dirname(zip_path)], capture_output=True)
        
        return True, None
    except Exception as e:
        return False, str(e)

def launch_main_app():
    app_path = os.path.join(get_main_app_dir(), "SMSCampaign.app")
    if os.path.exists(app_path):
        subprocess.Popen(["open", app_path])
        return True
    return False

def main_app_exists():
    return os.path.exists(os.path.join(get_main_app_dir(), "SMSCampaign.app"))

# ============================================================================
# MAIN - SHOW WINDOW IMMEDIATELY
# ============================================================================

# Signal file for main app to tell launcher it's ready
SIGNAL_FILE = os.path.join(tempfile.gettempdir(), "sms_campaign_ready.signal")

def cleanup_signal():
    """Remove signal file on startup"""
    try:
        if os.path.exists(SIGNAL_FILE):
            os.remove(SIGNAL_FILE)
    except:
        pass

def wait_for_main_app(timeout=30):
    """Wait for main app to signal it's ready"""
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(SIGNAL_FILE):
            log("Main app signaled ready")
            try:
                os.remove(SIGNAL_FILE)
            except:
                pass
            return True
        time.sleep(0.1)
    log("Timeout waiting for main app")
    return False

def main():
    log(f"Launcher v{LAUNCHER_VERSION} started")
    cleanup_signal()
    
    # ALWAYS create window IMMEDIATELY - no checks before this
    window = webview.create_window(
        "Campagne SMS",
        html=LOADING_HTML,
        width=400,
        height=350,
        resizable=False,
        frameless=False,
        easy_drag=True
    )
    
    def set_status(text):
        try:
            safe_text = text.replace("'", "\\'")
            window.evaluate_js(f"setStatus('{safe_text}')")
        except:
            pass
    
    def background_task():
        update = check_for_update()
        local = update.get("local", "0.0.0")
        
        if update.get("available"):
            version = update["version"]
            url = update["url"]
            
            set_status(f"Mise à jour v{version}...")
            zip_path, err = download_update(url)
            if zip_path:
                set_status("Installation...")
                ok, err = install_update(zip_path, version)
                if not ok:
                    set_status(f"Erreur: {err}")
                    time.sleep(1.5)
        
        elif local == "0.0.0":
            set_status("Installation...")
            try:
                url = CONFIG["update_url"] + "?t=" + str(int(time.time()))
                req = Request(url)
                with urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
                    data = json.loads(resp.read().decode())
                    dl_url = data.get("download_url", "")
                    ver = data.get("version", "1.0.0")
                    if dl_url:
                        zip_path, err = download_update(dl_url)
                        if zip_path:
                            install_update(zip_path, ver)
            except Exception as e:
                log(f"First install error: {e}")
                set_status("Erreur de connexion")
                time.sleep(1.5)
        
        # Launch and wait for main app to signal ready
        if main_app_exists():
            launch_main_app()
            wait_for_main_app(timeout=30)
            try:
                window.destroy()
            except:
                pass
        else:
            set_status("Application introuvable")
            time.sleep(2)
            try:
                window.destroy()
            except:
                pass
    
    def on_loaded():
        t = threading.Thread(target=background_task, daemon=True)
        t.start()
    
    window.events.loaded += on_loaded
    
    # START WINDOW - this blocks until window closes
    webview.start()
    log("Launcher finished")

def run_headless():
    """Run without GUI"""
    update = check_for_update()
    
    if update.get("available"):
        zip_path, _ = download_update(update["url"])
        if zip_path:
            install_update(zip_path, update["version"])
    elif get_local_version() == "0.0.0":
        try:
            req = Request(CONFIG["update_url"])
            with urlopen(req, timeout=10, context=SSL_CONTEXT) as resp:
                data = json.loads(resp.read().decode())
                url = data.get("download_url", "")
                ver = data.get("version", "1.0.0")
                if url:
                    zip_path, _ = download_update(url)
                    if zip_path:
                        install_update(zip_path, ver)
        except:
            pass
    
    launch_main_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Fatal error: {e}")
        log(traceback.format_exc())
        # Try to launch app anyway
        launch_main_app()
