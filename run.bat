@echo off
REM ──────────────────────────────────────────────────────────────
REM Tax Form Assistant — Windows launch script
REM ──────────────────────────────────────────────────────────────
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo Setting up environment ^(first run^)...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create venv. Is Python 3.10+ installed and on PATH?
        exit /b 1
    )
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        exit /b 1
    )
    echo Done! Launching...
) else (
    call venv\Scripts\activate.bat
)

python src\tax_form_agent\gui.py
endlocal
