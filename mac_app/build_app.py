#!/usr/bin/env python3
"""
Build script for SMS Campaign Mac App
Creates a standalone .app bundle using PyInstaller

Usage: python3 build_app.py
"""

import subprocess
import os
import shutil

# Configuration
APP_NAME = "SMS Campaign"
MAIN_SCRIPT = "sms_campaign.py"
ICON_FILE = None  # Set to "icon.icns" if you have an icon
PYINSTALLER = os.path.expanduser("~/.local/bin/pyinstaller")

def build():
    print("Building SMS Campaign.app...")
    
    # Clean previous builds
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Cleaned {folder}/")
    
    # PyInstaller command
    cmd = [
        PYINSTALLER,
        '--name', APP_NAME,
        '--windowed',           # No terminal window
        '--onedir',             # Create app bundle
        '--noconfirm',          # Overwrite without asking
        '--clean',              # Clean cache
    ]
    
    # Add icon if exists
    if ICON_FILE and os.path.exists(ICON_FILE):
        cmd.extend(['--icon', ICON_FILE])
    
    cmd.append(MAIN_SCRIPT)
    
    print(f"   Running PyInstaller...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        app_path = f"dist/{APP_NAME}.app"
        print(f"\n Build successful!")
        print(f"   App location: {os.path.abspath(app_path)}")
        print(f"\n To run:")
        print(f"   open '{app_path}'")
        print(f"\n To distribute:")
        print(f"   1. Right-click the .app -> Compress")
        print(f"   2. Share the .zip file")
        print(f"\n Note: First launch requires right-click -> Open -> Open Anyway")
    else:
        print(f"\n Build failed with code {result.returncode}")

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build()
