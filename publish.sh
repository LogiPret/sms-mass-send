#!/bin/bash
# Publish script - Updates public Gist and pushes to private repo
# Gist is public (for auto-updates), repo is private (for development)
# Only updates gist/version if sms_automatisation.js has changed

# Configuration
GIST_ID="0e0f68902ace0bfe94e0e83a8f89db2e"
SCRIPT_SOURCE="app/sms_automatisation.js"
VERSION_FILE="version.json"
BUILD_FILE=".build_number"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== SMS Mass Send - Publisher ===${NC}"

# Check if we're in the right directory
if [ ! -f "$SCRIPT_SOURCE" ]; then
    echo -e "${RED}Error: Cannot find $SCRIPT_SOURCE${NC}"
    echo "Run this script from the sms_mass_send directory"
    exit 1
fi

# Check if sms_automatisation.js has changed (staged or unstaged)
SCRIPT_CHANGED=false
if git diff --name-only HEAD 2>/dev/null | grep -q "sms_automatisation.js\|app/sms_automatisation.js"; then
    SCRIPT_CHANGED=true
fi
if git diff --cached --name-only 2>/dev/null | grep -q "sms_automatisation.js\|app/sms_automatisation.js"; then
    SCRIPT_CHANGED=true
fi
# Also check untracked changes
if git status --porcelain 2>/dev/null | grep -q "sms_automatisation.js"; then
    SCRIPT_CHANGED=true
fi

if [ "$SCRIPT_CHANGED" = false ]; then
    echo -e "${BLUE}ℹ️  No changes to sms_automatisation.js${NC}"
    echo -e "${BLUE}   Skipping version bump and gist update.${NC}"
    echo ""
    
    # Still commit and push other changes
    read -p "Push other changes to repo? (y/n): " PUSH_OTHER
    if [ "$PUSH_OTHER" = "y" ]; then
        git add -A
        read -p "Commit message: " COMMIT_MSG
        git commit -m "$COMMIT_MSG"
        git push -u origin main
        echo -e "${GREEN}✅ Pushed to repo (no gist update)${NC}"
    fi
    exit 0
fi

echo -e "${YELLOW}📱 Mobile script changed - updating version and gist${NC}"

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
cp "$SCRIPT_SOURCE" "sms_automatisation.js"

# Create a nice README
cat > "README.md" << 'EOF'
# SMS Mass Send 📱

Script Scriptable pour envoyer des SMS en masse depuis un fichier CSV.

## Plateformes

- **iPhone**: Script Scriptable avec auto-update
- **Mac**: Application web Python (dossier `mac_app/`)

## Installation iPhone

1. Télécharge le script depuis le [Gist public](https://gist.github.com/HugoOtth/0e0f68902ace0bfe94e0e83a8f89db2e)
2. Ouvre-le avec Scriptable sur iPhone
3. C'est prêt!

## Installation Mac

```bash
cd mac_app
./SMS\ Campaign.command
```

## Mise à jour automatique

Le script iPhone vérifie automatiquement les mises à jour à chaque lancement.

## Fonctionnalités

- 📂 Import CSV depuis iCloud/Files
- 📱 Détection automatique des numéros (mobile > work > home)
- 🔤 Variables personnalisées (**PRENOM**, **NOM** ou {name})
- 👁️ Prévisualisation avant envoi
- 🇫🇷 Support des accents français
- 🌐 Interface FR/EN (Mac)
EOF

# Git operations - push to private repo
echo -e "${YELLOW}Pushing to private repo...${NC}"
git add -A
git commit -m "v$FULL_VERSION: $CHANGELOG"
git branch -M main
git push -u origin main

# Sync to public Gist for auto-updates
echo -e "${YELLOW}Syncing to public Gist...${NC}"
gh gist edit "$GIST_ID" -f sms_automatisation.js -f version.json

echo ""
echo -e "${GREEN}=== Published v$FULL_VERSION! ===${NC}"
echo ""
echo "Private repo: https://github.com/LogiPret/sms-mass-send"
echo "Public Gist:  https://gist.github.com/HugoOtth/$GIST_ID"
echo ""
echo "Update URLs (public):"
echo "  Script:  https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/sms_automatisation.js"
echo "  Version: https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/version.json"

# Check if Mac app also needs publishing
MAC_GIST_ID_FILE="mac_app/.mac_gist_id"
if [ -f "$MAC_GIST_ID_FILE" ]; then
    MAC_CHANGED=false
    if git diff --name-only HEAD~1 2>/dev/null | grep -q "mac_app/sms_campaign.py"; then
        MAC_CHANGED=true
    fi
    
    if [ "$MAC_CHANGED" = true ]; then
        echo ""
        echo -e "${YELLOW}Mac app also changed - publishing to Mac gist...${NC}"
        cd mac_app
        ./publish_mac.sh
        cd ..
    fi
fi
