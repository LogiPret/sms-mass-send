#!/usr/bin/env python3
"""
Version Manager for SMS Campaign
Handles automatic version bumping and release creation.
"""

import json
import os
import sys
import subprocess
import re
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
MAC_APP_DIR = REPO_ROOT / "mac_app"
VERSION_JSON = MAC_APP_DIR / "version.json"
SMS_CAMPAIGN_PY = MAC_APP_DIR / "sms_campaign.py"
PHONE_APP_DIR = REPO_ROOT / "app"
PHONE_VERSION_JSON = PHONE_APP_DIR / "version.json" if (REPO_ROOT / "app" / "version.json").exists() else None

def get_local_version():
    """Get the current local version from version.json."""
    try:
        with open(VERSION_JSON) as f:
            data = json.load(f)
            return data.get("version", "0.0.0")
    except:
        return "0.0.0"

def get_remote_version():
    """Get the version from the remote Gist."""
    try:
        import urllib.request
        url = "https://gist.githubusercontent.com/hugootth/3e89759cac04be452c935c90b5733eea/raw/version.json"
        with urllib.request.urlopen(url + "?t=" + str(int(__import__('time').time())), timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get("version", "0.0.0")
    except Exception as e:
        print(f"Could not fetch remote version: {e}")
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
    """Update version.json with new version."""
    try:
        with open(VERSION_JSON) as f:
            data = json.load(f)
        
        data["version"] = new_version
        data["changelog"] = f"Version {new_version}"
        
        with open(VERSION_JSON, 'w') as f:
            json.dump(data, f, indent=4)
        
        return True
    except Exception as e:
        print(f"Error updating version.json: {e}")
        return False

def update_python_version(new_version):
    """Update VERSION in sms_campaign.py."""
    try:
        with open(SMS_CAMPAIGN_PY) as f:
            content = f.read()
        
        # Replace VERSION = "x.x.x"
        content = re.sub(
            r'VERSION = "[^"]*"',
            f'VERSION = "{new_version}"',
            content
        )
        
        with open(SMS_CAMPAIGN_PY, 'w') as f:
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

def create_github_release(version):
    """Create a GitHub release with the built app."""
    print(f"Creating GitHub release v{version}...")
    
    # Check if gh CLI is available
    result = subprocess.run(["which", "gh"], capture_output=True)
    if result.returncode != 0:
        print("GitHub CLI (gh) not found. Install with: brew install gh")
        return False
    
    # Build the app first
    print("Building SMS Campaign.app...")
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
    
    # Create ZIP
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
    
    # Create GitHub release
    print(f"Creating GitHub release v{version}...")
    release_result = subprocess.run(
        ["gh", "release", "create", f"v{version}",
         str(zip_path),
         "--title", f"SMS Campaign v{version}",
         "--notes", f"SMS Campaign version {version}\n\nDownload SMS.Campaign.zip and extract to use."],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    
    if release_result.returncode != 0:
        # Check if release already exists
        if "already exists" in release_result.stderr:
            print(f"Release v{version} already exists, uploading asset...")
            # Delete existing asset and upload new one
            subprocess.run(
                ["gh", "release", "delete-asset", f"v{version}", "SMS.Campaign.zip", "-y"],
                cwd=REPO_ROOT, capture_output=True
            )
            upload_result = subprocess.run(
                ["gh", "release", "upload", f"v{version}", str(zip_path), "--clobber"],
                cwd=REPO_ROOT, capture_output=True, text=True
            )
            if upload_result.returncode != 0:
                print(f"Upload failed: {upload_result.stderr}")
                return False
        else:
            print(f"Release creation failed: {release_result.stderr}")
            return False
    
    print(f"✅ GitHub release v{version} created successfully!")
    return True

def update_gist_version(version):
    """Update the Gist with new version."""
    print(f"Updating Gist version to {version}...")
    
    # Read current version.json
    with open(VERSION_JSON) as f:
        data = json.load(f)
    
    # Update Gist using gh CLI
    gist_id = "3e89759cac04be452c935c90b5733eea"
    
    result = subprocess.run(
        ["gh", "gist", "edit", gist_id, "-f", f"version.json", str(VERSION_JSON)],
        cwd=REPO_ROOT,
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Failed to update Gist: {result.stderr}")
        return False
    
    print(f"✅ Gist updated to v{version}")
    return True

# ============================================================================
# COMMANDS
# ============================================================================

def cmd_check():
    """Check if version needs bumping."""
    if mac_app_files_changed():
        print("mac_app files changed - version bump needed")
        return 0
    else:
        print("No mac_app files changed")
        return 1

def cmd_bump(bump_type="patch"):
    """Bump version and update files."""
    current = get_local_version()
    new_version = bump_version(current, bump_type)
    
    print(f"Bumping version: {current} -> {new_version}")
    
    if update_version_json(new_version):
        print(f"✅ Updated version.json")
    
    if update_python_version(new_version):
        print(f"✅ Updated sms_campaign.py")
    
    # Stage the updated files
    subprocess.run(["git", "add", str(VERSION_JSON), str(SMS_CAMPAIGN_PY)], cwd=REPO_ROOT)
    
    print(f"✅ Version bumped to {new_version}")
    return 0

def cmd_release():
    """Create GitHub release if version is higher than remote."""
    local_version = get_local_version()
    remote_version = get_remote_version()
    
    print(f"Local version: {local_version}")
    print(f"Remote version: {remote_version}")
    
    if remote_version is None:
        print("Could not fetch remote version, skipping release")
        return 1
    
    if parse_version(local_version) > parse_version(remote_version):
        print(f"Local version {local_version} > remote {remote_version}")
        
        if create_github_release(local_version):
            update_gist_version(local_version)
            return 0
        else:
            return 1
    else:
        print("No new version to release")
        return 0

def cmd_auto_commit():
    """Auto-bump version on commit if mac_app changed."""
    if mac_app_files_changed():
        return cmd_bump("patch")
    return 0

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
