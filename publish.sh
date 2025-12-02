#!/bin/bash
# Publish script - Updates public Gist and pushes to private repo
# Gist is public (for auto-updates), repo is private (for development)

# Configuration
GIST_ID="0e0f68902ace0bfe94e0e83a8f89db2e"
SCRIPT_SOURCE="app/script.js"
VERSION_FILE="version.json"
BUILD_FILE=".build_number"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== SMS Mass Send - Publisher ===${NC}"

# Check if we're in the right directory
if [ ! -f "$SCRIPT_SOURCE" ]; then
    echo -e "${RED}Error: Cannot find $SCRIPT_SOURCE${NC}"
    echo "Run this script from the sms_mass_send directory"
    exit 1
fi

# Read current build number or start at 0
if [ -f "$BUILD_FILE" ]; then
    BUILD=$(cat "$BUILD_FILE")
else
    BUILD=0
fi

# Increment build number
BUILD=$((BUILD + 1))
echo $BUILD > "$BUILD_FILE"

# Get base version from script (major.minor only)
CURRENT_FULL=$(grep 'const SCRIPT_VERSION' "$SCRIPT_SOURCE" | sed 's/.*"\(.*\)".*/\1/')
# Extract just major.minor (e.g., "1.0" from "1.0.5" or "1.0")
BASE_VERSION=$(echo "$CURRENT_FULL" | sed 's/^\([0-9]*\.[0-9]*\).*/\1/')

echo -e "Current base version: ${YELLOW}$BASE_VERSION${NC}"
echo -e "Current build: ${YELLOW}$((BUILD - 1))${NC} → ${GREEN}$BUILD${NC}"

# Ask if user wants to bump major.minor version
read -p "Bump version? (Enter for no, or type new version like 1.1): " NEW_BASE
if [ -n "$NEW_BASE" ]; then
    BASE_VERSION=$NEW_BASE
    echo -e "${GREEN}Version bumped to $BASE_VERSION${NC}"
fi

# Full version with build number
FULL_VERSION="${BASE_VERSION}.${BUILD}"

# Ask for changelog
read -p "Changelog (optional): " CHANGELOG
if [ -z "$CHANGELOG" ]; then
    CHANGELOG="Build $BUILD"
fi

# Update version in script
sed -i '' "s/const SCRIPT_VERSION = \"[^\"]*\"/const SCRIPT_VERSION = \"$FULL_VERSION\"/" "$SCRIPT_SOURCE"
echo -e "${GREEN}Updated script to version $FULL_VERSION${NC}"

# Update version.json
cat > "$VERSION_FILE" << EOF
{
    "version": "$FULL_VERSION",
    "changelog": "$CHANGELOG",
    "date": "$(date +%Y-%m-%d)",
    "build": $BUILD
}
EOF
echo -e "${GREEN}Updated version.json${NC}"

# Copy script to root for easy access
cp "$SCRIPT_SOURCE" "script.js"

# Create a nice README
cat > "README.md" << 'EOF'
# SMS Mass Send 📱

Script Scriptable pour envoyer des SMS en masse depuis un fichier CSV.

## Installation

1. Télécharge le script depuis le [Gist public](https://gist.github.com/HugoOtth/0e0f68902ace0bfe94e0e83a8f89db2e)
2. Ouvre-le avec Scriptable sur iPhone
3. C'est prêt!

## Mise à jour automatique

Le script vérifie automatiquement les mises à jour à chaque lancement.

## Fonctionnalités

- 📂 Import CSV depuis iCloud/Files
- 📱 Détection automatique des numéros (mobile > work > home)
- 🔤 Variables personnalisées (**PRENOM**, **NOM**)
- 👁️ Prévisualisation avant envoi
- 🇫🇷 Support des accents français
EOF

# Git operations - push to private repo
echo -e "${YELLOW}Pushing to private repo...${NC}"
git add script.js version.json README.md "$BUILD_FILE" "$SCRIPT_SOURCE"
git commit -m "v$FULL_VERSION: $CHANGELOG"
git branch -M main
git push -u origin main

# Sync to public Gist for auto-updates
echo -e "${YELLOW}Syncing to public Gist...${NC}"
gh gist edit "$GIST_ID" -f script.js -f version.json

echo ""
echo -e "${GREEN}=== Published v$FULL_VERSION! ===${NC}"
echo ""
echo "Private repo: https://github.com/LogiPret/sms-mass-send"
echo "Public Gist:  https://gist.github.com/HugoOtth/$GIST_ID"
echo ""
echo "Update URLs (public):"
echo "  Script:  https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/script.js"
echo "  Version: https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/version.json"
