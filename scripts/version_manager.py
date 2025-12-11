#!/usr/bin/env python3
"""
Version Manager for SMS Campaign
Handles automatic version bumping and release creation for BOTH Mac and Mobile apps.
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent

# Mac App Config
MAC_APP_DIR = REPO_ROOT / "mac_app"
MAC_VERSION_JSON = MAC_APP_DIR / "version.json"
MAC_SMS_CAMPAIGN_PY = MAC_APP_DIR / "sms_campaign.py"
MAC_GIST_ID = "3e89759cac04be452c935c90b5733eea"

# Mobile App Config
MOBILE_APP_DIR = REPO_ROOT / "app"
MOBILE_SCRIPT = MOBILE_APP_DIR / "sms_automatisation.js"
MOBILE_VERSION_JSON = MOBILE_APP_DIR / "version.json"
MOBILE_GIST_ID = "0e0f68902ace0bfe94e0e83a8f89db2e"

def get_local_version(app_type="mac"):
    """Get the current local version."""
    if app_type == "mac":
        try:
            with open(MAC_VERSION_JSON) as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
        except:
            return "0.0.0"
    else:  # mobile
        try:
            with open(MOBILE_SCRIPT) as f:
                content = f.read()
                match = re.search(r'const SCRIPT_VERSION = "([^"]+)"', content)
                if match:
                    return match.group(1)
        except:
            pass
        return "0.0.0"

def get_remote_version(app_type="mac"):
    """Get the version from the remote Gist."""
    try:
        import urllib.request
        import time
        
        if app_type == "mac":
            gist_id = MAC_GIST_ID
        else:
            gist_id = MOBILE_GIST_ID
            
        url = f"https://gist.githubusercontent.com/hugootth/{gist_id}/raw/version.json"
        # For mobile, try HugoOtth (capital O)
        if app_type == "mobile":
            url = f"https://gist.githubusercontent.com/HugoOtth/{gist_id}/raw/version.json"
            
        with urllib.request.urlopen(url + "?t=" + str(int(time.time())), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("version", "0.0.0")
    except Exception as e:
        print(f"Could not fetch remote version for {app_type}: {e}")
        return None

def parse_version(v):
    """Parse version string to tuple."""
    try:
        parts = v.split('.')
        return tuple(int(p) for p in parts)
    except:
        return (0, 0, 0)

def bump_version(version, bump_type="patch"):
    """Bump version number."""
    parts = list(parse_version(version))
    while len(parts) < 3:
        parts.append(0)
    
    if bump_type == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == "minor":
        parts[1] += 1
        parts[2] = 0
    else:  # patch
        parts[2] += 1
    
    return ".".join(str(p) for p in parts)

def update_version_json(new_version):
    """Update Mac version.json with new version."""
    try:
        with open(MAC_VERSION_JSON) as f:
            data = json.load(f)
        
        data["version"] = new_version
        data["changelog"] = f"Version {new_version}"
        
        with open(MAC_VERSION_JSON, 'w') as f:
            json.dump(data, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error updating version.json: {e}")
        return False

def update_python_version(new_version):
    """Update VERSION in sms_campaign.py."""
    try:
        with open(MAC_SMS_CAMPAIGN_PY) as f:
            content = f.read()
        
        # Replace VERSION = "x.x.x"
        content = re.sub(
            r'VERSION = "[^"]*"',
            f'VERSION = "{new_version}"',
            content
        )
        
        with open(MAC_SMS_CAMPAIGN_PY, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error updating sms_campaign.py: {e}")
        return False

def get_changed_files():
    """Get list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def mac_app_files_changed():
    """Check if any mac_app files are staged for commit."""
    changed = get_changed_files()
    return any(f.startswith("mac_app/") for f in changed if f)

def mobile_app_files_changed():
    """Check if any app/ files are staged for commit."""
    changed = get_changed_files()
    return any(f.startswith("app/") for f in changed if f)

