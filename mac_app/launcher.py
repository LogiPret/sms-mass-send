#!/usr/bin/env python3
"""
SMS Campaign Launcher - Bootstrap/Updater
This small launcher checks for updates and launches the main app.
The launcher itself rarely needs updating.
Authorization is stored in Keychain (persists across updates).
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
from datetime import datetime
from urllib.request import urlopen, Request

# Create SSL context that doesn't verify certificates (needed for PyInstaller bundled apps)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ============================================================================
# LOGGING
# ============================================================================

def get_log_path():
    """Get the path to the log file."""
    log_dir = os.path.expanduser("~/Library/Logs/SMSCampaign")
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, "launcher.log")

def log(message):
    """Log a message to file and print."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    try:
        with open(get_log_path(), "a") as f:
            f.write(log_message + "\n")
    except:
        pass

def log_exception(e):
    """Log an exception with full traceback."""
    log(f"EXCEPTION: {type(e).__name__}: {str(e)}")
    log(traceback.format_exc())

# ============================================================================
# CONFIG
# ============================================================================

LAUNCHER_VERSION = "1.1.0"
APP_NAME = "SMS Campaign"
CONFIG = {
    "update_url": "https://gist.githubusercontent.com/hugootth/3e89759cac04be452c935c90b5733eea/raw/version.json",
    "main_app_folder": "SMSCampaignApp",  # Folder inside the launcher bundle to store main app
}

def get_launcher_bundle_path():
    """Get the path to this launcher's .app bundle."""
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        if '.app/Contents/MacOS' in exe_path:
            return exe_path.split('.app/Contents/MacOS')[0] + '.app'
    # For development
    return os.path.dirname(os.path.abspath(__file__))

def get_app_support_path():
    """Get path to Application Support folder for storing the main app.
    This avoids App Translocation issues when running from Downloads."""
    home = os.path.expanduser("~")
    app_support = os.path.join(home, "Library", "Application Support", "SMSCampaign")
    os.makedirs(app_support, exist_ok=True)
    return app_support

def get_resources_path():
    """Get path to store app resources (now in Application Support)."""
    return get_app_support_path()

def get_main_app_path():
    """Get path to the main app stored inside launcher's Resources."""
    resources = get_resources_path()
    return os.path.join(resources, CONFIG["main_app_folder"], "main_app.py")

def get_main_app_dir():
    """Get the directory where main app code is stored."""
    resources = get_resources_path()
    app_dir = os.path.join(resources, CONFIG["main_app_folder"])
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_local_version():
    """Get the version of the installed main app."""
    app_dir = get_main_app_dir()
    version_file = os.path.join(app_dir, "version.json")
    if os.path.exists(version_file):
        try:
            with open(version_file) as f:
                return json.load(f).get("version", "0.0.0")
        except:
            pass
    return "0.0.0"

def save_local_version(version):
    """Save the version of the installed main app."""
    app_dir = get_main_app_dir()
    version_file = os.path.join(app_dir, "version.json")
    with open(version_file, 'w') as f:
        json.dump({"version": version}, f)

def check_for_update():
    """Check if an update is available."""
    try:
        req = Request(CONFIG["update_url"] + "?t=" + str(int(time.time())), 
                     headers={"Cache-Control": "no-cache", "Pragma": "no-cache"})
        with urlopen(req, timeout=10, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode('utf-8'))
            remote_version = data.get("version", "0.0.0")
            download_url = data.get("download_url", "")
            
            def parse_version(v):
                try:
                    return tuple(map(int, v.split('.')))
                except:
                    return (0, 0, 0)
            
            local_version = get_local_version()
            
            if parse_version(remote_version) > parse_version(local_version):
                return {
                    "available": True,
                    "version": remote_version,
                    "local_version": local_version,
                    "download_url": download_url
                }
            return {"available": False, "version": remote_version, "local_version": local_version}
    except Exception as e:
        return {"available": False, "error": str(e)}

