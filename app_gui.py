import os
import webview
import threading
from core_engine import process_document

class Api:
    def __init__(self, window):
        self._window = window
        self.is_processing = False

    def select_file(self):
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=('Word Documents (*.docx)', 'All files (*.*)')
        )
        if result:
            return result[0]
        return None

    def get_save_path(self, suggested_name):
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=suggested_name,
            file_types=('Word Documents (*.docx)',)
        )
        if result:
            return result
        return None

    def start_translation(self, file_path):
        if self.is_processing:
            return "ALREADY_PROCESSING"
        if not file_path:
            return "MISSING_FILE"

        # Ask user for save location before starting
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        suggested = f"{base_name} (English).docx"
        save_path = self.get_save_path(suggested)

        if not save_path:
            return "CANCELLED"

        self.is_processing = True
        thread = threading.Thread(
            target=self._run_process,
            args=(file_path, save_path)
        )
        thread.daemon = True
        thread.start()
        return "STARTED"

    def _run_process(self, file_path, save_path):
        def progress_cb(current, total):
            self._window.evaluate_js(f"updateProgress({current}, {total})")

        try:
            result_path, error = process_document(
                file_path,
                output_path=save_path,
                progress_callback=progress_cb
            )
            if error:
                safe_error = error.replace("'", "\\'").replace('"', '\\"')
                self._window.evaluate_js(f"onComplete(false, '{safe_error}')")
            else:
                safe_name = os.path.basename(result_path).replace("'", "\\'")
                self._window.evaluate_js(f"onComplete(true, '{safe_name}')")
        except Exception as e:
            safe_error = str(e).replace("'", "\\'").replace('"', '\\"')
            self._window.evaluate_js(f"onComplete(false, '{safe_error}')")
        finally:
            self.is_processing = False


html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gongbi Translator</title>
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Roboto:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1A73E8;
            --primary-dark: #1557B0;
            --primary-light: #E8F0FE;
            --surface: #FFFFFF;
            --bg: #F8F9FA;
            --on-surface: #202124;
            --on-surface-variant: #5F6368;
            --outline: #DADCE0;
            --error: #D93025;
            --success: #188038;
            --shadow-1: 0 1px 2px rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
            --shadow-2: 0 1px 3px rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-font-smoothing: antialiased;
        }

        body {
            font-family: 'Roboto', 'Google Sans', sans-serif;
            background: var(--bg);
            color: var(--on-surface);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* ── Top App Bar ── */
        .app-bar {
            background: var(--surface);
            border-bottom: 1px solid var(--outline);
            padding: 0 24px;
            height: 64px;
            display: flex;
            align-items: center;
            gap: 16px;
            flex-shrink: 0;
            -webkit-app-region: drag;
        }

        .app-bar-logo {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            overflow: hidden;
            flex-shrink: 0;
            -webkit-app-region: no-drag;
        }

        .app-bar-logo img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .app-bar-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 18px;
            font-weight: 500;
            color: var(--on-surface);
            letter-spacing: 0;
        }

        /* ── Main content ── */
        .main {
            flex: 1;
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
            overflow-y: auto;
        }

        /* ── Cards ── */
        .card {
            background: var(--surface);
            border-radius: 12px;
            padding: 24px;
            box-shadow: var(--shadow-1);
        }

        .card-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 14px;
            font-weight: 500;
            color: var(--on-surface-variant);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 16px;
        }

        /* ── File picker ── */
        .file-zone {
            border: 2px dashed var(--outline);
            border-radius: 8px;
            padding: 28px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: border-color 0.2s, background 0.2s;
            background: var(--bg);
        }

        .file-zone:hover {
            border-color: var(--primary);
            background: var(--primary-light);
        }

        .file-zone.has-file {
            border-style: solid;
            border-color: var(--primary);
            background: var(--primary-light);
        }

        .file-zone svg {
            color: var(--on-surface-variant);
            transition: color 0.2s;
        }

        .file-zone.has-file svg,
        .file-zone:hover svg {
            color: var(--primary);
        }

        .file-zone-label {
            font-size: 14px;
            font-weight: 500;
            color: var(--primary);
        }

        .file-zone-hint {
            font-size: 12px;
            color: var(--on-surface-variant);
            text-align: center;
        }

        #fileName {
            font-size: 13px;
            font-weight: 500;
            color: var(--on-surface);
            text-align: center;
            word-break: break-all;
            max-width: 100%;
        }

        /* ── Progress ── */
        .progress-container {
            display: none;
        }

        .progress-container.visible {
            display: block;
        }

        .progress-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .progress-label {
            font-size: 13px;
            color: var(--on-surface);
            font-weight: 500;
        }

        .progress-pct {
            font-size: 13px;
            color: var(--primary);
            font-weight: 500;
        }

        .progress-track {
            height: 4px;
            background: var(--primary-light);
            border-radius: 2px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            background: var(--primary);
            border-radius: 2px;
            transition: width 0.3s ease;
        }

        .status-text {
            font-size: 12px;
            color: var(--on-surface-variant);
            margin-top: 8px;
        }

        /* ── Actions ── */
        .actions {
            display: flex;
            gap: 12px;
        }

        .btn {
            flex: 1;
            padding: 0 24px;
            height: 40px;
            border-radius: 20px;
            font-family: 'Google Sans', sans-serif;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            transition: box-shadow 0.2s, background 0.2s, opacity 0.2s;
            letter-spacing: 0.25px;
        }

        .btn-primary {
            background: var(--primary);
            color: #ffffff;
        }

        .btn-primary:hover:not(:disabled) {
            background: var(--primary-dark);
            box-shadow: var(--shadow-1);
        }

        .btn-primary:disabled {
            opacity: 0.38;
            cursor: not-allowed;
        }

        /* ── Result banner ── */
        .result-banner {
            display: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 13px;
            font-weight: 500;
            gap: 10px;
            align-items: flex-start;
        }

        .result-banner.success {
            display: flex;
            background: #E6F4EA;
            color: var(--success);
        }

        .result-banner.error {
            display: flex;
            background: #FCE8E6;
            color: var(--error);
        }

        .result-banner span {
            flex: 1;
            word-break: break-all;
        }

        /* ── Footer ── */
        .footer {
            flex-shrink: 0;
            padding: 12px 24px;
            text-align: center;
            font-size: 11px;
            color: var(--on-surface-variant);
            border-top: 1px solid var(--outline);
            background: var(--surface);
        }
    </style>
