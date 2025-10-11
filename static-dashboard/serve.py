#!/usr/bin/env python3
"""
Simple HTTP server for Unhinged Health Dashboard
Serves the static HTML dashboard with CORS headers for API access
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for cross-origin API requests"""
    
    def end_headers(self):
        # Add CORS headers to allow API requests from the dashboard
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom log format
        print(f"🌐 Dashboard: {format % args}")

def main():
    # Change to the dashboard directory
    dashboard_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dashboard_dir)
    
    # Default port
    port = 8888
    
    # Check if port is provided as argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Check if port is available
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print("🧠 Unhinged Health Dashboard Server")
            print("=" * 50)
            print(f"📊 Dashboard URL: http://localhost:{port}")
            print(f"📁 Serving from: {dashboard_dir}")
            print(f"🔄 Auto-refresh: Enabled (30s)")
            print("=" * 50)
            print("📋 Available Services:")
            print("   🚀 Backend:      http://localhost:8080")
            print("   👁️  Vision AI:    http://localhost:8001")
            print("   🎤 Whisper TTS:  http://localhost:8000")
            print("   🧠 Context LLM:  http://localhost:8002")
            print("   📊 Grafana:      http://localhost:3001")
            print("   📈 Prometheus:   http://localhost:9090")
            print("   📝 Loki:         http://localhost:3100")
            print("=" * 50)
            print("💡 Tips:")
            print("   • Dashboard auto-refreshes every 30 seconds")
            print("   • Click service cards for detailed health checks")
            print("   • Use Quick Actions for common operations")
            print("   • Check browser console for any CORS issues")
            print("=" * 50)
            print(f"🎯 Press Ctrl+C to stop the server")
            print()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down dashboard server...")
                httpd.shutdown()
                
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Port {port} is already in use!")
            print(f"💡 Try a different port: python3 serve.py {port + 1}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
