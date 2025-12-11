#!/bin/bash
# SMS Campaign - Publish Script
# This script builds the app, creates a ZIP, and provides instructions for release

set -e

echo "🔨 SMS Campaign - Build & Publish"
echo "=================================="

# Get version from version.json
VERSION=$(python3 -c "import json; print(json.load(open('version.json'))['version'])")
echo "📦 Version: $VERSION"

# Build the app
echo ""
echo "🏗️  Building app..."
source .venv/bin/activate
pyinstaller -y --onefile --windowed --name "SMS Campaign" --add-data "version.json:." sms_campaign.py

# Create ZIP
echo ""
echo "📦 Creating ZIP..."
cd dist
rm -f "SMS Campaign.zip"
zip -r "SMS Campaign.zip" "SMS Campaign.app"

# Get file size
SIZE=$(du -h "SMS Campaign.zip" | cut -f1)
echo "✅ Created: SMS Campaign.zip ($SIZE)"

cd ..

echo ""
echo "=================================="
echo "📤 NEXT STEPS TO PUBLISH:"
echo "=================================="
echo ""
echo "1. Go to: https://github.com/LogiPret/sms-mass-send/releases/new"
echo ""
echo "2. Create release:"
echo "   - Tag: v$VERSION"
echo "   - Title: SMS Campaign v$VERSION"
echo "   - Upload: dist/SMS Campaign.zip"
echo ""
echo "3. Update Gist version.json:"
echo "   - Go to: https://gist.github.com/hugootth/3e89759cac04be452c935c90b5733eea"
echo "   - Update 'version' to: $VERSION"
echo ""
echo "4. Test update:"
echo "   - Open an older version of the app"
echo "   - It should show update banner"
echo "   - Click 'Update' to verify it works"
echo ""
echo "=================================="
echo "✅ Build complete!"