def download_update(download_url, progress_callback=None):
    """Download the update ZIP file."""
    try:
        temp_dir = tempfile.mkdtemp(prefix="sms_campaign_update_")
        zip_path = os.path.join(temp_dir, "update.zip")
        
        # Download using curl (handles GitHub redirects properly)
        result = subprocess.run(
            ["curl", "-L", "-o", zip_path, "-f", "--max-time", "180", "--progress-bar", download_url],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return None, f"Download failed: {result.stderr}"
        
        return zip_path, None
        
    except Exception as e:
        return None, str(e)

def install_update(zip_path, version):
    """Extract and install the update."""
    try:
        app_dir = get_main_app_dir()
        
        # Extract to temp location first
        temp_extract = tempfile.mkdtemp(prefix="sms_extract_")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract)
        
        # Find the .app bundle in extracted content
        app_bundle = None
        for item in os.listdir(temp_extract):
            if item.endswith('.app'):
                app_bundle = os.path.join(temp_extract, item)
                break
        
        if not app_bundle:
            for root, dirs, _ in os.walk(temp_extract):
                for d in dirs:
                    if d.endswith('.app'):
                        app_bundle = os.path.join(root, d)
                        break
                if app_bundle:
                    break
        
        if not app_bundle:
            return False, "No .app found in update"
        
        log(f"Found app bundle: {app_bundle}")
        
        # Clear old app directory
        if os.path.exists(app_dir):
            subprocess.run(["rm", "-rf", app_dir])
        os.makedirs(app_dir, exist_ok=True)
        
        dest_app = os.path.join(app_dir, "SMSCampaign.app")
        
        # Use ditto to copy (preserves permissions and attributes)
        result = subprocess.run(["ditto", app_bundle, dest_app], capture_output=True, text=True)
        log(f"Ditto result: {result.returncode}, stderr: {result.stderr}")
        
        # Also manually ensure executable permissions
        macos_dir = os.path.join(dest_app, "Contents", "MacOS")
        if os.path.exists(macos_dir):
            for item in os.listdir(macos_dir):
                exe_path = os.path.join(macos_dir, item)
                log(f"Setting executable permission on: {exe_path}")
                subprocess.run(["chmod", "+x", exe_path])
        
        # Remove quarantine attribute
        subprocess.run(["xattr", "-cr", app_dir], capture_output=True)
        
        # Save version
        save_local_version(version)
        
        # Cleanup
        subprocess.run(["rm", "-rf", temp_extract])
        subprocess.run(["rm", "-rf", os.path.dirname(zip_path)])
        
        log(f"Installation complete. App at: {dest_app}")
        
        return True, None
        
    except Exception as e:
        log_exception(e)
        return False, str(e)

def launch_main_app():
    """Launch the main SMS Campaign app."""
    app_dir = get_main_app_dir()
    main_app = os.path.join(app_dir, "SMSCampaign.app")
    
    log(f"launch_main_app called")
    log(f"main_app path: {main_app}")
    log(f"main_app exists: {os.path.exists(main_app)}")
    
    if os.path.exists(main_app):
        try:
            # Use open command with full path
            log(f"Running: open '{main_app}'")
            result = subprocess.run(["open", main_app], capture_output=True, text=True, timeout=10)
            log(f"open result: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
            
            if result.returncode != 0:
                # Try running directly
                log("open failed, trying direct execution...")
                exe_path = os.path.join(main_app, "Contents", "MacOS", "SMS Campaign")
                log(f"exe_path: {exe_path}")
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path])
                    log("Direct execution started")
            
            return True
        except Exception as e:
            log_exception(e)
            return False
    return False

def show_notification(title, message):
    """Show a macOS notification."""
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script], capture_output=True)

def show_dialog(title, message, buttons=["OK"], default=1):
    """Show a macOS dialog and return the clicked button."""
    button_list = ", ".join([f'"{b}"' for b in buttons])
    script = f'''
    tell application "System Events"
        display dialog "{message}" with title "{title}" buttons {{{button_list}}} default button {default}
    end tell
    '''
    try:
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=60)
        output = result.stdout.strip()
        for b in buttons:
            if b in output:
                return b
        return buttons[0]
    except:
        return buttons[-1]  # Return last button (usually cancel) on error

