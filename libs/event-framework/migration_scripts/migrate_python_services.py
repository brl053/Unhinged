#!/usr/bin/env python3
"""
Migration script for Python services logging

This script helps migrate Python services from standard logging to the event framework.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ServiceMigrationAnalyzer:
    """Analyzes and migrates Python service logging patterns"""
    
    def __init__(self, services_root: str):
        self.services_root = Path(services_root)
        
        # Patterns for migrating standard logging to event framework
        self.logging_patterns = {
            # Standard logging patterns
            r'logger\.info\(([^)]+)\)': r'event_logger.info(\1)',
            r'logger\.debug\(([^)]+)\)': r'event_logger.debug(\1)',
            r'logger\.warning\(([^)]+)\)': r'event_logger.warn(\1)',
            r'logger\.warn\(([^)]+)\)': r'event_logger.warn(\1)',
            r'logger\.error\(([^)]+)\)': r'event_logger.error(\1)',
            
            # Logging with format strings
            r'logging\.info\(([^)]+)\)': r'event_logger.info(\1)',
            r'logging\.debug\(([^)]+)\)': r'event_logger.debug(\1)',
            r'logging\.warning\(([^)]+)\)': r'event_logger.warn(\1)',
            r'logging\.warn\(([^)]+)\)': r'event_logger.warn(\1)',
            r'logging\.error\(([^)]+)\)': r'event_logger.error(\1)',
        }
        
        # Import replacements
        self.import_replacements = {
            r'import logging': 'from unhinged_events import create_service_logger',
            r'from logging import.*': '# Replaced with unhinged_events',
            r'logger = logging\.getLogger\(__name__\)': 'event_logger = create_service_logger(SERVICE_NAME, "1.0.0")',
            r'logger = logging\.getLogger\([^)]+\)': 'event_logger = create_service_logger(SERVICE_NAME, "1.0.0")',
        }
    
    def detect_service_name(self, file_path: Path) -> str:
        """Detect the service name from file path or content"""
        # Try to get from parent directory name
        if "services" in file_path.parts:
            services_index = file_path.parts.index("services")
            if services_index + 1 < len(file_path.parts):
                return file_path.parts[services_index + 1]
        
        # Fallback to file name
        return file_path.stem.replace('_', '-')
    
    def analyze_file(self, file_path: Path) -> Dict[str, any]:
        """Analyze a single Python service file"""
        if not file_path.exists() or file_path.suffix != '.py':
            return {"error": "File not found or not a Python file"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count logging statements
        logging_count = len(re.findall(r'logger\.|logging\.', content))
        print_count = len(re.findall(r'print\(', content))
        
        # Check for existing logging imports
        has_logging_import = bool(re.search(r'import logging|from logging', content))
        has_logger_creation = bool(re.search(r'logger = logging\.getLogger', content))
        
        # Check for event framework
        has_event_import = bool(re.search(r'from unhinged_events import', content))
        has_event_logger = bool(re.search(r'event_logger = create_service_logger', content))
        
        # Find specific patterns
        migrations = []
        for pattern, replacement in self.logging_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                migrations.append({
                    "pattern": pattern,
                    "replacement": replacement,
                    "matches": len(matches),
                    "examples": matches[:3]
                })
        
        service_name = self.detect_service_name(file_path)
        
        return {
            "file": str(file_path),
            "service_name": service_name,
            "logging_count": logging_count,
            "print_count": print_count,
            "has_logging_import": has_logging_import,
            "has_logger_creation": has_logger_creation,
            "has_event_import": has_event_import,
            "has_event_logger": has_event_logger,
            "migrations": migrations,
            "needs_migration": (logging_count > 0 or print_count > 0) and not has_event_logger
        }
    
    def analyze_service_directory(self, service_dir: Path) -> List[Dict[str, any]]:
        """Analyze all Python files in a service directory"""
        results = []
        
        for py_file in service_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            analysis = self.analyze_file(py_file)
            if analysis.get("logging_count", 0) > 0 or analysis.get("print_count", 0) > 0:
                results.append(analysis)
        
        return results
    
    def migrate_file(self, file_path: Path, service_name: str, dry_run: bool = True) -> Dict[str, any]:
        """Migrate a single service file"""
        if not file_path.exists():
            return {"error": "File not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        modified_content = original_content
        changes_made = []
        
        # Replace imports
        for old_import, new_import in self.import_replacements.items():
            if re.search(old_import, modified_content):
                modified_content = re.sub(old_import, new_import, modified_content)
                changes_made.append(f"Replaced import: {old_import}")
        
        # Add service name constant if not present
        if "SERVICE_NAME" not in modified_content and "create_service_logger" in modified_content:
            lines = modified_content.split('\n')
            # Find a good place to add the constant (after imports)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_index = i + 1
                elif line.strip() == '' and insert_index > 0:
                    break
            
            lines.insert(insert_index, f'SERVICE_NAME = "{service_name}"')
            modified_content = '\n'.join(lines)
            changes_made.append(f"Added SERVICE_NAME constant: {service_name}")
        
        # Replace logger creation with proper service name
        modified_content = re.sub(
            r'event_logger = create_service_logger\(SERVICE_NAME, "[^"]+"\)',
            f'event_logger = create_service_logger("{service_name}", "1.0.0")',
            modified_content
        )
        
        # Apply logging pattern replacements
        for pattern, replacement in self.logging_patterns.items():
            matches_before = len(re.findall(pattern, modified_content))
            if matches_before > 0:
                modified_content = re.sub(pattern, replacement, modified_content)
                changes_made.append(f"Replaced {matches_before} logging calls: {pattern}")
        
        # Handle print statements (convert to appropriate log level)
        print_patterns = {
            r'print\(f?"([^"]*ERROR[^"]*)"[^)]*\)': r'event_logger.error("\1")',
            r'print\(f?"([^"]*WARN[^"]*)"[^)]*\)': r'event_logger.warn("\1")',
            r'print\(f?"([^"]*DEBUG[^"]*)"[^)]*\)': r'event_logger.debug("\1")',
            r'print\(f?"([^"]*)"[^)]*\)': r'event_logger.info("\1")',  # Default to info
        }
        
        for pattern, replacement in print_patterns.items():
            matches_before = len(re.findall(pattern, modified_content))
            if matches_before > 0:
                modified_content = re.sub(pattern, replacement, modified_content)
                changes_made.append(f"Converted {matches_before} print statements")
                break  # Only apply the first matching pattern
        
        # Write the file if not dry run
        if not dry_run and modified_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
        
        return {
            "file": str(file_path),
            "service_name": service_name,
            "changes_made": changes_made,
            "dry_run": dry_run,
            "modified": modified_content != original_content
        }
    
    def generate_service_migration_plan(self, service_dir: Path) -> str:
        """Generate migration plan for a specific service"""
        analysis_results = self.analyze_service_directory(service_dir)
        
        if not analysis_results:
            return f"✅ No migration needed for {service_dir.name}"
        
        total_logging = sum(r.get("logging_count", 0) for r in analysis_results)
        total_prints = sum(r.get("print_count", 0) for r in analysis_results)
        files_needing_migration = len([r for r in analysis_results if r.get("needs_migration", False)])
        
        plan = f"""
