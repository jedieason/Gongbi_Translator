<div align="center">
  <img src="assets/icon.png" alt="Gongbi Translator" width="120" />
  <h1>Gongbi Translator</h1>
  <p>A clean, fast macOS app for translating Chinese Word documents to English.</p>

  <p>
    <img src="https://img.shields.io/badge/platform-macOS-lightgrey?logo=apple" />
    <img src="https://img.shields.io/badge/version-1.0-blue" />
    <img src="https://img.shields.io/badge/license-MIT-green" />
    <img src="https://img.shields.io/badge/engine-Google%20Translate-4285F4?logo=google" />
  </p>

  <a href="https://github.com/jedieason/Gongbi_Translator/releases/latest">
    <img src="https://img.shields.io/badge/⬇%20Download%20for%20macOS-v1.0-1A73E8?style=for-the-badge" alt="Download" />
  </a>
</div>

---

## Overview

**Gongbi Translator** translates `.docx` files from Chinese to English in seconds — preserving your document's original formatting, tables, fonts, and layout. No configuration required.

- 📄 Drag-and-drop `.docx` support
- ✅ Preserves paragraph structure, fonts, and tables
- 🌐 Powered by Google Translate
- 🖥️ Native macOS app — no Python installation needed
- 💾 Choose your own output location on every translation

---

## Download & Install

### Requirements
- macOS 12 Monterey or later
- Apple Silicon (M1/M2/M3) or Intel Mac

### Steps

1. **Download** the latest `.dmg` file from the [Releases page](https://github.com/jedieason/Gongbi_Translator/releases/latest).

2. **Open** the downloaded `.dmg` file by double-clicking it.

3. **Drag** `Gongbi Translator.app` into your **Applications** folder.

4. **First launch**: macOS may show a security warning since the app is not from the App Store.  
   To allow it:
   - Go to **System Settings → Privacy & Security**
   - Scroll down to the security section and click **"Open Anyway"**
   - Alternatively, right-click the app and select **Open**

5. **Done!** Gongbi Translator is ready to use.

---

## How to Use

1. Open **Gongbi Translator** from your Applications folder or Dock.
2. Click **"Choose a Word document"** and select your `.docx` file.
3. Click **"Translate Document"**.
4. A save dialog will appear — choose where to save the translated file.
5. The app will translate the document and confirm when complete.

---

## Build from Source

If you'd like to build the app yourself:

### 1. Prerequisites

- Python 3.11 or later
- macOS 12+

### 2. Clone the repository

```bash
git clone https://github.com/jedieason/Gongbi_Translator.git
cd Gongbi_Translator
```

### 3. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pywebview pyobjc pillow python-docx deep-translator pyinstaller
```

### 4. Build the app

```bash
./scripts/build_mac_app.sh
```

The finished app will be at `dist/Gongbi Translator.app` and the distributable installer at `dist/Gongbi_Translator_v1.0.dmg`.

---

## Project Structure

```
gongbi-translator/
├── app_gui.py          # App entry point and UI (pywebview + Material Design)
├── core_engine.py      # Translation engine (Google Translate, DOCX processing)
├── translate.py        # Legacy CLI translation script
├── assets/
│   ├── icon.png        # App icon (source)
│   └── icon.icns       # macOS icon bundle
└── scripts/
    └── build_mac_app.sh  # PyInstaller build script
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  <sub>Made by <a href="https://github.com/jedieason">Jedieason</a> &nbsp;·&nbsp; Powered by Google Translate</sub>
</div>
