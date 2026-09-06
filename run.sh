#!/bin/bash
# ──────────────────────────────────────────────────────────────
# Tax Form Assistant — launch script
# ──────────────────────────────────────────────────────────────
cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Setting up environment (first run)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    echo "Done! Launching..."
else
    source venv/bin/activate
fi

#python3 src/tax_form_agent/gui.py
PYTHONPATH=src python src/tax_form_agent/gui.py
