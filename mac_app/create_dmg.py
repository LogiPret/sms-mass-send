#!/usr/bin/env python3
"""
Create a styled DMG installer for SMS Campaign.
Features a dark background with arrow pointing from app to Applications.
"""

import subprocess
import os
import tempfile
import time
from pathlib import Path

MAC_APP_DIR = Path(__file__).parent
DIST_DIR = MAC_APP_DIR / "dist"

# DMG background as base64-encoded PNG (dark gradient with arrow)
# We'll create it programmatically using HTML + screenshot or simple approach

def create_background_image(output_path, width=540, height=380):
    """Create a background image for the DMG using ImageMagick."""
    
    png_path = str(output_path.with_suffix('.png'))
    
    # Create gradient background with arrow using ImageMagick
    result = subprocess.run([
        "convert", 
        "-size", f"{width}x{height}",
        # Dark gradient background
        "gradient:#1a1a2e-#0f3460",
        # Title at top
        "-font", "Helvetica-Bold", "-pointsize", "24", "-fill", "white",
        "-gravity", "North", "-annotate", "+0+35", "Installer SMS Campaign",
        # Instructions at bottom
        "-font", "Helvetica", "-pointsize", "14", "-fill", "#888888",
        "-gravity", "South", "-annotate", "+0+30", "Glissez vers Applications",
        # Arrow line (thicker)
        "-stroke", "#667eea", "-strokewidth", "5",
        "-draw", f"line {width//2 - 70},{height//2 + 20} {width//2 + 50},{height//2 + 20}",
        # Arrow head (filled triangle)
        "-stroke", "none", "-fill", "#667eea",
        "-draw", f"polygon {width//2 + 50},{height//2 + 5} {width//2 + 75},{height//2 + 20} {width//2 + 50},{height//2 + 35}",
        png_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(png_path):
        print("✅ Background image created")
        return Path(png_path)
    else:
        print(f"Background creation failed: {result.stderr}")
        return None


def create_styled_dmg(app_path, output_dmg, volume_name="SMS Campaign"):
    """Create a styled DMG with custom background and icon positions."""
    
    print("Creating styled DMG installer...")
    
    # Paths
    temp_dir = Path(tempfile.mkdtemp())
    dmg_temp = temp_dir / "dmg_contents"
    dmg_temp.mkdir()
    background_dir = dmg_temp / ".background"
    background_dir.mkdir()
    
    # Copy app
    app_dest = dmg_temp / "SMS Campaign.app"
    subprocess.run(["cp", "-R", str(app_path), str(app_dest)], check=True)
    
    # Create Applications symlink
    apps_link = dmg_temp / "Applications"
    subprocess.run(["ln", "-s", "/Applications", str(apps_link)], check=True)
    
    # Create background image using ImageMagick
    bg_png = create_background_image(background_dir / "background")
    
    # Create temporary writable DMG
    temp_dmg = temp_dir / "temp.dmg"
    
    subprocess.run([
        "hdiutil", "create",
        "-volname", volume_name,
        "-srcfolder", str(dmg_temp),
        "-format", "UDRW",
        "-fs", "HFS+",
        str(temp_dmg)
    ], check=True)
    
    # Mount the DMG
    mount_result = subprocess.run([
        "hdiutil", "attach", str(temp_dmg), "-readwrite", "-noverify", "-noautoopen"
    ], capture_output=True, text=True, check=True)
    
    # Find mount point
    mount_point = None
    for line in mount_result.stdout.split('\n'):
        if volume_name in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                mount_point = parts[-1].strip()
                break
    
    if not mount_point:
        mount_point = f"/Volumes/{volume_name}"
    
    print(f"DMG mounted at: {mount_point}")
    
    # Wait a moment for mount
    time.sleep(1)
    
    # Use AppleScript to customize the DMG window
    applescript = f'''
    tell application "Finder"
        tell disk "{volume_name}"
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set bounds of container window to {{100, 100, 640, 480}}
            set viewOptions to the icon view options of container window
            set arrangement of viewOptions to not arranged
            set icon size of viewOptions to 80
            
            -- Position the icons
            set position of item "SMS Campaign.app" of container window to {{130, 200}}
            set position of item "Applications" of container window to {{410, 200}}
            
            close
            open
            update without registering applications
            delay 1
        end tell
    end tell
    '''
    
    subprocess.run(["osascript", "-e", applescript], capture_output=True)
    
    # Set custom background if we have one
    if bg_png and bg_png.exists():
        bg_dest = Path(mount_point) / ".background"
        bg_dest.mkdir(exist_ok=True)
        subprocess.run(["cp", str(bg_png), str(bg_dest / "background.png")])
        
        # Set background via AppleScript
        bg_script = f'''
        tell application "Finder"
            tell disk "{volume_name}"
                open
                set current view of container window to icon view
                set viewOptions to the icon view options of container window
                set background picture of viewOptions to file ".background:background.png"
                close
                open
                update without registering applications
            end tell
        end tell
        '''
        subprocess.run(["osascript", "-e", bg_script], capture_output=True)
    
    time.sleep(1)
    
    # Unmount
    subprocess.run(["hdiutil", "detach", mount_point, "-quiet"], capture_output=True)
    
    # Convert to compressed read-only DMG
    subprocess.run(["rm", "-f", str(output_dmg)])
    subprocess.run([
        "hdiutil", "convert", str(temp_dmg),
        "-format", "UDZO",
        "-imagekey", "zlib-level=9",
        "-o", str(output_dmg)
    ], check=True)
    
    # Cleanup
    subprocess.run(["rm", "-rf", str(temp_dir)])
    
    print(f"✅ Created styled DMG: {output_dmg}")
    return True


def main():
    """Main entry point."""
    launcher_app = DIST_DIR / "SMS Campaign Launcher.app"
    output_dmg = DIST_DIR / "SMS.Campaign.Installer.dmg"
    
    if not launcher_app.exists():
        print(f"Error: {launcher_app} not found")
        print("Build the launcher first with: pyinstaller launcher_v2.py")
        return False
    
    return create_styled_dmg(launcher_app, output_dmg)


if __name__ == "__main__":
    main()
