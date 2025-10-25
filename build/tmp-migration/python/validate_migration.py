#!/usr/bin/env python3
"""
Migration Validation Script

Validates that migrated code follows event framework standards and
maintains functionality while improving observability.
"""

import os
import re
import sys
import ast
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class MigrationValidator:
    """Validates migrated code quality and compliance"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.validation_results = {
            "files_checked": 0,
            "issues_found": 0,
            "warnings": [],
            "errors": [],
            "suggestions": []
        }
    
    def validate_file(self, file_path: Path) -> Dict[str, any]:
        """Validate a single migrated Python file"""
        if not file_path.exists() or file_path.suffix != '.py':
            return {"error": "File not found or not a Python file"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {
            "file": str(file_path),
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "compliance_score": 100
        }
        
        # Check 1: Event framework imports
        self._check_imports(content, results)
        
        # Check 2: Logger initialization
        self._check_logger_initialization(content, results)
        
        # Check 3: Remaining print statements
        self._check_remaining_prints(content, results)
        
        # Check 4: Log level appropriateness
        self._check_log_levels(content, results)
        
        # Check 5: Metadata structure
        self._check_metadata_structure(content, results)
        
        # Check 6: Exception handling
        self._check_exception_handling(content, results)
        
        # Check 7: Syntax validation
        self._check_syntax(content, results)
        
        return results
    
    def _check_imports(self, content: str, results: Dict):
        """Check for proper event framework imports"""
        has_gui_import = bool(re.search(r'from unhinged_events import.*create_gui_logger', content))
        has_service_import = bool(re.search(r'from unhinged_events import.*create_service_logger', content))
        has_any_event_import = bool(re.search(r'from unhinged_events import', content))
        
        # Check if file uses event logging but missing imports
        uses_event_logging = bool(re.search(r'gui_logger\.|event_logger\.', content))
        
        if uses_event_logging and not has_any_event_import:
            results["issues"].append({
                "type": "missing_import",
                "severity": "error",
                "message": "File uses event logging but missing unhinged_events import"
            })
            results["compliance_score"] -= 20
        
        # Suggest appropriate import type
        if has_any_event_import:
            if 'gui' in str(results["file"]).lower() and not has_gui_import:
                results["suggestions"].append({
                    "type": "import_optimization",
                    "message": "Consider using create_gui_logger for GUI components"
                })
    
    def _check_logger_initialization(self, content: str, results: Dict):
        """Check for proper logger initialization"""
        has_gui_logger = bool(re.search(r'gui_logger = create_gui_logger\(', content))
        has_event_logger = bool(re.search(r'event_logger = create_service_logger\(', content))
        
        uses_logging = bool(re.search(r'\.info\(|\.debug\(|\.warn\(|\.error\(', content))
        
        if uses_logging and not (has_gui_logger or has_event_logger):
            results["issues"].append({
                "type": "missing_logger_init",
                "severity": "error", 
                "message": "File uses logging methods but no logger initialization found"
            })
            results["compliance_score"] -= 15
    
    def _check_remaining_prints(self, content: str, results: Dict):
        """Check for remaining print statements that should be migrated"""
        print_statements = re.findall(r'print\([^)]*\)', content)
        
        if print_statements:
            # Filter out acceptable prints (like in __main__ blocks or debug utilities)
            problematic_prints = []
            for print_stmt in print_statements:
                # Skip prints in main blocks or test utilities
                if not self._is_acceptable_print(print_stmt, content):
                    problematic_prints.append(print_stmt)
            
            if problematic_prints:
                results["warnings"].append({
                    "type": "remaining_prints",
                    "count": len(problematic_prints),
                    "message": f"Found {len(problematic_prints)} print statements that should be migrated",
                    "examples": problematic_prints[:3]
                })
                results["compliance_score"] -= min(len(problematic_prints) * 2, 20)
    
    def _is_acceptable_print(self, print_stmt: str, content: str) -> bool:
        """Check if a print statement is acceptable (e.g., in main block)"""
        # Simple heuristic: if it's in a main block or test function
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if print_stmt.replace(' ', '') in line.replace(' ', ''):
                # Check surrounding context
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 5)
                context = '\n'.join(lines[context_start:context_end])
                
                if ('if __name__ == "__main__"' in context or 
                    'def test_' in context or
                    'def main(' in context):
                    return True
        return False
    
    def _check_log_levels(self, content: str, results: Dict):
        """Check if log levels are appropriate for message content"""
        # Find all logging calls
        logging_calls = re.findall(r'(gui_logger|event_logger)\.(debug|info|warn|error)\([^)]*"([^"]*)"', content)
        
        inappropriate_levels = []
        for logger, level, message in logging_calls:
            expected_level = self._suggest_log_level(message)
            if expected_level and expected_level != level:
                inappropriate_levels.append({
                    "current": level,
                    "suggested": expected_level,
                    "message": message[:50] + "..." if len(message) > 50 else message
                })
        
        if inappropriate_levels:
            results["suggestions"].extend([{
                "type": "log_level_optimization",
                "message": f"Consider changing '{item['current']}' to '{item['suggested']}' for: {item['message']}"
            } for item in inappropriate_levels[:3]])  # Limit to 3 suggestions
    
    def _suggest_log_level(self, message: str) -> Optional[str]:
        """Suggest appropriate log level based on message content"""
        message_lower = message.lower()
        
        # Error indicators
        if any(word in message_lower for word in ['error', 'failed', 'exception', 'crash', '❌']):
            return 'error'
        
        # Warning indicators  
        if any(word in message_lower for word in ['warning', 'warn', 'deprecated', 'fallback', '⚠️']):
            return 'warn'
        
        # Debug indicators
        if any(word in message_lower for word in ['debug', 'trace', 'testing', 'initializing', '🔧']):
            return 'debug'
        
        # Success/info indicators (default)
        if any(word in message_lower for word in ['success', 'completed', 'started', 'ready', '✅', '🚀']):
            return 'info'
        
        return None
    
    def _check_metadata_structure(self, content: str, results: Dict):
        """Check if metadata follows structured format"""
        # Find logging calls with metadata
        metadata_calls = re.findall(r'(gui_logger|event_logger)\.\w+\([^,]+,\s*({[^}]+})', content)
        
        for logger, metadata_str in metadata_calls:
            try:
                # Basic validation of metadata structure
                if 'event_type' not in metadata_str:
                    results["suggestions"].append({
                        "type": "metadata_enhancement",
                        "message": "Consider adding 'event_type' to metadata for better categorization"
                    })
                    break  # Only suggest once per file
            except:
                pass  # Skip malformed metadata
    
    def _check_exception_handling(self, content: str, results: Dict):
        """Check if exceptions are properly logged"""
        # Find try-except blocks
        try_blocks = re.findall(r'try:.*?except[^:]*:(.*?)(?=\n\s*(?:except|finally|else|\S))', content, re.DOTALL)
        
        for block in try_blocks:
            if 'error(' not in block and 'exception' in block.lower():
                results["suggestions"].append({
                    "type": "exception_logging",
                    "message": "Consider using logger.error() with exception parameter in exception handlers"
                })
                break  # Only suggest once per file
    
    def _check_syntax(self, content: str, results: Dict):
        """Check if the migrated code has valid Python syntax"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            results["issues"].append({
                "type": "syntax_error",
                "severity": "error",
                "message": f"Syntax error at line {e.lineno}: {e.msg}",
                "line": e.lineno
            })
            results["compliance_score"] -= 50
    
    def validate_directory(self, directory: Path) -> Dict[str, any]:
        """Validate all Python files in a directory"""
        summary = {
            "total_files": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "total_warnings": 0,
            "average_compliance": 0,
            "file_results": []
        }
        
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            result = self.validate_file(py_file)
            summary["file_results"].append(result)
            summary["total_files"] += 1
            
            if result.get("issues") or result.get("warnings"):
                summary["files_with_issues"] += 1
            
            summary["total_issues"] += len(result.get("issues", []))
            summary["total_warnings"] += len(result.get("warnings", []))
        
        if summary["total_files"] > 0:
            total_compliance = sum(r.get("compliance_score", 100) for r in summary["file_results"])
            summary["average_compliance"] = total_compliance / summary["total_files"]
        
        return summary
    
    def generate_report(self, validation_results: Dict) -> str:
        """Generate a comprehensive validation report"""
        report = f"""
# Migration Validation Report

## Summary
- **Total files validated:** {validation_results['total_files']}
- **Files with issues:** {validation_results['files_with_issues']}
- **Total issues found:** {validation_results['total_issues']}
- **Total warnings:** {validation_results['total_warnings']}
- **Average compliance score:** {validation_results['average_compliance']:.1f}%

## Compliance Rating
"""
        
        if validation_results['average_compliance'] >= 95:
            report += "🟢 **EXCELLENT** - Migration meets high quality standards\n"
        elif validation_results['average_compliance'] >= 85:
            report += "🟡 **GOOD** - Migration is solid with minor improvements needed\n"
        elif validation_results['average_compliance'] >= 70:
            report += "🟠 **FAIR** - Migration needs attention in several areas\n"
        else:
            report += "🔴 **POOR** - Migration requires significant improvements\n"
        
        # Top issues
        if validation_results['total_issues'] > 0:
            report += "\n## Critical Issues to Address\n"
            issue_count = 0
            for file_result in validation_results['file_results']:
                for issue in file_result.get('issues', []):
                    if issue_count < 10:  # Limit to top 10 issues
                        report += f"- **{Path(file_result['file']).name}**: {issue['message']}\n"
                        issue_count += 1
        
        # Suggestions
        suggestion_count = 0
        suggestions_added = set()
        report += "\n## Improvement Suggestions\n"
        for file_result in validation_results['file_results']:
            for suggestion in file_result.get('suggestions', []):
                if suggestion_count < 5 and suggestion['message'] not in suggestions_added:
                    report += f"- {suggestion['message']}\n"
                    suggestions_added.add(suggestion['message'])
                    suggestion_count += 1
        
        return report

def main():
    """Main validation script"""
    if len(sys.argv) < 2:
        print("Usage: python3 validate_migration.py <directory_to_validate>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)
    
    print(f"🔍 Validating migration in: {directory}")
    
    validator = MigrationValidator(directory.parent)
    results = validator.validate_directory(directory)
    
    report = validator.generate_report(results)
    print(report)
    
    # Save report to file
    report_file = directory / "migration_validation_report.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if results['average_compliance'] >= 85:
        print("✅ Migration validation passed!")
        sys.exit(0)
    else:
        print("⚠️ Migration validation found issues that should be addressed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
