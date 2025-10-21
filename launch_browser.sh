#!/bin/bash
# Unhinged System Browser Launcher
# Game dev approach: Just launch the damn thing

echo "🎮 Launching Unhinged System Browser..."
echo "📄 Page: index.html"
echo "🔗 URL: file:///home/e-bliss-station-1/Projects/Unhinged/control/static_html/index.html"

# Try browsers in order of preference
BROWSERS=(
    "firefox --new-window"
    "google-chrome --new-window --allow-file-access-from-files"
    "chromium-browser --new-window --allow-file-access-from-files"
    "chromium --new-window --allow-file-access-from-files"
    "brave-browser --new-window --allow-file-access-from-files"
)

for browser_cmd in "${BROWSERS[@]}"; do
    browser_name=$(echo $browser_cmd | cut -d' ' -f1)
    if command -v $browser_name >/dev/null 2>&1; then
        echo "✅ Found browser: $browser_name"
        echo "🚀 Launching: $browser_cmd 'file:///home/e-bliss-station-1/Projects/Unhinged/control/static_html/index.html'"
        $browser_cmd 'file:///home/e-bliss-station-1/Projects/Unhinged/control/static_html/index.html' &
        echo "🎯 Browser launched! PID: $!"
        exit 0
    fi
done

echo "❌ No suitable browser found!"
echo "💡 Install one of: firefox, google-chrome, chromium-browser"
exit 1
