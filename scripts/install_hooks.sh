#!/bin/bash
# Install Git hooks for SMS Campaign auto-versioning

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Not in a git repository"
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"
SCRIPTS_HOOKS="$REPO_ROOT/scripts/hooks"

echo "Installing Git hooks..."

# Pre-commit hook
if [ -f "$SCRIPTS_HOOKS/pre-commit" ]; then
    cp "$SCRIPTS_HOOKS/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "✅ Installed pre-commit hook"
fi

# Pre-push hook
if [ -f "$SCRIPTS_HOOKS/pre-push" ]; then
    cp "$SCRIPTS_HOOKS/pre-push" "$HOOKS_DIR/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    echo "✅ Installed pre-push hook"
fi

echo ""
echo "Git hooks installed!"
echo ""
echo "How it works:"
echo "  - On commit: If mac_app/ files changed, version auto-bumps (patch)"
echo "  - On push: If local version > remote, creates GitHub release"
echo ""
echo "Manual commands:"
echo "  python3 scripts/version_manager.py bump        # Bump patch"
echo "  python3 scripts/version_manager.py bump-minor  # Bump minor"
echo "  python3 scripts/version_manager.py bump-major  # Bump major"
echo "  python3 scripts/version_manager.py release     # Create release"
