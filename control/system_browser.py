#!/usr/bin/env python3
"""
@llm-type system-browser
@llm-legend Native system browser for Unhinged control interfaces using file protocol
@llm-key System browser enabling native GUI access to HTML interfaces without web server
@llm-map Native browser application providing file protocol access to control interfaces
@llm-axiom System browser must support file protocol and provide native OS integration
@llm-contract Provides native window with HTML rendering for local file-based interfaces
@llm-token system-browser: Native GUI browser for file protocol HTML interfaces

Unhinged System Browser - Game Developer Approach
Native GUI window that renders our HTML files directly from file system
No web server needed, no CORS issues, pure local file access
"""

import os
import sys
import subprocess
import webbrowser
import tempfile
import time
from pathlib import Path
from typing import Optional

class UnhingedSystemBrowser:
    """
    @llm-type native-browser
    @llm-legend Native system browser providing file protocol access to HTML interfaces
    @llm-key Native browser window with HTML rendering and file system integration
    @llm-map System browser enabling local HTML interface access without web servers
    @llm-axiom Native browser must support file protocol and provide seamless user experience
    @llm-contract Provides native window rendering HTML files with full file system access
    @llm-token native-browser: System browser for local HTML interface rendering
    
    Game developer approach to GUI: Simple, direct, gets the job done
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.static_html_dir = self.project_root / "control" / "static_html"
        self.browser_process = None
        
        print(f"🎮 Unhinged System Browser initializing...")
        print(f"📁 Project root: {self.project_root}")
        print(f"🌐 Static HTML: {self.static_html_dir}")
    
    def get_available_browsers(self) -> list:
        """Get list of available browsers on system"""
        browsers = []
        
        # Check for common browsers
        browser_commands = [
            ('firefox', 'Firefox'),
            ('google-chrome', 'Google Chrome'),
            ('chromium-browser', 'Chromium'),
            ('chromium', 'Chromium'),
            ('brave-browser', 'Brave'),
            ('opera', 'Opera'),
            ('microsoft-edge', 'Microsoft Edge')
        ]
        
        for cmd, name in browser_commands:
            try:
                result = subprocess.run(['which', cmd], capture_output=True, text=True)
                if result.returncode == 0:
                    browsers.append((cmd, name, result.stdout.strip()))
            except:
                pass
        
        return browsers
    
    def create_browser_launcher(self, page: str = "index.html") -> str:
        """Create a browser launcher script for file protocol access"""
        
        # Get full path to HTML file
        html_file = self.static_html_dir / page
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")
        
        file_url = f"file://{html_file.absolute()}"
        
        # Create launcher script
        launcher_script = f"""#!/bin/bash
# Unhinged System Browser Launcher
# Game dev approach: Just launch the damn thing

echo "🎮 Launching Unhinged System Browser..."
echo "📄 Page: {page}"
echo "🔗 URL: {file_url}"

# Try browsers in order of preference
BROWSERS=(
    "firefox --new-window"
    "google-chrome --new-window --allow-file-access-from-files"
    "chromium-browser --new-window --allow-file-access-from-files"
    "chromium --new-window --allow-file-access-from-files"
    "brave-browser --new-window --allow-file-access-from-files"
)

for browser_cmd in "${{BROWSERS[@]}}"; do
    browser_name=$(echo $browser_cmd | cut -d' ' -f1)
    if command -v $browser_name >/dev/null 2>&1; then
        echo "✅ Found browser: $browser_name"
        echo "🚀 Launching: $browser_cmd '{file_url}'"
        $browser_cmd '{file_url}' &
        echo "🎯 Browser launched! PID: $!"
        exit 0
    fi
done

