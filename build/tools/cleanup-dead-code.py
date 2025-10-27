#!/usr/bin/env python3
"""
@llm-type cleanup-tool
@llm-legend Safe dead code cleanup tool with backup and rollback capabilities
@llm-key Removes identified dead code with safety checks and backup mechanisms
@llm-map Integrates with dead-code-analyzer for systematic codebase cleanup
@llm-axiom Cleanup operations must be reversible and include comprehensive safety checks
@llm-contract Provides safe cleanup with backup, dry-run, and rollback capabilities
@llm-token cleanup-tool: Safe dead code removal with backup and rollback

Dead Code Cleanup Tool

Safe removal tool for dead code identified by the dead-code-analyzer.
Includes backup mechanisms, dry-run mode, and rollback capabilities.

Features:
- Safety level filtering (only remove safe items by default)
- Backup creation before deletion
- Dry-run mode for preview
- Rollback capability
- Size and impact reporting

Author: Unhinged Team
Version: 1.0.0
Date: 2025-01-27
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CleanupResult:
    """Result of cleanup operation"""
    removed_files: List[str]
    removed_size: int
    skipped_files: List[str]
    errors: List[str]
    backup_location: Optional[str] = None


class DeadCodeCleanup:
    """
    Safe dead code cleanup tool.
    
    @llm-type cleanup-class
    @llm-legend Safe cleanup implementation with backup and rollback capabilities
    @llm-key Removes dead code with comprehensive safety checks and recovery options
    """
    
    def __init__(self, project_root: Path, backup_dir: Optional[Path] = None):
        """Initialize cleanup tool."""
        self.project_root = project_root
        self.backup_dir = backup_dir or (project_root / ".cleanup-backups")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def cleanup_from_analysis(self, 
                            analysis_file: Path,
                            safety_levels: List[str] = None,
                            dry_run: bool = True,
                            create_backup: bool = True) -> CleanupResult:
        """
        Cleanup dead code based on analysis results.
        
        Args:
            analysis_file: JSON file from dead-code-analyzer
            safety_levels: List of safety levels to clean (default: ['safe'])
            dry_run: If True, only show what would be removed
            create_backup: If True, create backup before removal
            
        Returns:
            CleanupResult with details of cleanup operation
        """
        if safety_levels is None:
            safety_levels = ['safe']  # Conservative default
        
        print(f"🧹 Starting cleanup (dry_run={dry_run})...")
        
        # Load analysis results
        try:
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
        except Exception as e:
            return CleanupResult([], 0, [], [f"Failed to load analysis file: {e}"])
        
        # Filter items by safety level
        items_to_remove = []
        for item in analysis.get('items', []):
            if item['safety_level'] in safety_levels:
                items_to_remove.append(item)
        
        print(f"📋 Found {len(items_to_remove)} items to remove with safety levels: {safety_levels}")
        
        if not items_to_remove:
            return CleanupResult([], 0, [], [])
        
        # Create backup if requested and not dry run
        backup_location = None
        if create_backup and not dry_run:
            backup_location = self._create_backup(items_to_remove)
            print(f"💾 Backup created: {backup_location}")
        
        # Process removals
        removed_files = []
        removed_size = 0
        skipped_files = []
        errors = []
        
        for item in items_to_remove:
            try:
                item_path = item['path']
                
                # Handle phantom modules (not real files)
                if item_path.startswith('phantom:'):
                    if dry_run:
                        print(f"  🔍 Would remove phantom module: {item_path}")
                        removed_files.append(item_path)
                    else:
                        # For phantom modules, we'd need to edit config files
                        # This is more complex and should be done manually
                        print(f"  ⚠️  Phantom module requires manual cleanup: {item_path}")
                        skipped_files.append(item_path)
                    continue
                
                # Handle real files
                full_path = self.project_root / item_path
                
                if not full_path.exists():
                    print(f"  ⚠️  File not found: {item_path}")
                    skipped_files.append(item_path)
                    continue
                
                file_size = item.get('size_bytes', 0)
                
                if dry_run:
                    print(f"  🔍 Would remove: {item_path} ({file_size:,} bytes)")
                    removed_files.append(item_path)
                    removed_size += file_size
                else:
                    print(f"  🗑️  Removing: {item_path} ({file_size:,} bytes)")
                    
                    if full_path.is_file():
                        full_path.unlink()
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
                    
                    removed_files.append(item_path)
                    removed_size += file_size
                    
            except Exception as e:
                error_msg = f"Failed to remove {item.get('path', 'unknown')}: {e}"
                print(f"  ❌ {error_msg}")
                errors.append(error_msg)
        
        # Summary
        if dry_run:
            print(f"\n📊 DRY RUN SUMMARY:")
            print(f"  Would remove: {len(removed_files)} items")
            print(f"  Total size: {removed_size:,} bytes ({removed_size/1024/1024:.1f} MB)")
            print(f"  Skipped: {len(skipped_files)} items")
            print(f"  Errors: {len(errors)} items")
        else:
            print(f"\n📊 CLEANUP SUMMARY:")
            print(f"  Removed: {len(removed_files)} items")
            print(f"  Total size freed: {removed_size:,} bytes ({removed_size/1024/1024:.1f} MB)")
            print(f"  Skipped: {len(skipped_files)} items")
            print(f"  Errors: {len(errors)} items")
            if backup_location:
                print(f"  Backup: {backup_location}")
        
        return CleanupResult(
            removed_files=removed_files,
            removed_size=removed_size,
            skipped_files=skipped_files,
            errors=errors,
            backup_location=backup_location
        )
    
    def _create_backup(self, items_to_remove: List[Dict]) -> str:
        """Create backup of files before removal."""
        backup_name = f"cleanup_backup_{self.timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create backup manifest
        manifest = {
            "timestamp": self.timestamp,
            "items": items_to_remove,
            "project_root": str(self.project_root)
        }
        
        with open(backup_path / "manifest.json", 'w') as f:
            json.dumps(manifest, f, indent=2)
        
        # Copy files to backup
        for item in items_to_remove:
            item_path = item['path']
            
            # Skip phantom modules
            if item_path.startswith('phantom:'):
                continue
            
            source_path = self.project_root / item_path
            if not source_path.exists():
                continue
            
            # Create backup file path
            backup_file_path = backup_path / item_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if source_path.is_file():
                    shutil.copy2(source_path, backup_file_path)
                elif source_path.is_dir():
                    shutil.copytree(source_path, backup_file_path)
            except Exception as e:
                print(f"  ⚠️  Failed to backup {item_path}: {e}")
        
        return str(backup_path)
    
    def list_backups(self) -> List[Dict]:
        """List available backups."""
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                manifest_file = backup_dir / "manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest = json.load(f)
                        
                        backups.append({
                            "name": backup_dir.name,
                            "path": str(backup_dir),
                            "timestamp": manifest.get("timestamp"),
                            "item_count": len(manifest.get("items", []))
                        })
                    except Exception:
                        continue
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def rollback(self, backup_name: str) -> bool:
        """Rollback from a backup."""
        backup_path = self.backup_dir / backup_name
        manifest_file = backup_path / "manifest.json"
        
        if not manifest_file.exists():
            print(f"❌ Backup manifest not found: {manifest_file}")
            return False
        
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            print(f"🔄 Rolling back from backup: {backup_name}")
            
            # Restore files
            restored_count = 0
            for item in manifest.get("items", []):
                item_path = item['path']
                
                # Skip phantom modules
                if item_path.startswith('phantom:'):
                    continue
                
                backup_file_path = backup_path / item_path
                target_path = self.project_root / item_path
                
                if backup_file_path.exists():
                    try:
                        # Create parent directories
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        if backup_file_path.is_file():
                            shutil.copy2(backup_file_path, target_path)
                        elif backup_file_path.is_dir():
                            if target_path.exists():
                                shutil.rmtree(target_path)
                            shutil.copytree(backup_file_path, target_path)
                        
                        restored_count += 1
                        print(f"  ✅ Restored: {item_path}")
                        
                    except Exception as e:
                        print(f"  ❌ Failed to restore {item_path}: {e}")
            
            print(f"🎉 Rollback complete: {restored_count} items restored")
            return True
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False


def main():
    """CLI entry point for cleanup tool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up dead code safely")
    parser.add_argument("--analysis", type=Path, required=True,
                       help="JSON analysis file from dead-code-analyzer")
    parser.add_argument("--safety-levels", nargs='+', default=['safe'],
                       choices=['safe', 'likely_safe', 'review', 'unsafe'],
                       help="Safety levels to clean (default: safe only)")
    parser.add_argument("--dry-run", action='store_true',
                       help="Show what would be removed without actually removing")
    parser.add_argument("--no-backup", action='store_true',
                       help="Skip creating backup (not recommended)")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(),
                       help="Project root directory")
    
    # Rollback commands
    parser.add_argument("--list-backups", action='store_true',
                       help="List available backups")
    parser.add_argument("--rollback", type=str,
                       help="Rollback from specified backup")
    
    args = parser.parse_args()
    
    cleanup = DeadCodeCleanup(args.project_root)
    
    # Handle rollback commands
    if args.list_backups:
        backups = cleanup.list_backups()
        if backups:
            print("📦 Available backups:")
            for backup in backups:
                print(f"  {backup['name']} - {backup['timestamp']} ({backup['item_count']} items)")
        else:
            print("📦 No backups found")
        return 0
    
    if args.rollback:
        success = cleanup.rollback(args.rollback)
        return 0 if success else 1
    
    # Perform cleanup
    if not args.analysis.exists():
        print(f"❌ Analysis file not found: {args.analysis}")
        return 1
    
    result = cleanup.cleanup_from_analysis(
        analysis_file=args.analysis,
        safety_levels=args.safety_levels,
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    if result.errors:
        print(f"\n⚠️  {len(result.errors)} errors occurred during cleanup")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