</head>
<body>

    <!-- Top App Bar -->
    <div class="app-bar">
        <div class="app-bar-logo">
            <img src="data:image/png;base64,ICON_BASE64_PLACEHOLDER" alt="">
        </div>
        <span class="app-bar-title">Gongbi Translator</span>
    </div>

    <!-- Main -->
    <div class="main">

        <!-- File card -->
        <div class="card">
            <div class="card-title">Source Document</div>
            <div class="file-zone" id="fileZone" onclick="selectFile()">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <line x1="9" y1="15" x2="15" y2="15"/>
                </svg>
                <div class="file-zone-label">Choose a Word document</div>
                <div class="file-zone-hint" id="fileName">Supports .docx files</div>
            </div>
        </div>

        <!-- Progress card -->
        <div class="card">
            <div class="progress-container" id="progressContainer">
                <div class="progress-header">
                    <span class="progress-label" id="progressLabel">Translating…</span>
                    <span class="progress-pct" id="progressPct">0%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
                <div class="status-text" id="statusText">Preparing translation…</div>
            </div>

            <!-- Result banner -->
            <div class="result-banner" id="resultBanner">
                <span id="resultText"></span>
            </div>

            <!-- Actions -->
            <div class="actions" style="margin-top: 16px;">
                <button class="btn btn-primary" id="translateBtn" onclick="startTranslation()" disabled>
                    Translate Document
                </button>
            </div>
        </div>

    </div>

    <!-- Footer -->
    <div class="footer">
        Powered by Jedieason &nbsp;·&nbsp; Gongbi Translator v1.0
    </div>

    <script>
        let selectedPath = null;
        let isProcessing = false;

        async function selectFile() {
            if (isProcessing) return;
            const path = await pywebview.api.select_file();
            if (path) {
                selectedPath = path;
                const name = path.split('/').pop();
                document.getElementById('fileName').innerText = name;
                document.getElementById('fileZone').classList.add('has-file');
                document.getElementById('fileZone').querySelector('.file-zone-label').innerText = 'File selected — click to change';
                document.getElementById('translateBtn').disabled = false;
                clearResult();
            }
        }

        async function startTranslation() {
            if (isProcessing || !selectedPath) return;

            clearResult();
            const res = await pywebview.api.start_translation(selectedPath);

            if (res === 'CANCELLED') return;
            if (res === 'ALREADY_PROCESSING') return;
            if (res !== 'STARTED') {
                showResult(false, 'Unable to start translation. Please try again.');
                return;
            }

            isProcessing = true;
            document.getElementById('translateBtn').disabled = true;
            document.getElementById('translateBtn').innerText = 'Translating…';
            document.getElementById('progressContainer').classList.add('visible');
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressPct').innerText = '0%';
            document.getElementById('statusText').innerText = 'Starting…';
        }

        function updateProgress(current, total) {
            const pct = Math.round((current / total) * 100);
            document.getElementById('progressBar').style.width = pct + '%';
            document.getElementById('progressPct').innerText = pct + '%';
            document.getElementById('statusText').innerText = `Processing paragraph ${current} of ${total}`;
        }

        function onComplete(success, message) {
            isProcessing = false;
            document.getElementById('translateBtn').disabled = false;
            document.getElementById('translateBtn').innerText = 'Translate Document';
            document.getElementById('progressContainer').classList.remove('visible');

            if (success) {
                showResult(true, 'Translation complete. File saved as: ' + message);
            } else {
                showResult(false, 'Translation failed: ' + message);
            }
        }

        function showResult(success, message) {
            const banner = document.getElementById('resultBanner');
            banner.className = 'result-banner ' + (success ? 'success' : 'error');
            document.getElementById('resultText').innerText = message;
        }

        function clearResult() {
            const banner = document.getElementById('resultBanner');
            banner.className = 'result-banner';
        }
    </script>
</body>
</html>
"""

def start_app():
    # Embed the icon as base64
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
    icon_b64 = ''
    try:
        import base64
        with open(icon_path, 'rb') as f:
            icon_b64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        pass

    final_html = html_content.replace('ICON_BASE64_PLACEHOLDER', icon_b64)

    api = Api(None)
    window = webview.create_window(
        'Gongbi Translator',
        html=final_html,
        js_api=api,
        width=520,
        height=620,
        resizable=False,
        background_color='#F8F9FA'
    )
    api._window = window
    webview.start(debug=False)

if __name__ == "__main__":
    start_app()
