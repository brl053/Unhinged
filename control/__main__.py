#!/usr/bin/env python3
"""
Unhinged Control Plane Server

A lightweight HTTP server that serves the control plane interface
for managing Unhinged platform services.

Usage:
    python3 -m control [--port PORT] [--host HOST]
"""

import argparse
import http.server
import socketserver
import os
import sys
import webbrowser
import threading
import time
from pathlib import Path

class ControlPlaneHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler for the control plane."""
    
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = str(Path(__file__).parent.parent)
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        # Handle root redirect
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/control/static_html/table-of-contents.html')
            self.end_headers()
            return
        
        # Handle /static_html redirect for convenience
        if self.path.startswith('/static_html/'):
            self.send_response(302)
            self.send_header('Location', f'/control{self.path}')
            self.end_headers()
            return
        
        super().do_GET()
    
    def log_message(self, format, *args):
        # Custom logging format
        print(f"🌐 {self.address_string()} - {format % args}")

def start_server(host='localhost', port=9000):
    """Start the control plane HTTP server."""
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"🚀 Starting Unhinged Control Plane on {host}:{port}")
    print(f"📁 Serving from: {project_root}")
    
    try:
        with socketserver.TCPServer((host, port), ControlPlaneHandler) as httpd:
            print(f"✅ Control Plane running at http://{host}:{port}")
            print(f"📚 Table of Contents: http://{host}:{port}/control/static_html/table-of-contents.html")
            print(f"🎛️  Service Orchestration: http://{host}:{port}/control/static_html/index.html")
            print(f"📝 Blog Editor: http://{host}:{port}/control/static_html/blog-editor.html")
            print(f"🔍 Persistence Platform: http://{host}:{port}/control/static_html/persistence-platform.html")
            print("")
            print("⏹️  Press Ctrl+C to stop the server")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Control Plane stopped by user")
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use. Try a different port or stop the existing server.")
            sys.exit(1)
        else:
            raise

def open_browser(url, delay=2):
    """Open browser after a delay."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        print(f"🌐 Opened browser: {url}")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")

def main():
    """Main entry point for the control plane server."""
    parser = argparse.ArgumentParser(description='Unhinged Control Plane Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=9000, help='Port to bind to (default: 9000)')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    
    args = parser.parse_args()
    
    # Start browser in background thread if requested
    if not args.no_browser:
        url = f"http://{args.host}:{args.port}/control/static_html/table-of-contents.html"
        browser_thread = threading.Thread(target=open_browser, args=(url,))
        browser_thread.daemon = True
        browser_thread.start()
    
    # Start the server
    start_server(args.host, args.port)

if __name__ == '__main__':
    main()
