#!/bin/bash
# gRPC Tool Launcher Script

echo "🔧 Starting gRPC Tool..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the AppImage
APPIMAGE_PATH="$SCRIPT_DIR/src-tauri/target/debug/bundle/appimage/gRPC Tool_0.1.0_amd64.AppImage"

# Check if AppImage exists
if [ ! -f "$APPIMAGE_PATH" ]; then
    echo "❌ Error: gRPC Tool AppImage not found at: $APPIMAGE_PATH"
    echo "Please run 'cargo tauri build --debug' first to create the AppImage."
    exit 1
fi

# Make sure it's executable
chmod +x "$APPIMAGE_PATH"

# Launch the application
echo "🚀 Launching gRPC Tool..."
"$APPIMAGE_PATH" &

echo "✅ gRPC Tool started successfully!"
echo "   - Professional gRPC client with server reflection"
echo "   - Connect to any gRPC server (host:port)"
echo "   - Discover services automatically"
echo "   - Inspect method signatures"
echo ""
echo "💡 Tip: You can also find 'gRPC Tool' in your Applications menu"