def update_mobile_script_version(new_version):
    """Update SCRIPT_VERSION in sms_automatisation.js."""
    try:
        with open(MOBILE_SCRIPT) as f:
            content = f.read()
        
        # Replace SCRIPT_VERSION = "x.x.x"
        content = re.sub(
            r'const SCRIPT_VERSION = "[^"]*"',
            f'const SCRIPT_VERSION = "{new_version}"',
            content
        )
        
        with open(MOBILE_SCRIPT, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error updating sms_automatisation.js: {e}")
        return False

def update_mobile_version_json(new_version):
    """Update mobile version.json with new version."""
    try:
        version_file = MOBILE_VERSION_JSON
        
        # Create or update version.json
        data = {"version": new_version, "changelog": f"Version {new_version}"}
        
        if version_file.exists():
            with open(version_file) as f:
                data = json.load(f)
            data["version"] = new_version
        
        with open(version_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error updating mobile version.json: {e}")
        return False

def update_mobile_gist(version):
    """Update the mobile Gist with new script and version."""
    print(f"Updating mobile Gist to v{version}...")
    
    # Update both sms_automatisation.js and version.json to the Gist
    result1 = subprocess.run(
        ["gh", "gist", "edit", MOBILE_GIST_ID, "-f", "sms_automatisation.js", str(MOBILE_SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    
    if result1.returncode != 0:
        print(f"Failed to update mobile script in Gist: {result1.stderr}")
        return False
    
    result2 = subprocess.run(
        ["gh", "gist", "edit", MOBILE_GIST_ID, "-f", "version.json", str(MOBILE_VERSION_JSON)],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    
    if result2.returncode != 0:
        print(f"Failed to update mobile version.json in Gist: {result2.stderr}")
        return False
    
    print(f"✅ Mobile Gist updated to v{version}")
    return True

def create_github_release(version):
    """Create a GitHub release with the built app."""
    print(f"Creating GitHub release v{version}...")
    
    # Check if gh CLI is available
    result = subprocess.run(["which", "gh"], capture_output=True)
    if result.returncode != 0:
        print("GitHub CLI (gh) not found. Install with: brew install gh")
        return False
    
    # Build the main app first
    print("Building SMS Campaign.app (main app)...")
    build_result = subprocess.run(
        ["pyinstaller", "-y", "--onefile", "--windowed", 
         "--name", "SMS Campaign", 
         "--add-data", "version.json:.",
         "sms_campaign.py"],
        cwd=MAC_APP_DIR,
        capture_output=True, text=True
    )
    
    if build_result.returncode != 0:
        print(f"Build failed: {build_result.stderr}")
        return False
    
    # Create ZIP (for auto-updater)
    print("Creating ZIP archive...")
    zip_path = MAC_APP_DIR / "dist" / "SMS.Campaign.zip"
    app_path = MAC_APP_DIR / "dist" / "SMS Campaign.app"
    
    subprocess.run(["rm", "-f", str(zip_path)], cwd=MAC_APP_DIR / "dist")
    zip_result = subprocess.run(
        ["zip", "-r", "SMS.Campaign.zip", "SMS Campaign.app"],
        cwd=MAC_APP_DIR / "dist",
        capture_output=True, text=True
    )
    
    if not zip_path.exists():
        print("Failed to create ZIP")
        return False
    
    # Build the launcher
    print("Building SMS Campaign Launcher.app...")
    launcher_path = MAC_APP_DIR / "launcher_v2.py"
    if launcher_path.exists():
        launcher_build = subprocess.run(
            ["pyinstaller", "-y", "--onefile", "--windowed", 
             "--name", "SMS Campaign Launcher", 
             "launcher_v2.py"],
            cwd=MAC_APP_DIR,
            capture_output=True, text=True
        )
        
        if launcher_build.returncode != 0:
            print(f"Launcher build failed: {launcher_build.stderr}")
            # Continue anyway, launcher is optional
        else:
            # Create styled DMG installer using create_dmg.py
            print("Creating styled DMG installer...")
            create_dmg_script = MAC_APP_DIR / "create_dmg.py"
            if create_dmg_script.exists():
                dmg_result = subprocess.run(
                    ["python3", str(create_dmg_script)],
                    cwd=MAC_APP_DIR,
                    capture_output=True, text=True
                )
                if dmg_result.returncode != 0:
                    print(f"Styled DMG failed, using basic DMG: {dmg_result.stderr}")
                    # Fallback to basic DMG
                    dmg_path = MAC_APP_DIR / "dist" / "SMS.Campaign.Installer.dmg"
                    dmg_temp = MAC_APP_DIR / "dist" / "dmg_temp"
                    
                    subprocess.run(["rm", "-rf", str(dmg_temp), str(dmg_path)], cwd=MAC_APP_DIR / "dist")
                    subprocess.run(["mkdir", "-p", str(dmg_temp)], cwd=MAC_APP_DIR / "dist")
                    subprocess.run(["cp", "-R", "SMS Campaign Launcher.app", str(dmg_temp / "SMS Campaign.app")], cwd=MAC_APP_DIR / "dist")
                    subprocess.run(["ln", "-s", "/Applications", str(dmg_temp / "Applications")], cwd=MAC_APP_DIR / "dist")
                    
                    subprocess.run(
                        ["hdiutil", "create", "-volname", "SMS Campaign", 
                         "-srcfolder", str(dmg_temp), "-ov", "-format", "UDZO", str(dmg_path)],
                        cwd=MAC_APP_DIR / "dist",
                        capture_output=True, text=True
                    )
                    subprocess.run(["rm", "-rf", str(dmg_temp)], cwd=MAC_APP_DIR / "dist")
                else:
                    print("✅ Styled DMG installer created")
            else:
                # Basic DMG fallback
                print("Creating basic DMG installer...")
                dmg_path = MAC_APP_DIR / "dist" / "SMS.Campaign.Installer.dmg"
                dmg_temp = MAC_APP_DIR / "dist" / "dmg_temp"
                
                subprocess.run(["rm", "-rf", str(dmg_temp), str(dmg_path)], cwd=MAC_APP_DIR / "dist")
                subprocess.run(["mkdir", "-p", str(dmg_temp)], cwd=MAC_APP_DIR / "dist")
                subprocess.run(["cp", "-R", "SMS Campaign Launcher.app", str(dmg_temp / "SMS Campaign.app")], cwd=MAC_APP_DIR / "dist")
                subprocess.run(["ln", "-s", "/Applications", str(dmg_temp / "Applications")], cwd=MAC_APP_DIR / "dist")
                
                subprocess.run(
                    ["hdiutil", "create", "-volname", "SMS Campaign", 
                     "-srcfolder", str(dmg_temp), "-ov", "-format", "UDZO", str(dmg_path)],
                    cwd=MAC_APP_DIR / "dist",
                    capture_output=True, text=True
                )
                subprocess.run(["rm", "-rf", str(dmg_temp)], cwd=MAC_APP_DIR / "dist")
                print("✅ Basic DMG installer created")
    
    # Create GitHub release
    print(f"Creating GitHub release v{version}...")
    
    # Prepare list of files to upload
    release_files = [str(zip_path)]
    dmg_path = MAC_APP_DIR / "dist" / "SMS.Campaign.Installer.dmg"
    if dmg_path.exists():
        release_files.append(str(dmg_path))
    
    release_result = subprocess.run(
        ["gh", "release", "create", f"v{version}"] + release_files + [
         "--title", f"SMS Campaign v{version}",
         "--notes", f"SMS Campaign version {version}\n\n**For new installs:** Download `SMS.Campaign.Installer.dmg` and drag to Applications.\n\n**For auto-updates:** The app updates automatically."],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    
    if release_result.returncode != 0:
        # Check if release already exists
        if "already exists" in release_result.stderr:
            print(f"Release v{version} already exists, uploading assets...")
            # Upload all files with --clobber to overwrite existing
            for file_path in release_files:
                upload_result = subprocess.run(
                    ["gh", "release", "upload", f"v{version}", file_path, "--clobber"],
                    cwd=REPO_ROOT, capture_output=True, text=True
                )
                if upload_result.returncode != 0:
                    print(f"Upload failed for {file_path}: {upload_result.stderr}")
        else:
            print(f"Release creation failed: {release_result.stderr}")
            return False
    
    print(f"✅ GitHub release v{version} created successfully!")
    return True

def update_gist_version(version, app_type="mac"):
    """Update the Gist with new version."""
    if app_type == "mac":
        print(f"Updating Mac Gist version to {version}...")
        
        result = subprocess.run(
            ["gh", "gist", "edit", MAC_GIST_ID, "-f", "version.json", str(MAC_VERSION_JSON)],
            cwd=REPO_ROOT,
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"Failed to update Mac Gist: {result.stderr}")
            return False
        
        print(f"✅ Mac Gist updated to v{version}")
        return True
    else:  # mobile
        return update_mobile_gist(version)

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_check():
    """Check if any app files changed."""
    mac_changed = mac_app_files_changed()
    mobile_changed = mobile_app_files_changed()
    
    if mac_changed:
        print("mac_app files changed - Mac version bump needed")
    if mobile_changed:
        print("app/ files changed - Mobile version bump needed")
    
    if mac_changed or mobile_changed:
        return 0
    else:
        print("No app files changed")
        return 1

def cmd_bump_mac(bump_type="patch"):
    """Bump Mac app version and update files."""
    current = get_local_version("mac")
    new_version = bump_version(current, bump_type)
    
    print(f"Bumping Mac version: {current} -> {new_version}")
    
    if update_version_json(new_version):
        print(f"✅ Updated mac_app/version.json")
    
    if update_python_version(new_version):
        print(f"✅ Updated sms_campaign.py")
    
    # Stage the updated files
    subprocess.run(["git", "add", str(MAC_VERSION_JSON), str(MAC_SMS_CAMPAIGN_PY)], cwd=REPO_ROOT)
    
    print(f"✅ Mac version bumped to {new_version}")
    return 0

def cmd_bump_mobile(bump_type="patch"):
    """Bump Mobile app version and update files."""
    current = get_local_version("mobile")
    new_version = bump_version(current, bump_type)
    
    print(f"Bumping Mobile version: {current} -> {new_version}")
    
    if update_mobile_script_version(new_version):
        print(f"✅ Updated sms_automatisation.js")
    
    if update_mobile_version_json(new_version):
        print(f"✅ Updated app/version.json")
    
    # Stage the updated files
    subprocess.run(["git", "add", str(MOBILE_SCRIPT), str(MOBILE_VERSION_JSON)], cwd=REPO_ROOT)
    
    print(f"✅ Mobile version bumped to {new_version}")
    return 0

def cmd_bump(bump_type="patch"):
    """Bump version and update files (legacy - bumps Mac only)."""
    return cmd_bump_mac(bump_type)

def cmd_release():
    """Create releases for both Mac and Mobile if versions are higher than remote."""
    result = 0
    
    # Check Mac App
    print("\n=== MAC APP ===")
    mac_local = get_local_version("mac")
    mac_remote = get_remote_version("mac")
    
    print(f"Mac Local version: {mac_local}")
    print(f"Mac Remote version: {mac_remote}")
    
    if mac_remote is not None and parse_version(mac_local) > parse_version(mac_remote):
        print(f"Mac version {mac_local} > remote {mac_remote}")
        
        if create_github_release(mac_local):
            update_gist_version(mac_local, "mac")
        else:
            result = 1
    else:
        print("No new Mac version to release")
    
    # Check Mobile App
    print("\n=== MOBILE APP ===")
    mobile_local = get_local_version("mobile")
    mobile_remote = get_remote_version("mobile")
    
    print(f"Mobile Local version: {mobile_local}")
    print(f"Mobile Remote version: {mobile_remote}")
    
    if mobile_remote is not None and parse_version(mobile_local) > parse_version(mobile_remote):
        print(f"Mobile version {mobile_local} > remote {mobile_remote}")
        
        if update_gist_version(mobile_local, "mobile"):
            print(f"✅ Mobile app released to Gist v{mobile_local}")
        else:
            result = 1
    else:
        print("No new Mobile version to release")
    
    return result

def cmd_auto_commit():
    """Auto-bump version on commit if app files changed."""
    result = 0
    
    if mac_app_files_changed():
        print("\n=== Auto-bumping Mac version ===")
        result |= cmd_bump_mac("patch")
    
    if mobile_app_files_changed():
        print("\n=== Auto-bumping Mobile version ===")
        result |= cmd_bump_mobile("patch")
    
    return result

def cmd_auto_push():
    """Auto-release on push if version is higher."""
    return cmd_release()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: version_manager.py <command>")
        print("Commands:")
        print("  check       - Check if mac_app files changed")
        print("  bump        - Bump patch version")
        print("  bump-minor  - Bump minor version")
        print("  bump-major  - Bump major version")
        print("  release     - Create GitHub release")
        print("  auto-commit - Auto-bump on commit (for pre-commit hook)")
        print("  auto-push   - Auto-release on push (for pre-push hook)")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        sys.exit(cmd_check())
    elif cmd == "bump":
        sys.exit(cmd_bump("patch"))
    elif cmd == "bump-minor":
        sys.exit(cmd_bump("minor"))
    elif cmd == "bump-major":
        sys.exit(cmd_bump("major"))
    elif cmd == "release":
        sys.exit(cmd_release())
    elif cmd == "auto-commit":
        sys.exit(cmd_auto_commit())
    elif cmd == "auto-push":
        sys.exit(cmd_auto_push())
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
