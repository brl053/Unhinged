#!/usr/bin/env python3
"""
@llm-type util.validator
@llm-does python-specific validation for code quality, imports, and
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from ..validators.polyglot_validator import BaseValidator, ValidationResult

class PythonValidator(BaseValidator):
    """
@llm-type util.validator
@llm-does python-specific validation for code quality and unhinged
"""
    
    def get_file_patterns(self) -> List[str]:
        return ["*.py"]
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        # Find all Python files
        for py_file in self.repo_root.rglob("*.py"):
            # Skip venv, __pycache__, .git
            if any(skip in str(py_file) for skip in ["venv", "__pycache__", ".git"]):
                continue
            
            await self._validate_python_file(py_file, results)
        
        return results
    
    async def _validate_python_file(self, file_path: Path, results: List[ValidationResult]):
        """Validate a single Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Check for Flask usage (should be removed)
            await self._check_flask_usage(file_path, content, results)

            # Check for health.proto implementation in services
            if "services/" in str(file_path) and file_path.name in ["main.py", "grpc_server.py"]:
                await self._check_health_proto_implementation(file_path, content, results)

            # Existing validations...
            await self._validate_existing_patterns(file_path, content, results)

        except Exception as e:
            results.append(ValidationResult(
                file_path=str(file_path),
                line_number=1,
                severity="ERROR",
                message=f"Failed to validate Python file: {e}",
                rule="python-file-validation"
            ))

    async def _check_flask_usage(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Check for forbidden Flask usage"""
        flask_patterns = [
            r"from flask import",
            r"import flask",
            r"Flask\(",
            r"@app\.route",
            r"app\.run\("
        ]

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in flask_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    results.append(ValidationResult(
                        file_path=str(file_path),
                        line_number=line_num,
                        severity="ERROR",
                        message=f"Flask usage detected: {line.strip()}. Use gRPC with health.proto instead.",
                        rule="no-flask-usage"
                    ))

    async def _check_health_proto_implementation(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Check for proper health.proto implementation in services"""
        if "grpc_server.py" in str(file_path):
            # Check for health.proto imports
            if "health_pb2" not in content:
                results.append(ValidationResult(
                    file_path=str(file_path),
                    line_number=1,
                    severity="ERROR",
                    message="gRPC server must import health_pb2 for health.proto implementation",
                    rule="health-proto-import"
                ))

            # Check for HealthService implementation
            if "HealthServiceServicer" not in content:
                results.append(ValidationResult(
                    file_path=str(file_path),
                    line_number=1,
                    severity="ERROR",
                    message="gRPC server must implement HealthServiceServicer",
                    rule="health-service-implementation"
                ))

            # Check for Heartbeat method
            if "def Heartbeat(" not in content:
                results.append(ValidationResult(
                    file_path=str(file_path),
                    line_number=1,
                    severity="ERROR",
                    message="gRPC server must implement Heartbeat() method",
                    rule="heartbeat-method"
                ))

            # Check for Diagnostics method
            if "def Diagnostics(" not in content:
                results.append(ValidationResult(
                    file_path=str(file_path),
                    line_number=1,
                    severity="WARNING",
                    message="gRPC server should implement Diagnostics() method",
                    rule="diagnostics-method"
                ))

    async def _validate_existing_patterns(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Validate existing Python patterns (llm-docs, imports, etc.)"""
        # Check for llm-docs compliance
        await self._check_llm_docs(file_path, content, results)

        # Check for proper imports
        await self._check_imports(file_path, content, results)

        # Check for centralized environment usage
        await self._check_environment_usage(file_path, content, results)

        # Parse AST for deeper analysis
        try:
            tree = ast.parse(content)
            await self._check_ast_patterns(file_path, tree, results)
        except SyntaxError as e:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="ERROR",
                message=f"Python syntax error: {e}",
                file_path=file_path,
                line_number=e.lineno,
                fix_suggestion="Fix Python syntax error",
                category="python"
            ))
    
    async def _check_llm_docs(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Check for proper llm-docs comment standard"""
        # Skip __init__.py and test files for now
        if file_path.name in ["__init__.py"] or "test" in file_path.name:
            return
        
        # Check for llm-docs comments
        has_llm_type = "@llm-type" in content
        has_llm_does = "@llm-does" in content
        
        if not has_llm_type and len(content.strip()) > 100:  # Only for substantial files
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message="Missing @llm-type documentation",
                file_path=file_path,
                fix_suggestion="Add @llm-type comment to describe file purpose",
                category="docs"
            ))
        
        if has_llm_type and not has_llm_does:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message="Has @llm-type but missing @llm-does",
                file_path=file_path,
                fix_suggestion="Add @llm-does comment to describe functionality",
                category="docs"
            ))
    
    async def _check_imports(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Check for problematic imports"""
        lines = content.split('\n')
        
        # Check for browser-related imports
        browser_imports = ["selenium", "playwright", "webdriver", "webkit"]
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if line_stripped.startswith(("import ", "from ")):
                for browser_import in browser_imports:
                    if browser_import in line_stripped.lower():
                        results.append(ValidationResult(
                            validator_name=self.name,
                            severity="ERROR",
                            message=f"Browser-related import detected: {browser_import}",
                            file_path=file_path,
                            line_number=i,
                            fix_suggestion="Remove browser dependency, use native alternatives",
                            category="cultural"
                        ))
    
    async def _check_environment_usage(self, file_path: Path, content: str, results: List[ValidationResult]):
        """Check for proper centralized environment usage"""
        # Check for subprocess calls that might bypass centralized Python
        if "subprocess" in content and "python" in content.lower():
            # Look for direct python calls instead of centralized environment
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if "subprocess" in line and re.search(r'\bpython[23]?\b', line, re.IGNORECASE):
                    if "build/python/venv" not in line:
                        results.append(ValidationResult(
                            validator_name=self.name,
                            severity="WARNING",
                            message="Direct Python subprocess call detected",
                            file_path=file_path,
                            line_number=i,
                            fix_suggestion="Use centralized Python environment: build/python/venv/bin/python",
                            category="build"
                        ))
    
    async def _check_ast_patterns(self, file_path: Path, tree: ast.AST, results: List[ValidationResult]):
        """Check AST for problematic patterns"""
        for node in ast.walk(tree):
            # Check for hardcoded paths that should be configurable
            if isinstance(node, ast.Str) and hasattr(node, 's'):
                if "/tmp/" in node.s or "/var/tmp/" in node.s:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="WARNING",
                        message="Hardcoded temp path detected",
                        file_path=file_path,
                        line_number=getattr(node, 'lineno', None),
                        fix_suggestion="Use generated/ directory or configurable temp path",
                        category="pattern"
                    ))
    
    def can_auto_fix(self) -> bool:
        return False  # Python auto-fixing is complex, leave for now

class PythonFormatterValidator(BaseValidator):
    """
@llm-type util.validator
@llm-does python code formatting validation using black and
"""
    
    def get_file_patterns(self) -> List[str]:
        return ["*.py"]
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        try:
            import black
            import isort
        except ImportError:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message="Python formatting tools not available (black, isort)",
                fix_suggestion="Install black and isort in centralized Python environment",
                category="tools"
            ))
            return results
        
        # Check formatting for Python files
        for py_file in self.repo_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ["venv", "__pycache__", ".git"]):
                continue
            
            await self._check_formatting(py_file, results)
        
        return results
    
    async def _check_formatting(self, file_path: Path, results: List[ValidationResult]):
        """Check if Python file is properly formatted"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Check black formatting
            try:
                import black
                formatted = black.format_str(content, mode=black.FileMode())
                if formatted != content:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="WARNING",
                        message="Python file not formatted with black",
                        file_path=file_path,
                        fix_suggestion="Run black formatter",
                        auto_fixable=True,
                        category="formatting"
                    ))
            except Exception:
                pass  # Skip if black fails
            
            # Check isort formatting
            try:
                import isort
                sorted_imports = isort.code(content)
                if sorted_imports != content:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="WARNING",
                        message="Python imports not sorted with isort",
                        file_path=file_path,
                        fix_suggestion="Run isort formatter",
                        auto_fixable=True,
                        category="formatting"
                    ))
            except Exception:
                pass  # Skip if isort fails
                
        except Exception as e:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message=f"Could not check formatting: {e}",
                file_path=file_path,
                category="formatting"
            ))
    
    def can_auto_fix(self) -> bool:
        return True
    
    async def auto_fix(self) -> List[ValidationResult]:
        """Auto-fix Python formatting issues"""
        fixed = []
        
        try:
            import black
            import isort
        except ImportError:
            return fixed
        
        for py_file in self.repo_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ["venv", "__pycache__", ".git"]):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # Apply black formatting
                try:
                    content = black.format_str(content, mode=black.FileMode())
                except Exception:
                    pass
                
                # Apply isort formatting
                try:
                    content = isort.code(content)
                except Exception:
                    pass
                
                # Write back if changed
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    fixed.append(ValidationResult(
                        validator_name=self.name,
                        severity="INFO",
                        message="Applied Python formatting",
                        file_path=py_file,
                        category="fix"
                    ))
                    
            except Exception as e:
                fixed.append(ValidationResult(
                    validator_name=self.name,
                    severity="ERROR",
                    message=f"Failed to format Python file: {e}",
                    file_path=py_file,
                    category="fix"
                ))
        
        return fixed
