#!/usr/bin/env python3
"""
Complete Python Logging Migration Script
Uses deterministic parser to migrate ALL print statements and standard logging

Phase 1: Complete Native GUI migration (remaining print statements)
Phase 2: Migrate Python services (standard logging)
Phase 3: Migrate build system logging
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add the deterministic parser
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "regex"))
from python_parser import PythonPrintParser, analyze_print_migration_needs

def migrate_file_complete(file_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """Complete migration of a Python file using deterministic parsing"""
    parser = PythonPrintParser()
    result = parser.parse_file(file_path)
    
    if result.total_prints == 0:
        return {
            "file": file_path,
            "modified": False,
            "changes_made": [],
            "message": "No print statements found"
        }
    
    # Read original file
    with open(file_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    modified_content = original_content
    changes_made = []
    
    # Add imports if needed
    if result.needs_event_import:
        modified_content = add_event_framework_import(modified_content)
        changes_made.append("Added event framework import")
    
    if result.needs_logger_init:
        modified_content = add_logger_initialization(modified_content, result.suggested_service_name)
        changes_made.append(f"Added logger initialization for {result.suggested_service_name}")
    
    # Replace print statements (in reverse order to preserve line numbers)
    print_statements = sorted(result.print_statements, key=lambda x: x.line_number, reverse=True)
    
    lines = modified_content.split('\n')
    
    for stmt in print_statements:
        line_idx = stmt.line_number - 1  # Convert to 0-based index
        if line_idx < len(lines):
            original_line = lines[line_idx]
            
            # Extract indentation
            indent = len(original_line) - len(original_line.lstrip())
            indent_str = ' ' * indent
            
            # Replace with structured logging
            new_line = indent_str + stmt.migration_pattern
            lines[line_idx] = new_line
            
            changes_made.append(f"Line {stmt.line_number}: {stmt.suggested_log_level} - {stmt.full_statement[:50]}...")
    
    modified_content = '\n'.join(lines)
    
    # Write file if not dry run
    if not dry_run and modified_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
    
    return {
        "file": file_path,
        "modified": modified_content != original_content,
        "changes_made": changes_made,
        "total_prints_migrated": result.total_prints,
        "log_level_breakdown": {
            "ERROR": len([p for p in result.print_statements if p.suggested_log_level == "ERROR"]),
            "WARN": len([p for p in result.print_statements if p.suggested_log_level == "WARN"]),
            "INFO": len([p for p in result.print_statements if p.suggested_log_level == "INFO"]),
            "DEBUG": len([p for p in result.print_statements if p.suggested_log_level == "DEBUG"])
        }
    }

def add_event_framework_import(content: str) -> str:
    """Add event framework import to file content"""
    lines = content.split('\n')
    
    # Check if import already exists
    for line in lines:
        if "from unhinged_events import" in line:
            return content  # Already has import
    
    # Find the best place to add import (after existing imports)
    insert_index = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_index = i + 1
        elif line.strip() == '' and insert_index > 0:
            break
    
    # Add the import
    import_line = "from unhinged_events import create_gui_logger"
    lines.insert(insert_index, import_line)
    
    return '\n'.join(lines)

def add_logger_initialization(content: str, service_name: str) -> str:
    """Add logger initialization to file content"""
    lines = content.split('\n')
    
    # Check if logger already exists
    for line in lines:
        if "gui_logger = create_gui_logger" in line:
            return content  # Already has logger
    
    # Find where to add logger init (after imports, before main code)
    insert_index = 0
    for i, line in enumerate(lines):
        if not (line.startswith('import ') or line.startswith('from ') or 
                line.strip() == '' or line.startswith('#')):
            insert_index = i
            break
    
    # Add logger initialization
    logger_lines = [
        "",
        "# Initialize GUI event logger",
        f'gui_logger = create_gui_logger("{service_name}", "1.0.0")',
        ""
    ]
    
    for j, logger_line in enumerate(logger_lines):
        lines.insert(insert_index + j, logger_line)
    
    return '\n'.join(lines)

def phase1_complete_native_gui():
    """Phase 1: Complete Native GUI migration"""
    print("🚀 Phase 1: Completing Native GUI Migration")
    print("=" * 50)
    
    gui_directory = Path(__file__).parent.parent.parent.parent / "control" / "native_gui"
    if not gui_directory.exists():
        print(f"❌ Directory not found: {gui_directory}")
        return False
    
    # Find all Python files with print statements
    files_to_migrate = []
    total_prints = 0
    
    for py_file in gui_directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            analysis = analyze_print_migration_needs(str(py_file))
            if analysis["total_print_statements"] > 0:
                files_to_migrate.append((str(py_file), analysis))
                total_prints += analysis["total_print_statements"]
        except Exception as e:
            print(f"⚠️ Error analyzing {py_file}: {e}")
    
    print(f"📊 Found {len(files_to_migrate)} files with {total_prints} print statements to migrate")
    
    if not files_to_migrate:
        print("✅ No files need migration!")
        return True
    
    # Show top files
    files_to_migrate.sort(key=lambda x: x[1]["total_print_statements"], reverse=True)
    print("\n📋 Top files to migrate:")
    for file_path, analysis in files_to_migrate[:10]:
        file_name = Path(file_path).name
        count = analysis["total_print_statements"]
        breakdown = analysis["log_level_breakdown"]
        print(f"  {file_name}: {count} prints (E:{breakdown['ERROR']}, W:{breakdown['WARN']}, I:{breakdown['INFO']}, D:{breakdown['DEBUG']})")
    
    # Ask for confirmation
    response = input(f"\n🔄 Migrate {total_prints} print statements across {len(files_to_migrate)} files? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return False
    
    # Perform migration
    print("\n🔄 Migrating files...")
    migrated_count = 0
    total_migrated_prints = 0
    
    for file_path, analysis in files_to_migrate:
        result = migrate_file_complete(file_path, dry_run=False)
        
        if result["modified"]:
            file_name = Path(file_path).name
            prints_migrated = result["total_prints_migrated"]
            migrated_count += 1
            total_migrated_prints += prints_migrated
            
            print(f"✅ {file_name}: {prints_migrated} prints migrated")
        else:
            print(f"⏭️ {Path(file_path).name}: No changes needed")
    
    print(f"\n🎉 Phase 1 Complete!")
    print(f"📊 Migrated {total_migrated_prints} print statements across {migrated_count} files")
    
    # Verify completion
    remaining_prints = 0
    for py_file in gui_directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                remaining_prints += content.count('print(')
        except:
            pass
    
    print(f"📈 Remaining print statements in Native GUI: {remaining_prints}")
    
    return remaining_prints == 0

def main():
    """Main migration script"""
    if len(sys.argv) > 1 and sys.argv[1] == "phase1":
        success = phase1_complete_native_gui()
        if success:
            print("✅ Phase 1 completed successfully!")
        else:
            print("❌ Phase 1 incomplete")
            sys.exit(1)
    else:
        print("Usage: python3 complete_migration.py phase1")
        print("  phase1: Complete Native GUI migration")

if __name__ == "__main__":
    main()
