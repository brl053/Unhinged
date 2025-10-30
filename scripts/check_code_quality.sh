#!/bin/bash

# Find project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$PROJECT_ROOT"

# Find Python executable
PYTHON_CMD=""
if [ -f "venv-production/bin/python" ]; then
    PYTHON_CMD="./venv-production/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python executable not found"
    exit 1
fi

echo "🔍 Running static analysis on all Python modules..."
$PYTHON_CMD build/static_analysis_manager.py control/gtk4_gui libs/python services
