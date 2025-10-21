#!/usr/bin/env python3
"""
@llm-type html-native-gui
@llm-legend Native GUI with HTML rendering via subprocess bridge
@llm-key HTML rendering in native window with system integration bridge
@llm-map Native window with HTML content and full system access capabilities
@llm-axiom HTML GUI must provide complete system integration while maintaining native performance
@llm-contract Provides HTML rendering with JavaScript bridge for system calls and gRPC access
@llm-token html-native-gui: Native window with HTML rendering and system integration

Unhinged HTML Native GUI - Game Developer Approach
Native X11 window + HTML rendering + System integration bridge
Fastest path to get HTML working with full system access
"""

import os
import sys
import json
import subprocess
import threading
import time

import http.server
import socketserver
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import logging
from datetime import datetime

# Cultural enforcement
try:
    from control.cultural_enforcement import CulturalEnforcer, IndependenceError
    CULTURAL_ENFORCEMENT_AVAILABLE = True
except ImportError:
    CULTURAL_ENFORCEMENT_AVAILABLE = False

class UnhingedHTMLNative:
    """
    @llm-type html-system-bridge
    @llm-legend HTML native application with system integration bridge
    @llm-key Native HTML rendering with JavaScript to Python system bridge
    @llm-map HTML application with full system access via Python bridge
    @llm-axiom HTML app must have complete system integration while remaining responsive
    @llm-contract Provides HTML UI with JavaScript bridge for system calls and file access
    @llm-token html-system-bridge: HTML application with native system integration
    
    Game dev approach: HTML UI + Python system bridge = Best of both worlds
    """
    
    def __init__(self, html_file=None, width=1200, height=800):
        self.html_file = html_file or "control/static_html/index.html"
        self.width = width
        self.height = height
        self.project_root = Path(__file__).parent.parent.parent
        self.bridge_port = self.find_available_port(9999)
        self.browser_process = None
        self.bridge_server = None
        self.bridge_thread = None
        self.start_time = time.time()
        self.request_count = 0

        # Setup logging for performance monitoring
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Cultural enforcement
        if CULTURAL_ENFORCEMENT_AVAILABLE:
            self.cultural_enforcer = CulturalEnforcer()
            try:
                self.cultural_enforcer.enforce_culture()
                print("🔒 CULTURAL COMPLIANCE: Independence validated")
            except IndependenceError as e:
                print(f"🚫 CULTURAL VIOLATION: {e}")
                raise

        print(f"🎮 Unhinged HTML Native GUI initializing...")
        print(f"📄 HTML file: {self.html_file}")
        print(f"📐 Window size: {width}x{height}")
        print(f"🌉 Bridge port: {self.bridge_port}")

    def find_available_port(self, start_port):
        """Find an available port starting from start_port"""
        import socket
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        return start_port  # Fallback
    
    def create_system_bridge(self):
        """Create JavaScript ↔ Python system bridge"""
        
        class SystemBridgeHandler(http.server.BaseHTTPRequestHandler):
            def __init__(self, gui_instance, *args, **kwargs):
                self.gui = gui_instance
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                """Handle GET requests for system operations"""
                start_time = time.time()
                self.gui.request_count += 1
                try:
                    parsed = urlparse(self.path)
                    params = parse_qs(parsed.query)
                    
                    if parsed.path == '/api/readfile':
                        file_path = params.get('path', [''])[0]
                        result = self.gui.read_file(file_path)
                    elif parsed.path == '/api/listdir':
                        dir_path = params.get('path', [''])[0]
                        result = self.gui.list_directory(dir_path)
                    elif parsed.path == '/api/runscript':
                        command = params.get('cmd', [''])[0]
                        result = self.gui.run_script(command)
                    elif parsed.path == '/api/grpc':
                        service = params.get('service', [''])[0]
                        method = params.get('method', [''])[0]
                        data = params.get('data', ['{}'])[0]
                        result = self.gui.grpc_call(service, method, data)
                    elif parsed.path == '/api/systeminfo':
                        result = self.gui.get_system_info()
                    elif parsed.path == '/api/projectinfo':
                        result = self.gui.get_project_info()
                    elif parsed.path == '/api/performance':
                        result = self.gui.get_performance_stats()
                    else:
                        result = {"error": "Unknown endpoint"}
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())

                    # Log performance
                    duration = time.time() - start_time
                    self.gui.logger.info(f"GET {parsed.path} - {duration:.3f}s")

                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            
            def do_POST(self):
                """Handle POST requests for system operations"""
                try:
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode())
                    
                    if self.path == '/api/runscript':
                        result = self.gui.run_script(data.get('command', ''))
                    elif self.path == '/api/grpc':
                        result = self.gui.grpc_call(
                            data.get('service', ''),
                            data.get('method', ''),
                            data.get('data', {})
                        )
                    elif self.path == '/api/writefile':
                        result = self.gui.write_file(
                            data.get('path', ''),
                            data.get('content', '')
                        )
                    else:
                        result = {"error": "Unknown endpoint"}
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode())
            
            def log_message(self, format, *args):
                """Suppress HTTP server logs"""
                pass
        
        # Create handler with GUI instance
        handler = lambda *args, **kwargs: SystemBridgeHandler(self, *args, **kwargs)
        
        # Start bridge server
        self.bridge_server = socketserver.TCPServer(("localhost", self.bridge_port), handler)
        self.bridge_thread = threading.Thread(target=self.bridge_server.serve_forever, daemon=True)
        self.bridge_thread.start()
        
        print(f"🌉 System bridge running on http://localhost:{self.bridge_port}")
    
    def read_file(self, file_path):
        """Read file from filesystem"""
        try:
            if not file_path or '..' in file_path:
                return {"error": "Invalid file path"}
            
            full_path = self.project_root / file_path
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {"success": True, "content": content, "path": file_path}
            
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def list_directory(self, dir_path):
        """List directory contents"""
        try:
            if not dir_path:
                dir_path = "."
            
            if '..' in dir_path:
                return {"error": "Invalid directory path"}
            
            full_path = self.project_root / dir_path
            if not full_path.exists() or not full_path.is_dir():
                return {"error": f"Directory not found: {dir_path}"}
            
            items = []
            for item in full_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            return {"success": True, "items": items, "path": dir_path}
            
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}
    
    def run_script(self, command):
        """Execute system command"""
        try:
            if not command:
                return {"error": "No command provided"}
            
            # Security: Only allow specific commands
            allowed_commands = ['make', 'ls', 'pwd', 'echo', 'cat', 'grep', 'find']
            cmd_parts = command.split()
            if not cmd_parts or cmd_parts[0] not in allowed_commands:
                return {"error": f"Command not allowed: {cmd_parts[0] if cmd_parts else 'empty'}"}
            
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10,
                cwd=self.project_root
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Failed to execute command: {str(e)}"}
    
    def grpc_call(self, service, method, data):
        """Make gRPC call to service"""
        try:
            # TODO: Implement actual gRPC calls
            # For now, return mock response
            return {
                "success": True,
                "service": service,
                "method": method,
                "response": f"Mock response from {service}.{method}",
                "data": data
            }

        except Exception as e:
            return {"error": f"gRPC call failed: {str(e)}"}

    def get_system_info(self):
        """Get system information"""
        try:
            import platform
            import psutil

            return {
                "success": True,
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "hostname": platform.node(),
                    "processor": platform.processor(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "memory_available": psutil.virtual_memory().available,
                    "disk_usage": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            return {"error": f"Failed to get system info: {str(e)}"}

    def get_project_info(self):
        """Get project information"""
        try:
            return {
                "success": True,
                "project": {
                    "root": str(self.project_root),
                    "name": "Unhinged Platform",
                    "version": "1.0.0",
                    "gui_mode": "HTML Native Bridge",
                    "bridge_port": self.bridge_port,
                    "html_file": self.html_file
                }
            }
        except Exception as e:
            return {"error": f"Failed to get project info: {str(e)}"}

    def write_file(self, path, content):
        """Write content to file"""
        try:
            file_path = Path(path)
            if not file_path.is_absolute():
                file_path = self.project_root / file_path

            # Security check - only allow writing within project
            if not str(file_path).startswith(str(self.project_root)):
                return {"error": "Access denied - path outside project"}

            file_path.write_text(content)
            return {
                "success": True,
                "path": str(file_path),
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    def get_performance_stats(self):
        """Get performance statistics"""
        try:
            uptime = time.time() - self.start_time
            return {
                "success": True,
                "stats": {
                    "uptime_seconds": round(uptime, 2),
                    "uptime_formatted": f"{int(uptime//60)}m {int(uptime%60)}s",
                    "total_requests": self.request_count,
                    "requests_per_minute": round(self.request_count / (uptime / 60), 2) if uptime > 0 else 0,
                    "bridge_port": self.bridge_port,
                    "html_file": self.html_file
                }
            }
        except Exception as e:
            return {"error": f"Failed to get performance stats: {str(e)}"}

    def get_bridge_javascript(self):
        """Get JavaScript bridge code for injection"""
        return f"""
// Unhinged System Bridge - JavaScript ↔ Python
window.unhinged = {{
    bridgeUrl: 'http://localhost:{self.bridge_port}',

    async readFile(path) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/readfile?path=${{encodeURIComponent(path)}}`);
        return await response.json();
    }},

    async listDirectory(path = '.') {{
        const response = await fetch(`${{this.bridgeUrl}}/api/listdir?path=${{encodeURIComponent(path)}}`);
        return await response.json();
    }},

    async runScript(command) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/runscript`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ command }})
        }});
        return await response.json();
    }},

    async grpcCall(service, method, data = {{}}) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/grpc`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ service, method, data }})
        }});
        return await response.json();
    }},

    async writeFile(path, content) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/writefile`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ path, content }})
        }});
        return await response.json();
    }},

    async getSystemInfo() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/systeminfo`);
        return await response.json();
    }},

    async getProjectInfo() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/projectinfo`);
        return await response.json();
    }},

    async getPerformanceStats() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/performance`);
        return await response.json();
    }}
}};

// Test bridge on load
console.log('🌉 Unhinged System Bridge loaded');
try {{
    // Test basic functionality
    const pwdResult = await window.unhinged.runScript('pwd');
    console.log('🎯 Bridge test (pwd):', pwdResult);

    // Test system info
    const sysInfo = await window.unhinged.getSystemInfo();
    console.log('💻 System info:', sysInfo);

    // Test project info
    const projInfo = await window.unhinged.getProjectInfo();
    console.log('📁 Project info:', projInfo);

    console.log('✅ All bridge functions loaded successfully');
}} catch (e) {{
    console.error('❌ Bridge test failed:', e);
}}
"""

    def inject_bridge_script(self, html_content):
        """Inject JavaScript bridge into HTML"""
        
        bridge_script = f"""
<script>
// Unhinged System Bridge - JavaScript ↔ Python
window.unhinged = {{
    bridgeUrl: 'http://localhost:{self.bridge_port}',
    
    async readFile(path) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/readfile?path=${{encodeURIComponent(path)}}`);
        return await response.json();
    }},
    
    async listDirectory(path = '.') {{
        const response = await fetch(`${{this.bridgeUrl}}/api/listdir?path=${{encodeURIComponent(path)}}`);
        return await response.json();
    }},
    
    async runScript(command) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/runscript`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ command }})
        }});
        return await response.json();
    }},
    
    async grpcCall(service, method, data = {{}}) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/grpc`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ service, method, data }})
        }});
        return await response.json();
    }},

    async writeFile(path, content) {{
        const response = await fetch(`${{this.bridgeUrl}}/api/writefile`, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ path, content }})
        }});
        return await response.json();
    }},

    async getSystemInfo() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/systeminfo`);
        return await response.json();
    }},

    async getProjectInfo() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/projectinfo`);
        return await response.json();
    }},

    async getPerformanceStats() {{
        const response = await fetch(`${{this.bridgeUrl}}/api/performance`);
        return await response.json();
    }}
}};

// Test bridge on load
window.addEventListener('load', async () => {{
    console.log('🌉 Unhinged System Bridge loaded');
    try {{
        // Test basic functionality
        const pwdResult = await window.unhinged.runScript('pwd');
        console.log('🎯 Bridge test (pwd):', pwdResult);

        // Test system info
        const sysInfo = await window.unhinged.getSystemInfo();
        console.log('💻 System info:', sysInfo);

        // Test project info
        const projInfo = await window.unhinged.getProjectInfo();
        console.log('📁 Project info:', projInfo);

        console.log('✅ All bridge functions loaded successfully');
    }} catch (e) {{
        console.error('❌ Bridge test failed:', e);
    }}
}});
</script>
"""
        
        # Inject before closing head tag
        if '</head>' in html_content:
            return html_content.replace('</head>', f'{bridge_script}</head>')
        else:
            return f'{bridge_script}\n{html_content}'
    
    def launch_native_renderer(self):
        """Launch native HTML renderer with WebKit"""
        try:
            # Get HTML file path
            html_path = self.project_root / self.html_file
            if not html_path.exists():
                print(f"❌ HTML file not found: {html_path}")
                return False

            # Load HTML directly from original location to preserve relative paths
            file_url = f"file://{html_path.absolute()}"
            
            # Try native HTML rendering with WebKit
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                gi.require_version('WebKit2', '4.1')
                from gi.repository import Gtk, WebKit2, GLib

                # Create native WebKit window
                window = Gtk.Window()
                window.set_title("Unhinged Native HTML GUI")
                window.set_default_size(self.width, self.height)

                webview = WebKit2.WebView()

                # Inject bridge script after page loads
                def on_load_finished(webview, load_event):
                    if load_event == WebKit2.LoadEvent.FINISHED:
                        bridge_js = self.get_bridge_javascript()
                        webview.run_javascript(bridge_js)
                        print("✅ Bridge script injected")

                webview.connect("load-changed", on_load_finished)
                webview.load_uri(file_url)

                window.add(webview)
                window.show_all()

                # Connect close event
                window.connect("destroy", Gtk.main_quit)

                print(f"✅ Launched native WebKit HTML renderer")
                self.native_window = window
                return True

            except ImportError:
                print("❌ WebKit not available - install python3-gi and gir1.2-webkit2-4.1")
                print("   Run: sudo apt install python3-gi gir1.2-webkit2-4.1")
                return False
            
        except Exception as e:
            print(f"❌ Failed to launch browser: {e}")
            return False
    
    def run(self):
        """Run HTML native application"""
        print("🚀 Starting HTML Native GUI...")
        
        # Start system bridge
        self.create_system_bridge()
        
        # Launch native HTML renderer
        if not self.launch_native_renderer():
            return False

        print("✅ HTML Native GUI running!")
        print("🌉 System bridge active - HTML has full system access")
        print("💡 Close window to exit")

        try:
            # Start GTK main loop for native renderer
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            Gtk.main()
        except (ImportError, KeyboardInterrupt):
            print("\n🛑 Exiting...")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        self.cleanup()
        return True
    
    def cleanup(self):
        """Clean up resources"""
        if self.bridge_server:
            self.bridge_server.shutdown()
        
        if hasattr(self, 'native_window'):
            try:
                import gi
                gi.require_version('Gtk', '3.0')
                from gi.repository import Gtk
                Gtk.main_quit()
            except ImportError:
                pass
        
        print("✅ HTML Native GUI closed")


def main():
    """Entry point for HTML native GUI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unhinged HTML Native GUI")
    parser.add_argument("--html", help="HTML file to load")
    parser.add_argument("--width", type=int, default=1200, help="Window width")
    parser.add_argument("--height", type=int, default=800, help="Window height")
    
    args = parser.parse_args()
    
    app = UnhingedHTMLNative(args.html, args.width, args.height)
    app.run()


if __name__ == "__main__":
    main()
