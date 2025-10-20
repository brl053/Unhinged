#!/usr/bin/env python3
"""
Build System File Watcher

A simple file watcher that monitors git status and rebuilds when changes are detected.
Designed for the custom /build system to auto-regenerate HTML files.

Usage:
    python3 build/watch.py [--interval SECONDS] [--verbose]
"""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path

class BuildWatcher:
    """Simple file watcher that monitors git status for changes."""
    
    def __init__(self, interval=2, verbose=False):
        self.interval = interval
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent
        self.last_git_status = None
        
    def get_git_status(self):
        """Get current git status hash for change detection."""
        try:
            # Get git status porcelain output
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return hash(result.stdout)
            else:
                return None
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def run_build(self):
        """Run the build process."""
        if self.verbose:
            print("🔨 Running build process...")
        
        try:
            # Run make generate
            result = subprocess.run(
                ['make', 'generate'],
                cwd=self.project_root,
                capture_output=not self.verbose,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Build completed successfully")
                return True
            else:
                print(f"❌ Build failed with exit code {result.returncode}")
                if not self.verbose and result.stderr:
                    print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Build timed out after 30 seconds")
            return False
        except Exception as e:
            print(f"💥 Build error: {e}")
            return False
    
    def watch(self):
        """Main watch loop."""
        print("👀 Starting build watcher...")
        print(f"📁 Watching: {self.project_root}")
        print(f"⏱️  Check interval: {self.interval}s")
        print("⏹️  Press Ctrl+C to stop")
        print("")
        
        # Initial build
        print("🚀 Running initial build...")
        self.run_build()
        self.last_git_status = self.get_git_status()
        
        try:
            while True:
                time.sleep(self.interval)
                
                current_status = self.get_git_status()
                
                if current_status is None:
                    if self.verbose:
                        print("⚠️  Could not get git status")
                    continue
                
                if current_status != self.last_git_status:
                    print(f"🔄 Changes detected at {time.strftime('%H:%M:%S')}")
                    
                    if self.run_build():
                        self.last_git_status = current_status
                    else:
                        print("🔄 Will retry on next change...")
                
                elif self.verbose:
                    print(f"✓ No changes at {time.strftime('%H:%M:%S')}")
                    
        except KeyboardInterrupt:
            print("\n🛑 Build watcher stopped by user")
        except Exception as e:
            print(f"\n💥 Watcher error: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Build System File Watcher')
    parser.add_argument('--interval', type=float, default=2.0, 
                       help='Check interval in seconds (default: 2.0)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate interval
    if args.interval < 0.1:
        print("❌ Interval must be at least 0.1 seconds")
        sys.exit(1)
    
    # Create and start watcher
    watcher = BuildWatcher(interval=args.interval, verbose=args.verbose)
    watcher.watch()

if __name__ == '__main__':
    main()
