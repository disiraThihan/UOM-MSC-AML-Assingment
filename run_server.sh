#!/usr/bin/env bash
# Quick-start script for Colombo Suburban Land Valuation System

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "=========================================================="
echo "  Colombo Suburban Land Valuation System"
echo "  Malabe - Kottawa Corridor | University of Moratuwa"
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found! Please run setup."
    exit 1
fi

source .venv/bin/activate
echo "Starting FastAPI deployment server on http://127.0.0.1:8000 ..."
python3 -m uvicorn src.app:app --host 127.0.0.1 --port 8000
