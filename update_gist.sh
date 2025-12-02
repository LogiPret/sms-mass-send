#!/bin/bash
# SMS Mass Send - Gist Update Script
# Run this script after making changes to update the online version

SCRIPT_PATH="$(dirname "$0")/app/script.js"
GIST_ID_FILE="$(dirname "$0")/.gist_id"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found at $SCRIPT_PATH"
    exit 1
fi

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "📱 First time setup - logging into GitHub..."
    gh auth login
fi

# Check if we have an existing Gist
if [ -f "$GIST_ID_FILE" ]; then
    GIST_ID=$(cat "$GIST_ID_FILE")
    echo "📤 Updating existing Gist: $GIST_ID"
    gh gist edit "$GIST_ID" "$SCRIPT_PATH"
    
    if [ $? -eq 0 ]; then
        echo "✅ Gist updated successfully!"
        echo ""
        echo "🔗 Raw URL (for Scriptable install link):"
        echo "https://gist.githubusercontent.com/$(gh api user -q .login)/$GIST_ID/raw/script.js"
        echo ""
        echo "📲 Install link:"
        echo "scriptable:///add?scriptName=SMS%20Mass%20Send&url=https://gist.githubusercontent.com/$(gh api user -q .login)/$GIST_ID/raw/script.js"
    else
        echo "❌ Failed to update Gist"
        exit 1
    fi
else
    echo "🆕 Creating new Gist..."
    RESULT=$(gh gist create "$SCRIPT_PATH" --public --desc "SMS Mass Send - Scriptable Script" 2>&1)
    
    if [ $? -eq 0 ]; then
        # Extract Gist ID from URL
        GIST_ID=$(echo "$RESULT" | grep -oE '[a-f0-9]{32}' | head -1)
        echo "$GIST_ID" > "$GIST_ID_FILE"
        
        echo "✅ Gist created successfully!"
        echo ""
        echo "🔗 Gist URL: $RESULT"
        echo ""
        echo "📲 Install link for clients:"
        USERNAME=$(gh api user -q .login)
        echo "scriptable:///add?scriptName=SMS%20Mass%20Send&url=https://gist.githubusercontent.com/$USERNAME/$GIST_ID/raw/script.js"
    else
        echo "❌ Failed to create Gist: $RESULT"
        exit 1
    fi
fi
