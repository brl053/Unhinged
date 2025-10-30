#!/usr/bin/env python3
"""
Checksum Manager - Deterministic update detection for Unhinged platform

Provides reusable checksum-based change detection to ensure code updates
are properly reflected in running applications. Prevents stale code issues.

Usage:
    from build.checksum_manager import ChecksumManager
    
    cm = ChecksumManager()
    if cm.has_changes("control/gtk4_gui"):
        print("🔄 Code changes detected, restart required")
        cm.update_checksums("control/gtk4_gui")
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Set


class ChecksumManager:
    """Manages checksums for deterministic change detection"""
    
    def __init__(self, build_dir: Optional[Path] = None):
        """Initialize checksum manager
        
        Args:
            build_dir: Build directory path (defaults to ./build)
        """
        if build_dir is None:
            # Auto-detect build directory relative to project root
            current = Path(__file__).parent
            if current.name == "build":
                self.build_dir = current
            else:
                self.build_dir = current / "build"
        else:
            self.build_dir = Path(build_dir)
            
        self.build_dir.mkdir(exist_ok=True)
        self.checksum_file = self.build_dir / "code_checksums.json"
        
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️ Checksum error for {file_path}: {e}")
            return ""
            
    def calculate_directory_checksums(self, directory: Path, 
                                    extensions: Set[str] = None) -> Dict[str, str]:
        """Calculate checksums for all files in directory
        
        Args:
            directory: Directory to scan
            extensions: File extensions to include (default: .py, .css, .js)
            
        Returns:
            Dict mapping relative file paths to checksums
        """
        if extensions is None:
            extensions = {'.py', '.css', '.js', '.json', '.yaml', '.yml'}
            
        checksums = {}
        directory = Path(directory)
        
        if not directory.exists():
            return checksums
            
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                # Use relative path as key for portability
                rel_path = str(file_path.relative_to(directory))
                checksums[rel_path] = self.calculate_file_checksum(file_path)
                
        return checksums
        
    def load_stored_checksums(self) -> Dict[str, Dict[str, str]]:
        """Load stored checksums from file"""
        try:
            if self.checksum_file.exists():
                with open(self.checksum_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading checksums: {e}")
            
        return {}
        
    def save_checksums(self, checksums: Dict[str, Dict[str, str]]):
        """Save checksums to file"""
        try:
            # Add metadata
            data = {
                "metadata": {
                    "updated": time.time(),
                    "updated_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "version": "1.0"
                },
                "checksums": checksums
            }
            
            with open(self.checksum_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error saving checksums: {e}")
            
    def has_changes(self, module_path: str) -> bool:
        """Check if module has changes since last checksum
        
        Args:
            module_path: Path to module directory (e.g., "control/gtk4_gui")
            
        Returns:
            True if changes detected, False if no changes
        """
        try:
            # Calculate current checksums
            current_checksums = self.calculate_directory_checksums(Path(module_path))
            
            # Load stored checksums
            stored_data = self.load_stored_checksums()
            stored_checksums = stored_data.get("checksums", {}).get(module_path, {})
            
            # Compare
            if not stored_checksums:
                print(f"📦 No stored checksums for {module_path} (first run)")
                return True
                
            # Check for new, modified, or deleted files
            current_files = set(current_checksums.keys())
            stored_files = set(stored_checksums.keys())
            
            new_files = current_files - stored_files
            deleted_files = stored_files - current_files
            common_files = current_files & stored_files
            
            modified_files = []
            for file_path in common_files:
                if current_checksums[file_path] != stored_checksums[file_path]:
                    modified_files.append(file_path)
                    
            # Report changes
            if new_files or deleted_files or modified_files:
                print(f"🔄 Changes detected in {module_path}:")
                if new_files:
                    print(f"   📄 New files: {len(new_files)}")
                if deleted_files:
                    print(f"   🗑️ Deleted files: {len(deleted_files)}")
                if modified_files:
                    print(f"   ✏️ Modified files: {len(modified_files)}")
                    for file_path in modified_files[:5]:  # Show first 5
                        print(f"      - {file_path}")
                    if len(modified_files) > 5:
                        print(f"      ... and {len(modified_files) - 5} more")
                return True
            else:
                print(f"✅ No changes in {module_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking changes for {module_path}: {e}")
            return True  # Assume changes on error
            
    def update_checksums(self, module_path: str):
        """Update stored checksums for module
        
        Args:
            module_path: Path to module directory
        """
        try:
            # Calculate current checksums
            current_checksums = self.calculate_directory_checksums(Path(module_path))
            
            # Load existing data
            stored_data = self.load_stored_checksums()
            if "checksums" not in stored_data:
                stored_data["checksums"] = {}
                
            # Update checksums for this module
            stored_data["checksums"][module_path] = current_checksums
            
            # Save updated data
            self.save_checksums(stored_data["checksums"])
            
            print(f"💾 Updated checksums for {module_path} ({len(current_checksums)} files)")
            
        except Exception as e:
            print(f"❌ Error updating checksums for {module_path}: {e}")
            
    def check_multiple_modules(self, modules: List[str]) -> Dict[str, bool]:
        """Check multiple modules for changes
        
        Args:
            modules: List of module paths to check
            
        Returns:
            Dict mapping module paths to change status
        """
        results = {}
        for module in modules:
            results[module] = self.has_changes(module)
        return results
        
    def force_update_all(self, modules: List[str]):
        """Force update checksums for all modules"""
        print("🔄 Force updating all module checksums...")
        for module in modules:
            self.update_checksums(module)
        print("✅ All checksums updated")
        
    def get_status_report(self, modules: List[str]) -> str:
        """Get formatted status report for modules"""
        results = self.check_multiple_modules(modules)
        
        report = ["📊 Checksum Status Report:"]
        for module, has_changes in results.items():
            status = "🔄 CHANGED" if has_changes else "✅ CURRENT"
            report.append(f"   {module}: {status}")
            
        return "\n".join(report)


def main():
    """CLI interface for checksum manager"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python checksum_manager.py <command> [modules...]")
        print("Commands:")
        print("  check <module>     - Check if module has changes")
        print("  update <module>    - Update checksums for module")
        print("  status <modules>   - Show status for multiple modules")
        print("  force-update <modules> - Force update all modules")
        return
        
    cm = ChecksumManager()
    command = sys.argv[1]
    modules = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if command == "check" and modules:
        for module in modules:
            has_changes = cm.has_changes(module)
            print(f"{module}: {'CHANGED' if has_changes else 'CURRENT'}")
            
    elif command == "update" and modules:
        for module in modules:
            cm.update_checksums(module)
            
    elif command == "status" and modules:
        print(cm.get_status_report(modules))
        
    elif command == "force-update" and modules:
        cm.force_update_all(modules)
        
    else:
        print("❌ Invalid command or missing modules")


if __name__ == "__main__":
    main()
