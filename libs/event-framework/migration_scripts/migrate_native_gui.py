#!/usr/bin/env python3
"""
Migration script for Native GUI logging

This script helps migrate print statements in the native GUI to structured event logging.
It analyzes existing print patterns and suggests/applies replacements.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Add the event framework to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "python" / "src"))

# Add the deterministic parser
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "build" / "regex"))
from python_parser import PythonPrintParser, analyze_print_migration_needs

class GUIMigrationAnalyzer:
    """Analyzes and migrates GUI logging patterns"""
    
    def __init__(self, gui_root: str):
        self.gui_root = Path(gui_root)
        self.patterns = {
            # Status messages (info level)
            r'print\("✅([^"]+)"\)': r'gui_logger.info("\1", {"status": "success"})',
            r'print\("🚀([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "startup"})',
            r'print\("🎯([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "activation"})',
            r'print\("🏗️([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "initialization"})',
            r'print\("🖼️([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "ui_display"})',
            r'print\("🎨([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "theming"})',
            
            # Error messages (error level)
            r'print\("❌([^"]+)"\)': r'gui_logger.error("\1")',
            r'print\(f"❌([^"]+)"\)': r'gui_logger.error(f"\1")',
            
            # Warning messages (warn level)
            r'print\("⚠️([^"]+)"\)': r'gui_logger.warn("\1")',
            r'print\(f"⚠️([^"]+)"\)': r'gui_logger.warn(f"\1")',
            
            # Debug messages (debug level)
            r'print\("🔧([^"]+)"\)': r'gui_logger.debug("\1", {"event_type": "configuration"})',
            r'print\("🔍([^"]+)"\)': r'gui_logger.debug("\1", {"event_type": "scanning"})',
            
            # Network/service messages
            r'print\("⚡([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "service_ready"})',
            r'print\("🌐([^"]+)"\)': r'gui_logger.info("\1", {"event_type": "network_ready"})',
        }
        
        self.import_pattern = r'^from unhinged_events import create_gui_logger'
        self.logger_init_pattern = r'^gui_logger = create_gui_logger\('
    
    def analyze_file(self, file_path: Path) -> Dict[str, any]:
        """Analyze a single Python file for migration opportunities"""
        if not file_path.exists() or file_path.suffix != '.py':
            return {"error": "File not found or not a Python file"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count print statements
        print_count = len(re.findall(r'print\(', content))
        
        # Find patterns that can be migrated
        migrations = []
        for pattern, replacement in self.patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                migrations.append({
                    "pattern": pattern,
                    "replacement": replacement,
                    "matches": len(matches),
                    "examples": matches[:3]  # First 3 examples
                })
        
        # Check if already has event framework imports
        has_import = bool(re.search(self.import_pattern, content, re.MULTILINE))
        has_logger = bool(re.search(self.logger_init_pattern, content, re.MULTILINE))
        
        return {
            "file": str(file_path),
            "print_count": print_count,
            "migrations": migrations,
            "has_event_import": has_import,
            "has_gui_logger": has_logger,
            "needs_migration": print_count > 0 and not has_logger
        }
    
    def analyze_directory(self) -> List[Dict[str, any]]:
        """Analyze all Python files in the GUI directory using deterministic parser"""
        results = []

        for py_file in self.gui_root.rglob("*.py"):
            # Skip __pycache__ and test files for now
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue

            try:
                # Use deterministic parser for complete analysis
                analysis = analyze_print_migration_needs(str(py_file))
                if analysis["total_print_statements"] > 0:
                    # Convert to expected format
                    converted_analysis = {
                        "file": str(py_file),
                        "print_count": analysis["total_print_statements"],
                        "has_event_import": not analysis["needs_event_import"],
                        "has_gui_logger": not analysis["needs_logger_init"],
                        "needs_migration": analysis["total_print_statements"] > 0,
                        "log_level_breakdown": analysis["log_level_breakdown"],
                        "suggested_service_name": analysis["suggested_service_name"]
                    }
                    results.append(converted_analysis)
            except Exception as e:
                print(f"⚠️ Error analyzing {py_file}: {e}")

        return results
    
    def generate_migration_plan(self, analysis_results: List[Dict[str, any]]) -> str:
        """Generate a detailed migration plan"""
        total_prints = sum(r.get("print_count", 0) for r in analysis_results)
        files_needing_migration = len([r for r in analysis_results if r.get("needs_migration", False)])
        
        plan = f"""
# Native GUI Migration Plan

