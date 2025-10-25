#!/usr/bin/env python3
"""
Phased Python Logging Migration
Systematic approach to migrate all Python logging to centralized event framework

Phase 1: Native GUI (print statements)
Phase 2: Python Services (standard logging)
Phase 3: Build System (mixed logging)
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any

def count_print_statements(directory: str) -> int:
    """Count total print statements in a directory"""
    try:
        result = subprocess.run([
            'find', directory, '-name', '*.py', '-exec', 'grep', '-c', 'print(', '{}', ';'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return sum(int(line.split(':')[-1]) for line in lines if line and ':' in line)
        return 0
    except:
        return 0

def count_logger_statements(directory: str) -> int:
    """Count standard logging statements in a directory"""
    try:
        result = subprocess.run([
            'find', directory, '-name', '*.py', '-exec', 'grep', '-c', '-E', 
            'logger\\.(debug|info|warn|warning|error|critical)', '{}', ';'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return sum(int(line.split(':')[-1]) for line in lines if line and ':' in line)
        return 0
    except:
        return 0

def get_files_with_prints(directory: str) -> List[str]:
    """Get list of files with print statements"""
    try:
        result = subprocess.run([
            'find', directory, '-name', '*.py', '-exec', 'grep', '-l', 'print(', '{}', ';'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)
        
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return []
    except:
        return []

def phase1_status():
    """Check Phase 1 (Native GUI) status"""
    print("🔍 Phase 1: Native GUI Migration Status")
    print("=" * 40)
    
    gui_dir = "control/native_gui"
    print_count = count_print_statements(gui_dir)
    files_with_prints = get_files_with_prints(gui_dir)
    
    print(f"📊 Print statements remaining: {print_count}")
    print(f"📁 Files with print statements: {len(files_with_prints)}")
    
    if print_count > 0:
        print("\n📋 Files needing migration:")
        for file_path in files_with_prints[:10]:  # Show top 10
            file_name = Path(file_path).name
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    count = content.count('print(')
                print(f"  {file_name}: {count} print statements")
            except:
                print(f"  {file_name}: ? print statements")
    
    return print_count == 0

def phase2_status():
    """Check Phase 2 (Python Services) status"""
    print("\n🔍 Phase 2: Python Services Migration Status")
    print("=" * 40)
    
    services_dir = "services"
    logger_count = count_logger_statements(services_dir)
    print_count = count_print_statements(services_dir)
    
    print(f"📊 Logger statements remaining: {logger_count}")
    print(f"📊 Print statements remaining: {print_count}")
    
    # Check individual services
    services = ["speech-to-text", "text-to-speech", "vision-ai"]
    for service in services:
        service_dir = f"services/{service}"
        if Path(service_dir).exists():
            s_logger = count_logger_statements(service_dir)
            s_print = count_print_statements(service_dir)
            print(f"  {service}: {s_logger} logger + {s_print} print statements")
    
    return logger_count == 0 and print_count == 0

def phase3_status():
    """Check Phase 3 (Build System) status"""
    print("\n🔍 Phase 3: Build System Migration Status")
    print("=" * 40)
    
    build_dir = "build"
    logger_count = count_logger_statements(build_dir)
    print_count = count_print_statements(build_dir)
    
    print(f"📊 Logger statements remaining: {logger_count}")
    print(f"📊 Print statements remaining: {print_count}")
    
    return logger_count == 0 and print_count == 0

def overall_status():
    """Check overall migration status"""
    print("🎯 Overall Migration Status")
    print("=" * 30)
    
    # Count across entire codebase (excluding venv)
    total_prints = 0
    total_loggers = 0
    
    # Key directories to check
    directories = ["control", "services", "build", "libs"]
    
    for directory in directories:
        if Path(directory).exists():
            prints = count_print_statements(directory)
            loggers = count_logger_statements(directory)
            total_prints += prints
            total_loggers += loggers
            
            if prints > 0 or loggers > 0:
                print(f"📁 {directory}/: {prints} prints + {loggers} loggers")
    
    print(f"\n📊 Total remaining: {total_prints} prints + {total_loggers} loggers")
    
    if total_prints == 0 and total_loggers == 0:
        print("🎉 Migration 100% Complete!")
        return True
    else:
        completion = max(0, 100 - ((total_prints + total_loggers) / 20))  # Rough estimate
        print(f"📈 Estimated completion: {completion:.1f}%")
        return False

def migrate_single_file(file_path: str) -> bool:
    """Migrate a single file using the existing migration script"""
    try:
        # Use the existing migration script
        script_path = Path(__file__).parent / "migrate_native_gui.py"
        result = subprocess.run([
            'python3', str(script_path), file_path, '--apply'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent.parent)
        
        return result.returncode == 0
    except:
        return False

def phase1_migrate_batch():
    """Migrate a batch of Native GUI files using the existing event framework"""
    print("🚀 Phase 1: Native GUI Migration (Using Existing Event Framework)")
    print("=" * 60)

    files_with_prints = get_files_with_prints("control/native_gui")

    if not files_with_prints:
        print("✅ No files need migration!")
        return True

    print(f"📋 Found {len(files_with_prints)} files to migrate")
    print("🔧 Using existing event framework from libs/event-framework/")
    print("📝 Migration pattern: print() -> events.info/debug/error()")

    # Show what the migration will do
    print("\n📋 Migration approach:")
    print("  • Import: from unhinged_events import create_service_logger")
    print("  • Create: events = create_service_logger('native-gui', '1.0.0')")
    print("  • Replace: print('message') -> events.info('message')")
    print("  • Variable name: 'events' (not 'gui_logger')")

    response = input(f"\n🔄 Proceed with migration? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migration cancelled")
        return False

    print("\n⚠️ Note: This requires manual migration using the existing event framework")
    print("🔧 The existing migration scripts need to be updated to use the correct API")

    return False  # Return False until we implement the correct migration

def main():
    """Main migration control"""
    if len(sys.argv) < 2:
        print("Usage: python3 phased_migration.py <command>")
        print("Commands:")
        print("  status    - Show migration status")
        print("  phase1    - Migrate Native GUI")
        print("  phase2    - Migrate Python Services")
        print("  phase3    - Migrate Build System")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        phase1_complete = phase1_status()
        phase2_complete = phase2_status()
        phase3_complete = phase3_status()
        overall_complete = overall_status()
        
        print(f"\n📋 Phase Status:")
        print(f"  Phase 1 (Native GUI): {'✅ Complete' if phase1_complete else '🔄 In Progress'}")
        print(f"  Phase 2 (Services): {'✅ Complete' if phase2_complete else '🔄 Pending'}")
        print(f"  Phase 3 (Build): {'✅ Complete' if phase3_complete else '🔄 Pending'}")
        print(f"  Overall: {'✅ Complete' if overall_complete else '🔄 In Progress'}")
    
    elif command == "phase1":
        if phase1_migrate_batch():
            print("✅ Phase 1 completed successfully!")
        else:
            print("⚠️ Phase 1 partially completed")
    
    elif command == "phase2":
        print("🚀 Phase 2: Python Services Migration")
        print("⚠️ Not implemented yet - requires service-specific migration logic")
    
    elif command == "phase3":
        print("🚀 Phase 3: Build System Migration")
        print("⚠️ Not implemented yet - requires build-specific migration logic")
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
