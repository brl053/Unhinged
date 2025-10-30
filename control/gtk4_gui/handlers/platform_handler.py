"""
Platform Handler for Unhinged Desktop GUI

This module handles all platform control operations including start/stop
and command execution.
"""

import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class PlatformHandler:
    """Handles platform control operations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.running = False
        self.process = None
        
        # Callbacks for UI updates
        self._status_callback: Optional[Callable[[str, Optional[float]], None]] = None
        self._log_callback: Optional[Callable[[str], None]] = None
        self._error_callback: Optional[Callable[[str, str], None]] = None
        
    def set_callbacks(self,
                     status_callback: Optional[Callable[[str, Optional[float]], None]] = None,
                     log_callback: Optional[Callable[[str], None]] = None,
                     error_callback: Optional[Callable[[str, str], None]] = None):
        """Set callbacks for UI updates"""
        self._status_callback = status_callback
        self._log_callback = log_callback
        self._error_callback = error_callback
        
    def start_platform(self):
        """Start the platform backend"""
        if self.running:
            return
            
        self.running = True
        
        try:
            self._update_status("Starting platform...", 0.1)
            self._log("Starting Unhinged platform...")
            
            # Execute platform start command
            cmd = [str(self.project_root / "unhinged"), "start"]
            
            self._update_status("Launching backend services...", 0.3)
            self._log(f"Executing: {' '.join(cmd)}")
            
            self.process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self._update_status("Platform starting...", 0.5)
            
            # Monitor process output
            self._monitor_process()
            
        except Exception as e:
            self.running = False
            self._error("Platform Start Failed", str(e))
            logger.error(f"Failed to start platform: {e}")
            
    def stop_platform(self):
        """Stop the platform backend"""
        if not self.running:
            return
            
        self.running = False
        
        try:
            self._update_status("Stopping platform...", 0.1)
            self._log("Stopping Unhinged platform...")
            
            if self.process:
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self._log("Force killing platform process...")
                    self.process.kill()
                    self.process.wait()
                    
                self.process = None
                
            self._update_status("Platform stopped", 1.0)
            self._log("Platform stopped successfully")
            
        except Exception as e:
            self._error("Platform Stop Failed", str(e))
            logger.error(f"Failed to stop platform: {e}")
            
    def run_command(self, command: str):
        """Run a platform command"""
        try:
            self._log(f"Running command: {command}")
            
            if command == "generate":
                subprocess.run([str(self.project_root / "unhinged"), "build", "generate"],
                             cwd=self.project_root, check=True)
            elif command == "clean":
                subprocess.run([str(self.project_root / "unhinged"), "build", "clean"],
                             cwd=self.project_root, check=True)
            elif command == "test":
                subprocess.run([str(self.project_root / "unhinged"), "test"],
                             cwd=self.project_root, check=True)
            else:
                subprocess.run([str(self.project_root / "unhinged"), command],
                             cwd=self.project_root, check=True)
                             
            self._log(f"Command '{command}' completed successfully")
            
        except subprocess.CalledProcessError as e:
            self._error(f"Command Failed: {command}", f"Exit code: {e.returncode}")
            logger.error(f"Command '{command}' failed with exit code {e.returncode}")
        except Exception as e:
            self._error(f"Command Error: {command}", str(e))
            logger.error(f"Error running command '{command}': {e}")
            
    def _monitor_process(self):
        """Monitor the platform process output"""
        if not self.process:
            return
            
        def monitor():
            try:
                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self._log(line.rstrip())
                        
                    # Check if process has ended
                    if self.process.poll() is not None:
                        break
                        
                # Process has ended
                return_code = self.process.poll()
                if return_code == 0:
                    self._update_status("Platform running", 1.0)
                    self._log("Platform started successfully")
                else:
                    self.running = False
                    self._error("Platform Start Failed", f"Process exited with code {return_code}")
                    
            except Exception as e:
                self.running = False
                self._error("Platform Monitor Error", str(e))
                logger.error(f"Error monitoring platform process: {e}")
                
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
    def _update_status(self, message: str, progress: Optional[float] = None):
        """Update status via callback"""
        if self._status_callback:
            self._status_callback(message, progress)
            
    def _log(self, message: str):
        """Log message via callback"""
        if self._log_callback:
            self._log_callback(message)
            
    def _error(self, title: str, message: str):
        """Report error via callback"""
        if self._error_callback:
            self._error_callback(title, message)
            
    def cleanup(self):
        """Clean up resources"""
        if self.running:
            self.stop_platform()
            
    @property
    def is_running(self) -> bool:
        """Check if platform is running"""
        return self.running
