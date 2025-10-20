#!/bin/bash
# 
# Unhinged Control Plane Browser Launcher
# 
# Opens the appropriate control plane interface in the default browser
# 

set -e

# Default values
HOST="localhost"
PORT="9000"
PAGE="table-of-contents"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --toc|--table-of-contents)
            PAGE="table-of-contents"
            shift
            ;;
        --index|--home)
            PAGE="index"
            shift
            ;;
        --blog)
            PAGE="blog-editor"
            shift
            ;;
        --persistence)
            PAGE="persistence-platform"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST          Server host (default: localhost)"
            echo "  --port PORT          Server port (default: 9000)"
            echo "  --toc                Open table of contents (default)"
            echo "  --index              Open main index page"
            echo "  --blog               Open blog editor"
            echo "  --persistence        Open persistence platform"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Construct URL
BASE_URL="http://${HOST}:${PORT}/control/static_html"
URL="${BASE_URL}/${PAGE}.html"

echo "🌐 Opening Control Plane interface..."
echo "📍 URL: $URL"

# Try different browser opening methods
if command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open "$URL"
elif command -v open >/dev/null 2>&1; then
    # macOS
    open "$URL"
elif command -v start >/dev/null 2>&1; then
    # Windows
    start "$URL"
else
    echo "⚠️  Could not detect browser opener"
    echo "📋 Please manually open: $URL"
fi

echo "✅ Browser launch attempted"
