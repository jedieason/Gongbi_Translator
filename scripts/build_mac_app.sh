#!/bin/bash

# Exit on error
set -e

# Run from project root (not from scripts/ directory)
cd "$(dirname "$0")/.."

echo "🚀 Starting Gongbi Translator Build Process..."

# 1. Clean previous build attempt
echo "🧹 Cleaning previous build artifacts..."
rm -rf build dist GongbiTranslator.spec "Gongbi Translator.spec"

# 2. Activate Virtual Environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️ Error: .venv not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install pywebview pyobjc pillow python-docx deep-translator pyinstaller"
    exit 1
fi

# 3. Install Dependencies (comment out after first successful run to save time)
# echo "📥 Ensuring all dependencies are ready..."
# pip install pyinstaller pywebview pyobjc pillow python-docx deep-translator --upgrade

# 4. Build with PyInstaller
# Note: We use 'GongbiTranslator' (no spaces) internally to avoid macOS codesign path issues.
echo "🛠️ Bundling application into .app package..."
pyinstaller --noconfirm --windowed --icon="assets/icon.icns" \
    --name "GongbiTranslator" \
    --add-data "core_engine.py:." \
    --add-data "assets/icon.png:." \
    --collect-all pywebview \
    --collect-all docx \
    app_gui.py

# 5. Rename to final product name
echo "📦 Finalizing app name..."
mv "dist/GongbiTranslator.app" "dist/Gongbi Translator.app"

# 6. Create DMG
echo "📀 Packaging into DMG..."
mkdir -p dist/dmg
cp -r "dist/Gongbi Translator.app" dist/dmg/
hdiutil create -volname "Gongbi Translator" -srcfolder dist/dmg -ov -format UDZO "dist/Gongbi_Translator_v1.0.dmg"

echo ""
echo "✨ BUILD COMPLETE! ✨"
echo "✅ DMG: $(pwd)/dist/Gongbi_Translator_v1.0.dmg"
echo "✅ App: $(pwd)/dist/Gongbi Translator.app"
echo ""
echo "Next step: Upload dist/Gongbi_Translator_v1.0.dmg to GitHub Releases."
