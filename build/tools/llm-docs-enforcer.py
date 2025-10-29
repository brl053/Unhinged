#!/usr/bin/env python3
"""
@llm-type util.enforcer
@llm-does llmdocs enforcement and template generation for evolved format
@llm-rule all code files must have proper llmdocs tags for ai comprehension
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse


class LLMDocsEnforcer:
    """
    Enforces LLM documentation standards across all source files.
    
    Validates and injects @llm- headers into source files to ensure
    consistent documentation for AI comprehension.
    """
    
    # File type mappings to comment styles
    COMMENT_STYLES = {
        '.py': ('"""', '"""', '#'),
        '.kt': ('//', '//', '//'),
        '.js': ('//', '//', '//'),
        '.ts': ('//', '//', '//'),
        '.java': ('//', '//', '//'),
        '.sh': ('#', '#', '#'),
        '.yml': ('#', '#', '#'),
        '.yaml': ('#', '#', '#'),
    }
    
    # Required @llm- tags - Evolved 3-tag format
    REQUIRED_TAGS = ['@llm-type', '@llm-does']
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations = []
        self.fixed_files = []
        
    def scan_files(self, directories: List[str]) -> List[Path]:
        """Scan directories for source files requiring @llm- headers."""
        files = []
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                continue
                
            for ext in self.COMMENT_STYLES.keys():
                pattern = f"**/*{ext}"
                found_files = list(dir_path.glob(pattern))
                files.extend(found_files)
                
        # Filter out generated files and cache directories
        filtered_files = []
        for file_path in files:
            if self._should_process_file(file_path):
                filtered_files.append(file_path)
                
        return filtered_files
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed for @llm- headers."""
        exclude_patterns = [
            '__pycache__',
            'build/python/venv',
            '.git',
            'node_modules',
            '_pb2.py',
            '_pb2_grpc.py',
            'generated/',
        ]
        
        path_str = str(file_path)
        for pattern in exclude_patterns:
            if pattern in path_str:
                return False
                
        return True
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate if file has proper @llm- headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, [f"Failed to read file: {e}"]
            
        violations = []
        
        # Check for required @llm- tags
        for tag in self.REQUIRED_TAGS:
            if tag not in content:
                violations.append(f"Missing required tag: {tag}")
                
        return len(violations) == 0, violations
    
    def inject_headers(self, file_path: Path, file_type: str = None) -> bool:
        """Inject @llm- headers into file if missing."""
        if not file_type:
            file_type = file_path.suffix
            
        if file_type not in self.COMMENT_STYLES:
            return False
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return False
            
        # Generate appropriate header based on file type and path
        header = self._generate_header(file_path, file_type)
        
        # Insert header after shebang if present
        lines = content.split('\n')
        insert_index = 0
        
        if lines and lines[0].startswith('#!'):
            insert_index = 1
            
        # Insert header
        header_lines = header.split('\n')
        for i, header_line in enumerate(header_lines):
            lines.insert(insert_index + i, header_line)
            
        new_content = '\n'.join(lines)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        except Exception:
            return False
    
    def _generate_header(self, file_path: Path, file_type: str) -> str:
        """Generate appropriate @llm- header for file."""
        comment_start, comment_end, line_comment = self.COMMENT_STYLES[file_type]
        
        # Determine file purpose from path
        path_parts = file_path.parts
        
        if 'services' in path_parts:
            llm_type = 'service'
            purpose = 'microservice component'
        elif 'control' in path_parts:
            llm_type = 'control-system'
            purpose = 'system control component'
        elif 'platforms' in path_parts:
            llm_type = 'platform'
            purpose = 'platform infrastructure component'
        elif 'build' in path_parts:
            llm_type = 'build-tool'
            purpose = 'build system component'
        else:
            llm_type = 'component'
            purpose = 'system component'
            
        file_name = file_path.name
        
        if file_type == '.py':
            return f'''"""
@llm-type {llm_type}
@llm-does {purpose}
"""'''
        else:
            return f'''{line_comment}
{line_comment} @llm-type {llm_type}
{line_comment} @llm-does {purpose}
{line_comment}'''
    
    def enforce_compliance(self, directories: List[str], fix: bool = False) -> bool:
        """Enforce @llm- documentation compliance across directories."""
        files = self.scan_files(directories)
        all_compliant = True
        
        print(f"Scanning {len(files)} files for @llm- compliance...")
        
        for file_path in files:
            is_compliant, violations = self.validate_file(file_path)
            
            if not is_compliant:
                all_compliant = False
                self.violations.append({
                    'file': str(file_path),
                    'violations': violations
                })
                
                if fix:
                    if self.inject_headers(file_path):
                        self.fixed_files.append(str(file_path))
                        print(f"✅ Fixed: {file_path}")
                    else:
                        print(f"❌ Failed to fix: {file_path}")
                else:
                    print(f"❌ Non-compliant: {file_path}")
                    for violation in violations:
                        print(f"   - {violation}")
                        
        return all_compliant
    
    def report_results(self):
        """Report enforcement results."""
        if self.violations:
            print(f"\n📊 Results:")
            print(f"   Non-compliant files: {len(self.violations)}")
            print(f"   Fixed files: {len(self.fixed_files)}")
        else:
            print("\n✅ All files are @llm- compliant!")


def main():
    parser = argparse.ArgumentParser(description="Enforce LLM documentation standards")
    parser.add_argument("--fix", action="store_true", help="Fix non-compliant files")
    parser.add_argument("--directories", nargs="+",
                       default=["services", "control", "platforms", "build", "vm"],
                       help="Directories to scan")
    
    args = parser.parse_args()
    
    project_root = Path.cwd()
    enforcer = LLMDocsEnforcer(project_root)
    
    is_compliant = enforcer.enforce_compliance(args.directories, fix=args.fix)
    enforcer.report_results()
    
    if not is_compliant and not args.fix:
        print("\n💡 Run with --fix to automatically add missing headers")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
