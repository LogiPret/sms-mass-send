#!/usr/bin/env python3
"""
Create a styled DMG installer for SMS Campaign using create-dmg.
Features a dark background with proper icon positioning.
"""

import subprocess
import os
import tempfile
from pathlib import Path

MAC_APP_DIR = Path(__file__).parent
DIST_DIR = MAC_APP_DIR / "dist"


def create_background_image(output_path, width=600, height=400):
    """Create a background image for the DMG using ImageMagick."""
    
    png_path = str(output_path)
    
    # Icons are at Y=185 (from top of content area, not window)
    # Window bounds: 200,120 to 800,520 = 600x400
    # But there's ~50px for title bar, so content is ~350px
    # Arrow should be at roughly Y=200 (slightly below center to align with icon centers)
    arrow_y = 210
    
    # Create gradient background with arrow using ImageMagick
    result = subprocess.run([
        "convert", 
        "-size", f"{width}x{height}",
        # Dark gradient background
        "gradient:#1a1a2e-#0f3460",
        # Title at top
        "-font", "Helvetica-Bold", "-pointsize", "28", "-fill", "white",
        "-gravity", "North", "-annotate", "+0+40", "SMS Campaign",
        # Instructions at bottom
        "-font", "Helvetica", "-pointsize", "16", "-fill", "#888888",
        "-gravity", "South", "-annotate", "+0+35", "Glissez l'application vers Applications",
        # Arrow line (centered, at icon height)
        "-stroke", "#667eea", "-strokewidth", "6",
        "-draw", f"line {width//2 - 80},{arrow_y} {width//2 + 60},{arrow_y}",
        # Arrow head (filled triangle)
        "-stroke", "none", "-fill", "#667eea",
        "-draw", f"polygon {width//2 + 60},{arrow_y - 15} {width//2 + 90},{arrow_y} {width//2 + 60},{arrow_y + 15}",
        png_path
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and os.path.exists(png_path):
        print("✅ Background image created")
        return Path(png_path)
    else:
        print(f"Background creation failed: {result.stderr}")
        # Create a simple fallback background
        fallback = subprocess.run([
            "convert",
            "-size", f"{width}x{height}",
            "xc:#1a1a2e",
            "-font", "Helvetica-Bold", "-pointsize", "24", "-fill", "white",
            "-gravity", "Center", "-annotate", "+0-60", "SMS Campaign",
            "-font", "Helvetica", "-pointsize", "14", "-fill", "#888888",
            "-gravity", "South", "-annotate", "+0+30", "Drag to Applications →",
            png_path
        ], capture_output=True, text=True)
        
        if fallback.returncode == 0:
            print("✅ Fallback background created")
            return Path(png_path)
        return None


def create_styled_dmg(app_path, output_dmg, volume_name="SMS Campaign"):
    """Create a styled DMG using create-dmg tool."""
    
    print("Creating styled DMG installer...")
    
    # Use a unique volume name to avoid conflicts
    import time as time_module
    unique_vol = f"SMSCampaign{int(time_module.time())}"
    
    # Create temporary directory for background and staging
    temp_dir = Path(tempfile.mkdtemp())
    bg_path = temp_dir / "background.png"
    
    # Copy app with proper name - use quotes in AppleScript
    staged_app = temp_dir / "SMS Campaign.app"
    subprocess.run(["cp", "-R", str(app_path), str(staged_app)], check=True)
    
    # Create background image
    create_background_image(bg_path, width=600, height=400)
    
    # Remove existing DMG
    if output_dmg.exists():
        output_dmg.unlink()
    
    # Create a temporary folder with the content
    dmg_content = temp_dir / "dmg_content"
    dmg_content.mkdir()
    subprocess.run(["cp", "-R", str(staged_app), str(dmg_content / "SMS Campaign.app")], check=True)
    subprocess.run(["ln", "-s", "/Applications", str(dmg_content / "Applications")], check=True)
    
    # Copy background
    bg_dir = dmg_content / ".background"
    bg_dir.mkdir()
    if bg_path.exists():
        subprocess.run(["cp", str(bg_path), str(bg_dir / "background.png")], check=True)
    
    # Create writable DMG with unique name
    temp_dmg = temp_dir / "temp.dmg"
    subprocess.run([
        "hdiutil", "create",
        "-volname", unique_vol,
        "-srcfolder", str(dmg_content),
        "-format", "UDRW",
        "-fs", "HFS+",
        str(temp_dmg)
    ], check=True, capture_output=True)
    
    # Mount the DMG
    mount_result = subprocess.run([
        "hdiutil", "attach", str(temp_dmg), 
        "-readwrite", "-noverify", "-noautoopen"
    ], capture_output=True, text=True, check=True)
    
    # Find mount point from output
    mount_point = f"/Volumes/{unique_vol}"
    for line in mount_result.stdout.split('\n'):
        if '/Volumes/' in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                mount_point = parts[-1].strip()
                break
    
    print(f"Mounted at: {mount_point}")
    time_module.sleep(2)
    
    # Apply styling via AppleScript using mount point path
    applescript = f'''
    tell application "Finder"
        set dmgVolume to POSIX file "{mount_point}" as alias
        tell folder dmgVolume
            open
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set bounds of container window to {{200, 120, 800, 520}}
            
            set theViewOptions to the icon view options of container window
            set arrangement of theViewOptions to not arranged
            set icon size of theViewOptions to 80
            set background picture of theViewOptions to file ".background:background.png"
            
            set position of item "SMS Campaign.app" of container window to {{150, 185}}
            set position of item "Applications" of container window to {{450, 185}}
            
            update without registering applications
            delay 2
            close
        end tell
    end tell
    '''
    
    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"AppleScript warning: {result.stderr}")
    
    # Wait for Finder to write .DS_Store
    time_module.sleep(3)
    subprocess.run(["sync"])
    
    # Rename volume to proper name before converting
    subprocess.run([
        "diskutil", "rename", mount_point, volume_name
    ], capture_output=True)
    time_module.sleep(1)
    
    # Unmount (use new mount point after rename)
    new_mount_point = f"/Volumes/{volume_name}"
    subprocess.run(["hdiutil", "detach", new_mount_point, "-quiet", "-force"], capture_output=True)
    time_module.sleep(1)
    
    # Convert to compressed read-only DMG with proper volume name
    subprocess.run([
        "hdiutil", "convert", str(temp_dmg),
        "-format", "UDZO",
        "-imagekey", "zlib-level=9",
        "-o", str(output_dmg)
    ], check=True, capture_output=True)
    
    # Cleanup
    subprocess.run(["rm", "-rf", str(temp_dir)])
    
    print(f"✅ Created styled DMG: {output_dmg}")
    return True


def create_basic_dmg(app_path, output_dmg, volume_name="SMS Campaign"):
    """Create a basic DMG without styling (fallback)."""
    
    temp_dir = Path(tempfile.mkdtemp())
    dmg_temp = temp_dir / "dmg_contents"
    dmg_temp.mkdir()
    
    # Copy app
    app_dest = dmg_temp / "SMS Campaign.app"
    subprocess.run(["cp", "-R", str(app_path), str(app_dest)], check=True)
    
    # Create Applications symlink
    apps_link = dmg_temp / "Applications"
    subprocess.run(["ln", "-s", "/Applications", str(apps_link)], check=True)
    
    # Create DMG
    subprocess.run([
        "hdiutil", "create",
        "-volname", volume_name,
        "-srcfolder", str(dmg_temp),
        "-ov", "-format", "UDZO",
        str(output_dmg)
    ], check=True)
    
    # Cleanup
    subprocess.run(["rm", "-rf", str(temp_dir)])
    
    if output_dmg.exists():
        print(f"✅ Created basic DMG: {output_dmg}")
        return True
    return False


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
    success = main()
    exit(0 if success else 1)