## Summary
- **Total print statements to migrate:** {total_prints}
- **Files requiring migration:** {files_needing_migration}
- **Estimated effort:** {files_needing_migration * 0.5:.1f} hours

## File-by-File Analysis

"""
        
        for result in sorted(analysis_results, key=lambda x: x.get("print_count", 0), reverse=True):
            file_path = result["file"]
            print_count = result["print_count"]
            
            plan += f"### {file_path}\n"
            plan += f"- **Print statements:** {print_count}\n"
            plan += f"- **Needs migration:** {'Yes' if result.get('needs_migration') else 'No'}\n"
            
            if result.get("migrations"):
                plan += "- **Migration opportunities:**\n"
                for migration in result["migrations"]:
                    plan += f"  - {migration['matches']} instances of pattern: `{migration['pattern']}`\n"
                    if migration["examples"]:
                        plan += f"    - Examples: {migration['examples']}\n"
            
            plan += "\n"
        
        return plan
    
    def migrate_file(self, file_path: Path, dry_run: bool = True) -> Dict[str, any]:
        """Migrate a single file (dry run by default)"""
        if not file_path.exists():
            return {"error": "File not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content = original_content
        changes_made = []
        
        # Add import if not present
        if not re.search(self.import_pattern, modified_content, re.MULTILINE):
            # Find the best place to add the import (after existing imports)
            import_lines = []
            lines = modified_content.split('\n')
            insert_index = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
                elif line.strip() == '' and insert_index > 0:
                    break
            
            lines.insert(insert_index, 'from unhinged_events import create_gui_logger')
            modified_content = '\n'.join(lines)
            changes_made.append("Added event framework import")
        
        # Add logger initialization if not present
        if not re.search(self.logger_init_pattern, modified_content, re.MULTILINE):
            # Add after imports, before main code
            lines = modified_content.split('\n')
            insert_index = 0
            
            for i, line in enumerate(lines):
                if not (line.startswith('import ') or line.startswith('from ') or line.strip() == ''):
                    insert_index = i
                    break
            
            service_name = file_path.stem.replace('_', '-')
            logger_init = f'\n# Initialize GUI event logger\ngui_logger = create_gui_logger("unhinged-{service_name}", "1.0.0")\n'
            lines.insert(insert_index, logger_init)
            modified_content = '\n'.join(lines)
            changes_made.append("Added GUI logger initialization")
        
        # Apply pattern replacements
        for pattern, replacement in self.patterns.items():
            matches_before = len(re.findall(pattern, modified_content))
            if matches_before > 0:
                modified_content = re.sub(pattern, replacement, modified_content)
                matches_after = len(re.findall(pattern, modified_content))
                changes_made.append(f"Replaced {matches_before} instances of pattern: {pattern}")
        
        # Write the file if not dry run
        if not dry_run and modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        
        return {
            "file": str(file_path),
            "changes_made": changes_made,
            "dry_run": dry_run,
            "modified": modified_content != original_content
        }

def main():
    """Main migration script"""
    if len(sys.argv) < 2:
        print("Usage: python migrate_native_gui.py <gui_directory> [--apply]")
        print("  --apply: Actually apply changes (default is dry run)")
        sys.exit(1)
    
    gui_directory = sys.argv[1]
    apply_changes = "--apply" in sys.argv
    
    analyzer = GUIMigrationAnalyzer(gui_directory)
    
    print("🔍 Analyzing Native GUI logging patterns...")
    analysis_results = analyzer.analyze_directory()
    
    if not analysis_results:
        print("✅ No files with print statements found!")
        return
    
    print(f"📊 Found {len(analysis_results)} files with logging to migrate")
    
    # Generate migration plan
    plan = analyzer.generate_migration_plan(analysis_results)
    print(plan)
    
    if apply_changes:
        print("🚀 Applying migrations...")
        for result in analysis_results:
            if result.get("needs_migration"):
                file_path = Path(result["file"])
                migration_result = analyzer.migrate_file(file_path, dry_run=False)
                
                if migration_result.get("modified"):
                    print(f"✅ Migrated: {file_path}")
                    for change in migration_result["changes_made"]:
                        print(f"   - {change}")
                else:
                    print(f"⏭️ Skipped: {file_path} (no changes needed)")
        
        print("\n🎉 Migration complete!")
        print("📝 Next steps:")
        print("   1. Test the migrated code")
        print("   2. Update any remaining manual print statements")
        print("   3. Configure log levels as needed")
    else:
        print("\n🔍 This was a dry run. Use --apply to make actual changes.")

if __name__ == "__main__":
    main()
