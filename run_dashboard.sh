#!/bin/bash
# Sets up a virtual environment the first time, then opens the dashboard.
# Works on macOS and Linux:  bash run_dashboard.sh
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi
.venv/bin/streamlit run dashboard.py
