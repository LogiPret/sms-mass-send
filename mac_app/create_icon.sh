#!/bin/bash
# Convert a PNG to macOS .icns format
# Usage: ./create_icon.sh source.png output.icns

set -e

SOURCE="${1:-icon.png}"
OUTPUT="${2:-icon.icns}"
ICONSET="AppIcon.iconset"

if [ ! -f "$SOURCE" ]; then
    echo "❌ Source file not found: $SOURCE"
    echo "Usage: ./create_icon.sh source.png [output.icns]"
    exit 1
fi

echo "🎨 Creating icon from $SOURCE..."

# Clean up any previous iconset
rm -rf "$ICONSET"
mkdir -p "$ICONSET"

# Generate all required sizes using sips (built into macOS)
declare -a sizes=("16" "32" "64" "128" "256" "512" "1024")

for size in "${sizes[@]}"; do
    sips -z "$size" "$size" "$SOURCE" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null 2>&1
done

# Rename files to match Apple's naming convention
mv "$ICONSET/icon_16x16.png" "$ICONSET/icon_16x16.png" 2>/dev/null || true
mv "$ICONSET/icon_32x32.png" "$ICONSET/icon_16x16@2x.png" 2>/dev/null || true
cp "$ICONSET/icon_16x16@2x.png" "$ICONSET/icon_32x32.png" 2>/dev/null || true
mv "$ICONSET/icon_64x64.png" "$ICONSET/icon_32x32@2x.png" 2>/dev/null || true
mv "$ICONSET/icon_128x128.png" "$ICONSET/icon_128x128.png" 2>/dev/null || true
mv "$ICONSET/icon_256x256.png" "$ICONSET/icon_128x128@2x.png" 2>/dev/null || true
cp "$ICONSET/icon_128x128@2x.png" "$ICONSET/icon_256x256.png" 2>/dev/null || true
mv "$ICONSET/icon_512x512.png" "$ICONSET/icon_256x256@2x.png" 2>/dev/null || true
cp "$ICONSET/icon_256x256@2x.png" "$ICONSET/icon_512x512.png" 2>/dev/null || true
mv "$ICONSET/icon_1024x1024.png" "$ICONSET/icon_512x512@2x.png" 2>/dev/null || true

# Convert iconset to icns
iconutil -c icns "$ICONSET" -o "$OUTPUT"

# Cleanup
rm -rf "$ICONSET"

echo "✅ Created: $OUTPUT"
ls -lh "$OUTPUT"
