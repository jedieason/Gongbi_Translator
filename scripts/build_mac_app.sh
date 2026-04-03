#!/bin/bash

# Configuration
APP_NAME="Gongbi Translator"
DMG_NAME="Gongbi_Translator_v1.0.dmg"
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPTS_DIR/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
ASSETS_DIR="$ROOT_DIR/assets"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python3"

# Exit on error
set -e

echo "🚀 Starting Premium Build for $APP_NAME..."

# 1. Cleanup
echo "🧹 Cleaning previous build artifacts..."
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist"
rm -f "$ROOT_DIR/*.spec"

# 2. Bundle App
echo "🛠️ Creating .app bundle with PyInstaller..."
"$VENV_PYTHON" -m PyInstaller --noconfirm --windowed \
    --icon="$ASSETS_DIR/icon.icns" \
    --name "$APP_NAME" \
    --add-data "core_engine.py:." \
    --add-data "assets/icon.png:." \
    --hidden-import "webview" \
    --hidden-import "docx" \
    --hidden-import "deep_translator" \
    "$ROOT_DIR/app_gui.py"

# Wait for PyInstaller to finish (it should be synchronous if called correctly)

# 3. Prepare DMG Staging
echo "📦 Preparing DMG staging volume..."
STAGING_DIR="$DIST_DIR/staging"
mkdir -p "$STAGING_DIR/.background"
cp "$ASSETS_DIR/dmg_background.png" "$STAGING_DIR/.background/background.png"
ln -s /Applications "$STAGING_DIR/Applications"
cp -R "$DIST_DIR/$APP_NAME.app" "$STAGING_DIR/"

# 4. Create Initial DMG
echo "📀 Creating temporary disk image..."
TEMP_DMG="$DIST_DIR/temp.dmg"
hdiutil create -srcfolder "$STAGING_DIR" -volname "$APP_NAME Installation" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW "$TEMP_DMG"

# 5. Configure Visuals via AppleScript
echo "🎨 Configuring DMG layout and background..."
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$TEMP_DMG" | egrep '^/dev/' | sed 1q | awk '{print $1}')
VOLUME_PATH="/Volumes/$APP_NAME Installation"

# Give it a second to mount
sleep 2

# AppleScript to set layout
osascript <<EOF
tell application "Finder"
    tell disk "$APP_NAME Installation"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 400 + 800, 100 + 500}
        set theViewOptions to the icon view options of container window
        set icon size of theViewOptions to 120
        set arrangement of theViewOptions to not arranged
        set background picture of theViewOptions to file ".background:background.png"
        
        # Positions: {x, y}
        # Based on a 800x500 window
        set position of item "$APP_NAME.app" of container window to {200, 250}
        set position of item "Applications" of container window to {600, 250}
        
        update (path to current folder)
        # Give some time for changes to persist
        delay 2
        close
    end tell
end tell
EOF

# Unmount
echo "🔌 Finalizing storage..."
chmod -Rf go-w "$VOLUME_PATH"
sync
hdiutil detach "$DEVICE"

# 6. Convert to Final DMG
echo "🗜️ Converting to compressed production DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -imagekey zlib-level=9 -o "$DIST_DIR/$DMG_NAME"

# Cleanup
rm -f "$TEMP_DMG"
rm -rf "$STAGING_DIR"

echo ""
echo "✨ PROGRESS COMPLETE! ✨"
echo "✅ DMG: $DIST_DIR/$DMG_NAME"
echo ""
echo "You can now distribute the DMG file."
