#!/bin/bash
# ============================================
# SMS Campaign - Build Script
# Creates the unsigned .app bundle using PyInstaller
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔧 SMS Campaign Mac App Builder"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found${NC}"
    echo "Install with: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"

# Create/activate virtual environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
fi

echo "🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check for PyInstaller in venv
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  PyInstaller not found. Installing...${NC}"
    pip install --upgrade pip
    pip install pyinstaller
fi

PYINSTALLER_VERSION=$(python -c "import PyInstaller; print(PyInstaller.__version__)")
echo -e "${GREEN}✓ PyInstaller $PYINSTALLER_VERSION${NC}"

# Clean previous builds
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf build dist "SMS Campaign.app" 2>/dev/null || true

# Get version from sms_campaign.py
VERSION=$(grep -m1 'SCRIPT_VERSION = ' sms_campaign.py | cut -d'"' -f2)
echo -e "${GREEN}📦 Building version $VERSION${NC}"
echo ""

# Build with PyInstaller
echo "🔨 Building .app bundle..."
python -m PyInstaller "SMS Campaign.spec" --clean --noconfirm

# Deactivate venv
deactivate

# Check if build succeeded
if [ -d "dist/SMS Campaign.app" ]; then
    echo ""
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    
    # Get app size
    APP_SIZE=$(du -sh "dist/SMS Campaign.app" | cut -f1)
    echo "📊 App size: $APP_SIZE"
    
    # Copy to root of mac_app folder for easy access
    rm -rf "SMS Campaign.app" 2>/dev/null || true
    cp -r "dist/SMS Campaign.app" "SMS Campaign.app"
    
    echo ""
    echo "📍 App location: $SCRIPT_DIR/SMS Campaign.app"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📦 Distribution:"
    echo "   1. ZIP the app: zip -r 'SMS Campaign.zip' 'SMS Campaign.app'"
    echo "   2. Share the ZIP file with users"
    echo ""
    echo "📱 First-time launch (users need to do this once):"
    echo "   • Right-click the app → Open → Click 'Open' in dialog"
    echo "   • OR run: xattr -cr 'SMS Campaign.app'"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the output above for errors."
    exit 1
fi