## Service: {service_dir.name}

### Summary
- **Logging statements to migrate:** {total_logging}
- **Print statements to convert:** {total_prints}
- **Files requiring migration:** {files_needing_migration}
- **Estimated effort:** {files_needing_migration * 0.3:.1f} hours

### Files
"""
        
        for result in analysis_results:
            file_path = Path(result["file"]).name
            plan += f"- **{file_path}**: {result['logging_count']} logging, {result['print_count']} prints\n"
        
        return plan

def main():
    """Main migration script for Python services"""
    if len(sys.argv) < 2:
        print("Usage: python migrate_python_services.py <services_directory> [service_name] [--apply]")
        print("  service_name: Migrate specific service (optional)")
        print("  --apply: Actually apply changes (default is dry run)")
        sys.exit(1)
    
    services_directory = sys.argv[1]
    specific_service = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    apply_changes = "--apply" in sys.argv
    
    analyzer = ServiceMigrationAnalyzer(services_directory)
    services_root = Path(services_directory)
    
    if specific_service:
        # Migrate specific service
        service_dir = services_root / specific_service
        if not service_dir.exists():
            print(f"❌ Service directory not found: {service_dir}")
            sys.exit(1)
        
        print(f"🔍 Analyzing service: {specific_service}")
        plan = analyzer.generate_service_migration_plan(service_dir)
        print(plan)
        
        if apply_changes:
            print(f"🚀 Migrating service: {specific_service}")
            analysis_results = analyzer.analyze_service_directory(service_dir)
            
            for result in analysis_results:
                if result.get("needs_migration"):
                    file_path = Path(result["file"])
                    migration_result = analyzer.migrate_file(
                        file_path, 
                        result["service_name"], 
                        dry_run=False
                    )
                    
                    if migration_result.get("modified"):
                        print(f"✅ Migrated: {file_path.name}")
                        for change in migration_result["changes_made"]:
                            print(f"   - {change}")
    else:
        # Analyze all services
        print("🔍 Analyzing all Python services...")
        
        for service_dir in services_root.iterdir():
            if service_dir.is_dir() and not service_dir.name.startswith('.'):
                plan = analyzer.generate_service_migration_plan(service_dir)
                print(plan)
        
        if apply_changes:
            print("🚀 Migrating all services...")
            for service_dir in services_root.iterdir():
                if service_dir.is_dir() and not service_dir.name.startswith('.'):
                    analysis_results = analyzer.analyze_service_directory(service_dir)
                    
                    for result in analysis_results:
                        if result.get("needs_migration"):
                            file_path = Path(result["file"])
                            migration_result = analyzer.migrate_file(
                                file_path, 
                                result["service_name"], 
                                dry_run=False
                            )
                            
                            if migration_result.get("modified"):
                                print(f"✅ Migrated: {service_dir.name}/{file_path.name}")
    
    if not apply_changes:
        print("\n🔍 This was a dry run. Use --apply to make actual changes.")
    else:
        print("\n🎉 Migration complete!")

if __name__ == "__main__":
    main()
