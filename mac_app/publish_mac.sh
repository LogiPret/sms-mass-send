#!/bin/bash
# Publish Mac SMS Campaign to public Gist
# Creates/updates a public Gist for auto-updates
# Only updates gist/version if mac_app files have changed

# Configuration
GIST_ID_FILE="$(dirname "$0")/.mac_gist_id"
SCRIPT_SOURCE="$(dirname "$0")/sms_campaign.py"
VERSION_FILE="$(dirname "$0")/version.json"
BUILD_FILE="$(dirname "$0")/.mac_build_number"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${GREEN}=== Mac SMS Campaign - Publisher ===${NC}"

# Check if script exists
if [ ! -f "$SCRIPT_SOURCE" ]; then
    echo -e "${RED}Error: Cannot find $SCRIPT_SOURCE${NC}"
    exit 1
fi

# Check if gh CLI is authenticated
if ! gh auth status &>/dev/null; then
    echo -e "${YELLOW}📱 First time setup - logging into GitHub...${NC}"
    gh auth login
fi

# Check if mac_app files have changed (staged or unstaged)
MAC_CHANGED=false
if git diff --name-only HEAD 2>/dev/null | grep -q "mac_app/"; then
    MAC_CHANGED=true
fi
if git diff --cached --name-only 2>/dev/null | grep -q "mac_app/"; then
    MAC_CHANGED=true
fi
# Also check untracked/modified files
if git status --porcelain 2>/dev/null | grep -q "mac_app/"; then
    MAC_CHANGED=true
fi

if [ "$MAC_CHANGED" = false ]; then
    echo -e "${BLUE}ℹ️  No changes to mac_app/ files${NC}"
    echo -e "${BLUE}   Skipping version bump and gist update.${NC}"
    echo ""
    
    # Still offer to push other changes
    read -p "Push other changes to repo? (y/n): " PUSH_OTHER
    if [ "$PUSH_OTHER" = "y" ]; then
        cd ..
        git add -A
        read -p "Commit message: " COMMIT_MSG
        git commit -m "$COMMIT_MSG"
        git push -u origin main
        echo -e "${GREEN}✅ Pushed to repo (no gist update)${NC}"
    fi
    exit 0
fi

echo -e "${YELLOW}📱 Mac app files changed - updating version and gist${NC}"

# Read current build number or start at 0
if [ -f "$BUILD_FILE" ]; then
    BUILD=$(cat "$BUILD_FILE")
else
    BUILD=0
fi

# Increment build number
BUILD=$((BUILD + 1))
echo $BUILD > "$BUILD_FILE"

# Get current version from script
CURRENT_VERSION=$(grep 'SCRIPT_VERSION = "' "$SCRIPT_SOURCE" | sed 's/.*"\(.*\)".*/\1/' | head -1)
BASE_VERSION=$(echo "$CURRENT_VERSION" | sed 's/^\([0-9]*\.[0-9]*\).*/\1/')

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
sed -i '' "s/SCRIPT_VERSION = \"[^\"]*\"/SCRIPT_VERSION = \"$FULL_VERSION\"/" "$SCRIPT_SOURCE"
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

# Check if we have an existing Gist
if [ -f "$GIST_ID_FILE" ]; then
    GIST_ID=$(cat "$GIST_ID_FILE")
    echo -e "${YELLOW}Updating existing Gist: $GIST_ID${NC}"
    
    gh gist edit "$GIST_ID" -f sms_campaign.py -f version.json
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}=== Published v$FULL_VERSION! ===${NC}"
        echo ""
        echo "Gist URL: https://gist.github.com/HugoOtth/$GIST_ID"
        echo ""
        echo "Update URLs (public):"
        echo "  Script:  https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/sms_campaign.py"
        echo "  Version: https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/version.json"
    else
        echo -e "${RED}Failed to update Gist${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Creating new public Gist...${NC}"
    
    # Create gist with both files
    RESULT=$(gh gist create sms_campaign.py version.json --public --desc "Mac SMS Campaign - Auto-updating mass SMS sender" 2>&1)
    
    if [ $? -eq 0 ]; then
        # Extract Gist ID from URL
        GIST_ID=$(echo "$RESULT" | grep -oE '[a-f0-9]{32}' | head -1)
        
        if [ -z "$GIST_ID" ]; then
            # Try alternative extraction
            GIST_ID=$(echo "$RESULT" | grep -oE 'gist\.github\.com/[^/]+/([a-f0-9]+)' | sed 's/.*\///')
        fi
        
        if [ -n "$GIST_ID" ]; then
            echo "$GIST_ID" > "$GIST_ID_FILE"
            
            # Now update the script with the correct GIST_ID
            sed -i '' "s/GIST_ID = \"mac_sms_campaign\"/GIST_ID = \"$GIST_ID\"/" "$SCRIPT_SOURCE"
            
            # Update the gist again with the correct ID embedded
            gh gist edit "$GIST_ID" -f sms_campaign.py
            
            echo ""
            echo -e "${GREEN}=== Gist Created! ===${NC}"
            echo ""
            echo "Gist ID: $GIST_ID"
            echo "Gist URL: $RESULT"
            echo ""
            echo "Update URLs (public):"
            echo "  Script:  https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/sms_campaign.py"
            echo "  Version: https://gist.githubusercontent.com/HugoOtth/$GIST_ID/raw/version.json"
            echo ""
            echo -e "${YELLOW}⚠️  IMPORTANT: Re-run publish_mac.sh to embed the correct GIST_ID${NC}"
        else
            echo -e "${RED}Failed to extract Gist ID from: $RESULT${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Failed to create Gist: $RESULT${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Note: Users with the app will see update notification on next launch.${NC}"
