#!/bin/bash

echo "🔍 Running static analysis on Python code..."

# Install ruff if not available
if ! command -v ruff &> /dev/null; then
    echo "📦 Installing ruff..."
    pip install ruff
fi

echo ""
echo "🔍 Checking control/gtk4_gui for import errors and style issues..."
ruff check control/gtk4_gui/ --select=F,E,I

echo ""
echo "🔍 Checking libs/python for import errors and style issues..."
ruff check libs/python/ --select=F,E,I

echo ""
echo "🔍 Checking services for import errors and style issues..."
ruff check services/ --select=F,E,I

echo ""
echo "✅ Static analysis complete!"
echo ""
echo "💡 To fix auto-fixable issues, run:"
echo "   ruff check --fix control/gtk4_gui/"
echo "   ruff check --fix libs/python/"
echo "   ruff check --fix services/"
