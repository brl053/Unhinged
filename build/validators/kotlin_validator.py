#!/usr/bin/env python3
"""
@llm-type util.validator
@llm-does kotlin-specific validation for build patterns and code
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from ..validators.polyglot_validator import BaseValidator, ValidationResult

class KotlinValidator(BaseValidator):
    """
@llm-type util.validator
@llm-does kotlin-specific validation for build patterns and code
"""
    
    def get_file_patterns(self) -> List[str]:
        return ["*.kt", "*.kts", "build.gradle*", "settings.gradle*"]
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        # Check Gradle build files
        await self._check_gradle_files(results)
        
        # Check Kotlin source files
        await self._check_kotlin_files(results)
        
        # Check package structure
        await self._check_package_structure(results)
        
        return results
    
    async def _check_gradle_files(self, results: List[ValidationResult]):
        """Check Gradle build files for proper patterns"""
        gradle_files = list(self.repo_root.rglob("build.gradle*")) + list(self.repo_root.rglob("settings.gradle*"))
        
        for gradle_file in gradle_files:
            # Skip if in allowed locations
            rel_path = gradle_file.relative_to(self.repo_root)
            
            # Allow in platforms/ and libs/ but warn about centralization
            if any(allowed in str(rel_path) for allowed in ["platforms/", "libs/"]):
                await self._validate_gradle_content(gradle_file, results, severity="WARNING")
            else:
                # Error if in other locations
                results.append(ValidationResult(
                    validator_name=self.name,
                    severity="ERROR",
                    message="Gradle build file in unexpected location",
                    file_path=gradle_file,
                    fix_suggestion="Move to platforms/ or libs/ directory, or integrate with centralized build",
                    category="build"
                ))
    
    async def _validate_gradle_content(self, gradle_file: Path, results: List[ValidationResult], severity: str = "WARNING"):
        """Validate content of Gradle build files"""
        try:
            content = gradle_file.read_text(encoding='utf-8')
            
            # Check for hardcoded versions
            version_patterns = [
                r'version\s*=\s*["\'][\d.]+["\']',
                r'implementation\s*["\'][^:]+:[\d.]+["\']'
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in version_patterns:
                    if re.search(pattern, line):
                        results.append(ValidationResult(
                            validator_name=self.name,
                            severity=severity,
                            message="Hardcoded version detected in Gradle file",
                            file_path=gradle_file,
                            line_number=i,
                            fix_suggestion="Use version catalog or centralized dependency management",
                            category="build"
                        ))
            
            # Check for proper proto integration
            if "protobuf" in content.lower():
                if "generated" not in content:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="WARNING",
                        message="Proto generation not configured to use /generated/ directory",
                        file_path=gradle_file,
                        fix_suggestion="Configure proto generation to output to /generated/kotlin/",
                        category="generated"
                    ))
            
            # Check for proper repository configuration
            if "repositories" in content:
                if "mavenCentral()" not in content and "gradlePluginPortal()" not in content:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="INFO",
                        message="Consider using standard repositories (mavenCentral, gradlePluginPortal)",
                        file_path=gradle_file,
                        fix_suggestion="Add mavenCentral() and gradlePluginPortal() repositories",
                        category="build"
                    ))
                    
        except Exception as e:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message=f"Could not validate Gradle file: {e}",
                file_path=gradle_file,
                category="build"
            ))
    
    async def _check_kotlin_files(self, results: List[ValidationResult]):
        """Check Kotlin source files for patterns"""
        for kt_file in self.repo_root.rglob("*.kt"):
            # Skip generated files
            if "generated" in str(kt_file) or "build/" in str(kt_file):
                continue
            
            await self._validate_kotlin_file(kt_file, results)
    
    async def _validate_kotlin_file(self, kt_file: Path, results: List[ValidationResult]):
        """Validate a single Kotlin file"""
        try:
            content = kt_file.read_text(encoding='utf-8')
            
            # Check package declaration
            await self._check_package_declaration(kt_file, content, results)
            
            # Check imports
            await self._check_kotlin_imports(kt_file, content, results)
            
            # Check for llm-docs compliance
            await self._check_kotlin_docs(kt_file, content, results)
            
        except Exception as e:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message=f"Could not validate Kotlin file: {e}",
                file_path=kt_file,
                category="kotlin"
            ))
    
    async def _check_package_declaration(self, kt_file: Path, content: str, results: List[ValidationResult]):
        """Check package declaration matches file structure"""
        lines = content.split('\n')
        package_line = None
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("package "):
                package_line = line.strip()
                break
        
        if not package_line:
            results.append(ValidationResult(
                validator_name=self.name,
                severity="WARNING",
                message="Missing package declaration",
                file_path=kt_file,
                fix_suggestion="Add package declaration matching directory structure",
                category="kotlin"
            ))
            return
        
        # Extract package name
        package_match = re.match(r'package\s+([a-zA-Z0-9_.]+)', package_line)
        if package_match:
            package_name = package_match.group(1)
            
            # Check if package matches directory structure
            rel_path = kt_file.relative_to(self.repo_root)
            expected_path_parts = package_name.split('.')
            
            # Simple check - package should somewhat match directory structure
            path_parts = str(rel_path.parent).split('/')
            if not any(part in path_parts for part in expected_path_parts[-2:]):  # Check last 2 parts
                results.append(ValidationResult(
                    validator_name=self.name,
                    severity="INFO",
                    message="Package declaration may not match directory structure",
                    file_path=kt_file,
                    fix_suggestion="Ensure package declaration matches directory structure",
                    category="kotlin"
                ))
    
    async def _check_kotlin_imports(self, kt_file: Path, content: str, results: List[ValidationResult]):
        """Check Kotlin imports for problematic patterns"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if line_stripped.startswith("import "):
                # Check for wildcard imports (generally discouraged)
                if line_stripped.endswith(".*"):
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="INFO",
                        message="Wildcard import detected",
                        file_path=kt_file,
                        line_number=i,
                        fix_suggestion="Consider explicit imports instead of wildcard",
                        category="kotlin"
                    ))
                
                # Check for browser-related imports
                browser_imports = ["webview", "webkit", "browser"]
                for browser_import in browser_imports:
                    if browser_import.lower() in line_stripped.lower():
                        results.append(ValidationResult(
                            validator_name=self.name,
                            severity="ERROR",
                            message=f"Browser-related import detected: {browser_import}",
                            file_path=kt_file,
                            line_number=i,
                            fix_suggestion="Remove browser dependency, use native alternatives",
                            category="cultural"
                        ))
    
    async def _check_kotlin_docs(self, kt_file: Path, content: str, results: List[ValidationResult]):
        """Check for proper documentation in Kotlin files"""
        # Check for KDoc comments on classes and functions
        lines = content.split('\n')
        
        class_pattern = re.compile(r'^\s*(class|interface|object)\s+\w+')
        function_pattern = re.compile(r'^\s*fun\s+\w+')
        
        for i, line in enumerate(lines):
            if class_pattern.match(line) or function_pattern.match(line):
                # Check if previous lines contain documentation
                has_doc = False
                for j in range(max(0, i-5), i):
                    if "/**" in lines[j] or "@llm-" in lines[j]:
                        has_doc = True
                        break
                
                if not has_doc and len(content) > 500:  # Only for substantial files
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="INFO",
                        message="Missing documentation for class/function",
                        file_path=kt_file,
                        line_number=i + 1,
                        fix_suggestion="Add KDoc or llm-docs comments",
                        category="docs"
                    ))
    
    async def _check_package_structure(self, results: List[ValidationResult]):
        """Check overall package structure"""
        kotlin_dirs = set()
        
        for kt_file in self.repo_root.rglob("*.kt"):
            if "generated" in str(kt_file) or "build/" in str(kt_file):
                continue
            kotlin_dirs.add(kt_file.parent)
        
        # Check for proper separation of concerns
        for kotlin_dir in kotlin_dirs:
            rel_path = kotlin_dir.relative_to(self.repo_root)
            
            # Check if Kotlin files are in appropriate locations
            if "src/main/kotlin" not in str(rel_path) and "src/test/kotlin" not in str(rel_path):
                if any(allowed in str(rel_path) for allowed in ["platforms/", "libs/"]):
                    continue  # Allow in designated areas
                
                results.append(ValidationResult(
                    validator_name=self.name,
                    severity="INFO",
                    message="Kotlin files not in standard Maven/Gradle structure",
                    file_path=kotlin_dir,
                    fix_suggestion="Consider using src/main/kotlin or src/test/kotlin structure",
                    category="structure"
                ))
    
    def can_auto_fix(self) -> bool:
        return False  # Kotlin auto-fixing is complex