def show_progress_dialog(message):
    """Show a progress dialog (non-blocking)."""
    script = f'''
    tell application "System Events"
        display dialog "{message}" with title "SMS Campaign" buttons {{"Annuler"}} giving up after 300
    end tell
    '''
    # Run in background
    return subprocess.Popen(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    """Main launcher logic."""
    log("=" * 60)
    log(f"SMS Campaign Launcher v{LAUNCHER_VERSION} started")
    log(f"Python: {sys.version}")
    log(f"Executable: {sys.executable}")
    log(f"Frozen: {getattr(sys, 'frozen', False)}")
    log(f"Bundle path: {get_launcher_bundle_path()}")
    log(f"Resources path: {get_resources_path()}")
    log(f"Main app dir: {get_main_app_dir()}")
    
    # Check for updates
    log("Checking for updates...")
    update_info = check_for_update()
    log(f"Update info: {update_info}")
    
    local_version = get_local_version()
    log(f"Local version: {local_version}")
    main_app_exists = local_version != "0.0.0"
    log(f"Main app exists: {main_app_exists}")
    
    if update_info.get("available"):
        version = update_info.get("version", "")
        download_url = update_info.get("download_url", "")
        
        log(f"Update available: {local_version} -> {version}")
        log(f"Download URL: {download_url}")
        
        if main_app_exists:
            # Ask user if they want to update
            log("Showing update dialog...")
            choice = show_dialog(
                "Mise à jour disponible",
                f"Une nouvelle version de SMS Campaign est disponible.\\n\\nVersion actuelle: {local_version}\\nNouvelle version: {version}\\n\\nVoulez-vous mettre à jour maintenant?",
                ["Mettre à jour", "Plus tard"],
                default=1
            )
            log(f"User choice: {choice}")
            
            if choice != "Mettre à jour":
                log("User skipped update")
                launch_main_app()
                return
        else:
            # First install - mandatory
            log("First install - showing installation dialog...")
            show_dialog(
                "Installation",
                f"SMS Campaign v{version} va être téléchargé et installé.\\n\\nCela peut prendre quelques instants.",
                ["OK"]
            )
        
        # Download and install
        log(f"Downloading update from {download_url}...")
        show_notification("SMS Campaign", "Téléchargement de la mise à jour...")
        
        zip_path, error = download_update(download_url)
        log(f"Download result: zip_path={zip_path}, error={error}")
        
        if error:
            log(f"Download failed: {error}")
            show_dialog("Erreur", f"Échec du téléchargement:\\n{error}", ["OK"])
            if main_app_exists:
                launch_main_app()
            return
        
        log("Installing update...")
        success, error = install_update(zip_path, version)
        log(f"Install result: success={success}, error={error}")
        
        if not success:
            log(f"Install failed: {error}")
            show_dialog("Erreur", f"Échec de l'installation:\\n{error}", ["OK"])
            if main_app_exists:
                launch_main_app()
            return
        
        log("Update installed successfully!")
        show_notification("SMS Campaign", f"Mise à jour vers v{version} terminée!")
    
    elif update_info.get("error"):
        log(f"Update check failed: {update_info.get('error')}")
        # Continue anyway if we have a local version
    
    else:
        log(f"No update available. Current version: {local_version}")
    
    # Launch the main app
    log("Launching main app...")
    main_app_path = os.path.join(get_main_app_dir(), "SMSCampaign.app")
    log(f"Main app path: {main_app_path}")
    log(f"Main app exists at path: {os.path.exists(main_app_path)}")
    
    if os.path.exists(main_app_path):
        log(f"Contents of main app dir: {os.listdir(get_main_app_dir())}")
    
    if not launch_main_app():
        log("Failed to launch main app")
        if local_version == "0.0.0":
            show_dialog("Erreur", "Impossible de lancer SMS Campaign.\\nVeuillez vérifier votre connexion internet et réessayer.", ["OK"])
        else:
            show_dialog("Erreur", "Impossible de lancer SMS Campaign.", ["OK"])
        sys.exit(1)
    else:
        log("Main app launched successfully")
    
    log("Launcher finished")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_exception(e)
        show_dialog("Erreur", f"Une erreur s'est produite:\\n{str(e)}", ["OK"])
        sys.exit(1)

