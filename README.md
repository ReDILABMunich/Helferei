# Tax Form Assistant (Bruno)

Interactive desktop assistant for filling out the German tax registration form
*Fragebogen zur steuerlichen Erfassung für Einzelunternehmen*.

Bruno walks the user through all 23 sections of the form, explains each field
in plain English or German, and answers follow-up questions about tax concepts.

## Requirements

- **Python 3.10+** (3.12 recommended)
- **OpenAI API key** — uses `gpt-4o-mini`; a full session typically costs a few cents
- macOS or Windows

## Quick Start (development)

### macOS / Linux

```bash
./run.sh
```

The script creates a virtual environment, installs dependencies and launches
the GUI. On first run, paste your OpenAI API key into the dialog — it is stored
locally in `config.json` (gitignored) and never sent anywhere except OpenAI.

### Windows

```cmd
run.bat
```

The script creates a virtual environment, installs dependencies and launches
the GUI. On first run, paste your OpenAI API key into the dialog — it is stored
locally in `%APPDATA%\Bruno\config.json` (gitignored) and never sent anywhere
except OpenAI.

If you prefer to run the steps manually:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\tax_form_agent\gui.py
```

## Building Release Binaries

Both builds use **PyInstaller**. Specs live at the repo root.

### macOS — `Bruno.app`

```bash
source venv/bin/activate
pip install pyinstaller
pyinstaller tax_form_app.spec --clean --noconfirm
```

Output: `dist/Bruno.app`.

### Windows — `Bruno.exe`

Must be built on a Windows machine (PyInstaller is platform-specific).

```cmd
venv\Scripts\activate
pip install pyinstaller
pyinstaller tax_form_app_win.spec --clean --noconfirm
```

Output: `dist\Bruno.exe` (single-file build — bootstraps into a temp folder on
first launch). Version metadata embedded via [version_win.txt](version_win.txt).

Alternatively, trigger the **GitHub Actions workflow**
(`.github/workflows/build-windows.yml`) — it builds the `.exe` on a hosted
Windows runner and uploads `Bruno.exe` as a downloadable artifact. Trigger
manually via the *Actions* tab on GitHub.

## Project Structure

```
├── README.md
├── run.sh                         # macOS/Linux launcher
├── run.bat                        # Windows launcher
├── setup.py                       # Python package metadata (CLI entry point)
├── requirements.txt               # PySide6, certifi
├── config.example.json            # Config template — copy to config.json
├── tax_form_app.spec              # PyInstaller spec — macOS
├── tax_form_app_win.spec          # PyInstaller spec — Windows
├── version_win.txt                # VersionInfo embedded into Bruno.exe
├── icon.icns / icon.ico / icon.png
├── icon.iconset/                  # Source PNGs for icon.icns
├── data/
│   └── COMPLETE_FORM_STRUCTURE.json   # Full form (23 sections)
├── fonts/                         # DM Sans — bundled into the app
├── src/tax_form_agent/
│   ├── __init__.py
│   ├── gui.py                     # Desktop GUI (PySide6)
│   ├── agent.py                   # Conversation agent (core)
│   ├── form_knowledge.py          # Form structure parser & search
│   ├── llm_client.py              # OpenAI API client (raw HTTP)
│   ├── tools.py                   # German tax-term glossary
│   └── cli.py                     # Terminal interface (alternative)
└── dist/                          # Build outputs (gitignored)
    ├── Bruno.app
    └── Bruno.exe
```

## Configuration

`config.json` (gitignored, created on first launch):

```json
{
  "openai_api_key": "sk-...",
  "model": "gpt-4o-mini",
  "language": "en"
}
```

`language` can be `"en"` or `"de"` — also toggleable from the GUI top-right.