echo "❌ No suitable browser found!"
echo "💡 Install one of: firefox, google-chrome, chromium-browser"
exit 1
"""
        
        # Write launcher script
        launcher_path = self.project_root / "launch_browser.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_script)
        
        # Make executable
        os.chmod(launcher_path, 0o755)
        
        return str(launcher_path)
    
    def launch_page(self, page: str = "index.html", browser: Optional[str] = None) -> bool:
        """Launch a specific page in system browser"""
        
        try:
            # Get full path to HTML file
            html_file = self.static_html_dir / page
            if not html_file.exists():
                print(f"❌ HTML file not found: {html_file}")
                return False
            
            file_url = f"file://{html_file.absolute()}"
            print(f"🚀 Launching: {file_url}")
            
            if browser:
                # Use specific browser
                subprocess.Popen([browser, file_url])
            else:
                # Use system default or create launcher
                launcher = self.create_browser_launcher(page)
                subprocess.Popen([launcher])
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    def launch_mission_control(self) -> bool:
        """Launch main mission control interface"""
        return self.launch_page("index.html")
    
    def launch_code_editor(self) -> bool:
        """Launch code editor interface"""
        return self.launch_page("code-editor.html")
    
    def launch_service_orchestration(self) -> bool:
        """Launch service orchestration interface"""
        return self.launch_page("service-orchestration.html")
    
    def launch_data_lake(self) -> bool:
        """Launch data lake interface"""
        return self.launch_page("data-lake.html")
    
    def list_available_pages(self) -> list:
        """List all available HTML pages"""
        pages = []
        for html_file in self.static_html_dir.glob("*.html"):
            pages.append(html_file.name)
        return sorted(pages)
    
    def create_desktop_shortcuts(self) -> bool:
        """Create desktop shortcuts for main interfaces"""
        try:
            desktop_dir = Path.home() / "Desktop"
            if not desktop_dir.exists():
                desktop_dir = Path.home()
            
            shortcuts = [
                ("Unhinged Mission Control", "index.html", "🎮"),
                ("Unhinged Code Editor", "code-editor.html", "💻"),
                ("Unhinged Services", "service-orchestration.html", "🔧"),
                ("Unhinged Data Lake", "data-lake.html", "🏊"),
            ]
            
            for name, page, icon in shortcuts:
                desktop_file = desktop_dir / f"{name.replace(' ', '_')}.desktop"
                
                desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={name}
Comment=Unhinged System Interface
Exec=python3 {__file__} --page {page}
Icon=applications-games
Terminal=false
Categories=Development;
"""
                
                with open(desktop_file, 'w') as f:
                    f.write(desktop_content)
                
                os.chmod(desktop_file, 0o755)
                print(f"✅ Created desktop shortcut: {desktop_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create desktop shortcuts: {e}")
            return False


def main():
    """CLI entry point for system browser"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unhinged System Browser - Game Dev GUI Approach",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch mission control
  python3 system_browser.py
  
  # Launch specific page
  python3 system_browser.py --page code-editor.html
  
  # List available pages
  python3 system_browser.py --list
  
  # Create desktop shortcuts
  python3 system_browser.py --shortcuts
        """
    )
    
    parser.add_argument("--page", default="index.html", help="HTML page to launch")
    parser.add_argument("--browser", help="Specific browser command to use")
    parser.add_argument("--list", action="store_true", help="List available pages")
    parser.add_argument("--shortcuts", action="store_true", help="Create desktop shortcuts")
    
    args = parser.parse_args()
    
    browser = UnhingedSystemBrowser()
    
    if args.list:
        print("📄 Available pages:")
        for page in browser.list_available_pages():
            print(f"   • {page}")
        return
    
    if args.shortcuts:
        print("🖥️ Creating desktop shortcuts...")
        browser.create_desktop_shortcuts()
        return
    
    print(f"🎮 Launching Unhinged System Browser...")
    success = browser.launch_page(args.page, args.browser)
    
    if success:
        print("✅ Browser launched successfully!")
    else:
        print("❌ Failed to launch browser")
        sys.exit(1)


if __name__ == "__main__":
    main()
