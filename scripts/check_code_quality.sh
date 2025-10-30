#!/bin/bash

# Find project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$PROJECT_ROOT"

# Use venv-production (the working environment)
PYTHON_CMD="./venv-production/bin/python"

if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ venv-production not found"
    echo "   Run: make setup-python"
    exit 1
fi

echo "🔍 Running static analysis on all Python modules..."
$PYTHON_CMD build/static_analysis_manager.py control/gtk4_gui libs/python services
