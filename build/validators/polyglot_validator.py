#!/usr/bin/env python3
"""
@llm-type validation-system
@llm-legend Polyglot validation system for enforcing Unhinged codebase patterns and cultural commandments
@llm-key Modular, parallel validation runner that checks file patterns, build structure, and cultural compliance across all languages
@llm-map Central validation orchestrator that coordinates language-specific validators and pattern checkers
@llm-axiom All validation must be fast, parallel, actionable, and educational
@llm-contract Provides unified validation interface with detailed reporting and optional auto-fixing
@llm-token polyglot-validator: Comprehensive codebase pattern enforcement and validation system

Polyglot Validation System for Unhinged Monorepo

Provides comprehensive validation of:
- File creation patterns and locations
- Build system structure and compliance
- Cultural commandments (independence, centralization)
- Language-specific patterns and conventions
- Generated content management
- Documentation standards (llm-docs)

Designed for parallel execution and actionable feedback.
"""

import os
import sys
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import json
import time

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """
    @llm-type data-model
    @llm-legend Result from a validation check with severity, location, and fix suggestions
    @llm-key Structured validation result that provides actionable feedback to developers
    """
    validator_name: str
    severity: str  # ERROR, WARNING, INFO
    message: str
    file_path: Optional[Path] = None
    line_number: Optional[int] = None
    fix_suggestion: Optional[str] = None
    auto_fixable: bool = False
    category: str = "general"  # pattern, cultural, build, docs, etc.

@dataclass
class ValidationSummary:
    """
    @llm-type data-model
    @llm-legend Summary of all validation results with metrics and categorization
    @llm-key Comprehensive validation report for build system integration
    """
    total_files_checked: int
    total_violations: int
    errors: int
    warnings: int
    infos: int
    duration_seconds: float
    results_by_category: Dict[str, List[ValidationResult]]
    auto_fixable_count: int

class BaseValidator(ABC):
    """
    @llm-type interface
    @llm-legend Abstract base class for all validators in the polyglot system
    @llm-key Defines common interface for pattern validation, cultural checks, and language-specific rules
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def validate(self) -> List[ValidationResult]:
        """Run validation and return results"""
        pass
    
    @abstractmethod
    def can_auto_fix(self) -> bool:
        """Whether this validator can automatically fix issues"""
        pass
    
    async def auto_fix(self) -> List[ValidationResult]:
        """Attempt to automatically fix issues (if supported)"""
        return []
    
    def get_file_patterns(self) -> List[str]:
        """Get file patterns this validator should check"""
        return ["*"]

class FilePatternValidator(BaseValidator):
    """
    @llm-type validator
    @llm-legend Validates file creation patterns and prevents scattered cruft
    @llm-key Checks for forbidden files in root, scattered build files, and proper directory usage
    """
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        # Check for forbidden files in root
        forbidden_patterns = ["*.py", "*.js", "*.ts", "*.sh", "demo_*", "test_*", "*.backup*", "*_temp*"]
        allowed_root_files = {
            "requirements.txt", "Makefile", "README.md", "build-config.yml", 
            ".gitignore", "LICENSE", "CHANGELOG.md"
        }
        
        for pattern in forbidden_patterns:
            for match in self.repo_root.glob(pattern):
                if match.is_file() and match.name not in allowed_root_files:
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="ERROR",
                        message=f"Forbidden file in root directory",
                        file_path=match,
                        fix_suggestion=f"Move to appropriate subdirectory or remove",
                        auto_fixable=False,
                        category="pattern"
                    ))
        
        # Check for scattered build files
        await self._check_scattered_build_files(results)
        
        # Check for backup and temp files
        await self._check_backup_files(results)
        
        return results
    
    async def _check_scattered_build_files(self, results: List[ValidationResult]):
        """Check for build files outside designated areas"""
        scattered_files = {
            "gradlew": "Use centralized build system",
            "gradlew.bat": "Use centralized build system", 
            "package.json": "Use centralized npm management",
            "package-lock.json": "Use centralized npm management",
            "build.gradle": "Use centralized Gradle management",
            "build.gradle.kts": "Use centralized Gradle management"
        }
        
        # Allow in specific service directories but warn
        allowed_dirs = {"platforms", "libs", "services"}
        
        for root, dirs, files in os.walk(self.repo_root):
            rel_path = Path(root).relative_to(self.repo_root)
            
            # Skip build and generated directories
            if any(part in str(rel_path) for part in ["build", "generated", ".git", "venv"]):
                continue
            
            for file in files:
                if file in scattered_files:
                    severity = "WARNING" if any(allowed in str(rel_path) for allowed in allowed_dirs) else "ERROR"
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity=severity,
                        message=f"Scattered build file: {file}",
                        file_path=Path(root) / file,
                        fix_suggestion=scattered_files[file],
                        auto_fixable=False,
                        category="build"
                    ))
    
    async def _check_backup_files(self, results: List[ValidationResult]):
        """Check for backup and temporary files"""
        backup_patterns = ["*.backup", "*.old", "*.tmp", "*~", "*.bak"]
        
        for pattern in backup_patterns:
            for match in self.repo_root.rglob(pattern):
                if ".git" not in str(match) and "venv" not in str(match):
                    results.append(ValidationResult(
                        validator_name=self.name,
                        severity="WARNING",
                        message=f"Backup/temp file found",
                        file_path=match,
                        fix_suggestion="Remove backup file, use git for version control",
                        auto_fixable=True,
                        category="pattern"
                    ))
    
    def can_auto_fix(self) -> bool:
        return True
    
    async def auto_fix(self) -> List[ValidationResult]:
        """Remove backup files automatically"""
        fixed = []
        backup_patterns = ["*.backup", "*.old", "*.tmp", "*~", "*.bak"]
        
        for pattern in backup_patterns:
            for match in self.repo_root.rglob(pattern):
                if ".git" not in str(match) and "venv" not in str(match):
                    try:
                        match.unlink()
                        fixed.append(ValidationResult(
                            validator_name=self.name,
                            severity="INFO",
                            message=f"Removed backup file",
                            file_path=match,
                            category="fix"
                        ))
                    except Exception as e:
                        fixed.append(ValidationResult(
                            validator_name=self.name,
                            severity="ERROR",
                            message=f"Failed to remove backup file: {e}",
                            file_path=match,
                            category="fix"
                        ))
        
        return fixed

class CulturalValidator(BaseValidator):
    """
    @llm-type validator
    @llm-legend Validates cultural commandments like independence and self-containment
    @llm-key Checks for external browser dependencies, WebKit usage, and independence violations
    """
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        # Check for browser dependencies
        browser_indicators = ["firefox", "chrome", "safari", "webkit", "chromium", "selenium", "playwright"]
        
        for root, dirs, files in os.walk(self.repo_root):
            if any(skip in root for skip in [".git", "venv", "__pycache__"]):
                continue
            
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".yml", ".yaml")):
                    file_path = Path(root) / file
                    
                    # Skip enforcement files that legitimately mention browsers
                    if any(skip in file.lower() for skip in ["enforcement", "cultural", "validator"]):
                        continue
                    
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore').lower()
                        for indicator in browser_indicators:
                            if indicator in content:
                                results.append(ValidationResult(
                                    validator_name=self.name,
                                    severity="ERROR",
                                    message=f"Browser dependency detected: {indicator}",
                                    file_path=file_path,
                                    fix_suggestion="Remove external browser dependency, use native rendering",
                                    auto_fixable=False,
                                    category="cultural"
                                ))
                                break
                    except Exception:
                        continue
        
        return results
    
    def can_auto_fix(self) -> bool:
        return False

class GeneratedContentValidator(BaseValidator):
    """
    @llm-type validator
    @llm-legend Validates that generated content is properly located in /generated/
    @llm-key Checks for proto-generated files, build artifacts, and other generated content outside /generated/
    """
    
    async def validate(self) -> List[ValidationResult]:
        results = []
        
        # Generated file patterns
        generated_patterns = ["*_pb2.py", "*_pb2_grpc.py", "*.pb.go", "*_grpc.pb.go"]
        
        for pattern in generated_patterns:
            for match in self.repo_root.rglob(pattern):
                rel_path = match.relative_to(self.repo_root)
                
                # Skip if already in generated directory
                if str(rel_path).startswith("generated/"):
                    continue
                
                # Skip venv and git
                if any(part in str(rel_path) for part in ["venv", ".git", "__pycache__"]):
                    continue
                
                results.append(ValidationResult(
                    validator_name=self.name,
                    severity="WARNING",
                    message=f"Generated file outside /generated/",
                    file_path=match,
                    fix_suggestion="Move to /generated/ directory or regenerate properly",
                    auto_fixable=False,
                    category="generated"
                ))
        
        return results
    
    def can_auto_fix(self) -> bool:
        return False

class PolyglotValidationRunner:
    """
    @llm-type orchestrator
    @llm-legend Main validation runner that coordinates all validators in parallel
    @llm-key Executes validation checks concurrently and provides comprehensive reporting
    """
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.validators: List[BaseValidator] = []
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register all default validators"""
        self.validators = [
            FilePatternValidator(self.repo_root),
            CulturalValidator(self.repo_root),
            GeneratedContentValidator(self.repo_root),
        ]

        # Try to register language-specific validators
        try:
            from .python_validator import PythonValidator, PythonFormatterValidator
            self.validators.extend([
                PythonValidator(self.repo_root),
                PythonFormatterValidator(self.repo_root)
            ])
        except ImportError:
            pass

        try:
            from .kotlin_validator import KotlinValidator
            self.validators.append(KotlinValidator(self.repo_root))
        except ImportError:
            pass
    
    def register_validator(self, validator: BaseValidator):
        """Register a custom validator"""
        self.validators.append(validator)
    
    async def run_validation(self, auto_fix: bool = False) -> ValidationSummary:
        """
        @llm-type function
        @llm-legend Run all validators in parallel and return comprehensive summary
        @llm-key Main entry point for validation system with optional auto-fixing
        """
        start_time = time.time()
        all_results = []
        
        # Run validators in parallel
        tasks = []
        for validator in self.validators:
            tasks.append(self._run_validator(validator, auto_fix))
        
        validator_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for results in validator_results:
            all_results.extend(results)
        
        # Calculate summary
        duration = time.time() - start_time
        summary = self._create_summary(all_results, duration)
        
        return summary
    
    async def _run_validator(self, validator: BaseValidator, auto_fix: bool) -> List[ValidationResult]:
        """Run a single validator with optional auto-fix"""
        results = await validator.validate()
        
        if auto_fix and validator.can_auto_fix():
            fix_results = await validator.auto_fix()
            results.extend(fix_results)
        
        return results
    
    def _create_summary(self, results: List[ValidationResult], duration: float) -> ValidationSummary:
        """Create validation summary from results"""
        errors = sum(1 for r in results if r.severity == "ERROR")
        warnings = sum(1 for r in results if r.severity == "WARNING")
        infos = sum(1 for r in results if r.severity == "INFO")
        auto_fixable = sum(1 for r in results if r.auto_fixable)
        
        # Group by category
        by_category = {}
        for result in results:
            category = result.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        return ValidationSummary(
            total_files_checked=len(set(r.file_path for r in results if r.file_path)),
            total_violations=len(results),
            errors=errors,
            warnings=warnings,
            infos=infos,
            duration_seconds=duration,
            results_by_category=by_category,
            auto_fixable_count=auto_fixable
        )

async def main():
    """
    @llm-type function
    @llm-legend Main entry point for polyglot validation system
    @llm-key Command-line interface for running validation with reporting
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Unhinged Polyglot Validation System")
    parser.add_argument("--auto-fix", action="store_true", help="Automatically fix issues where possible")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")
    
    args = parser.parse_args()
    
    runner = PolyglotValidationRunner(args.repo_root)
    summary = await runner.run_validation(auto_fix=args.auto_fix)
    
    if args.format == "json":
        # Convert to JSON-serializable format
        json_summary = {
            "total_files_checked": summary.total_files_checked,
            "total_violations": summary.total_violations,
            "errors": summary.errors,
            "warnings": summary.warnings,
            "infos": summary.infos,
            "duration_seconds": summary.duration_seconds,
            "auto_fixable_count": summary.auto_fixable_count
        }
        print(json.dumps(json_summary, indent=2))
    else:
        # Text format
        print(f"🔍 Polyglot Validation Results")
        print(f"=" * 50)
        print(f"Files checked: {summary.total_files_checked}")
        print(f"Total violations: {summary.total_violations}")
        print(f"Errors: {summary.errors}")
        print(f"Warnings: {summary.warnings}")
        print(f"Auto-fixable: {summary.auto_fixable_count}")
        print(f"Duration: {summary.duration_seconds:.2f}s")
        
        if summary.total_violations > 0:
            print(f"\n📋 Violations by Category:")
            for category, results in summary.results_by_category.items():
                print(f"\n{category.upper()}: {len(results)} issues")
                for result in results[:5]:  # Show first 5
                    icon = "❌" if result.severity == "ERROR" else "⚠️" if result.severity == "WARNING" else "ℹ️"
                    print(f"  {icon} {result.message}")
                    if result.file_path:
                        print(f"     📁 {result.file_path}")
                    if result.fix_suggestion:
                        print(f"     💡 {result.fix_suggestion}")
                if len(results) > 5:
                    print(f"     ... and {len(results) - 5} more")
    
    # Exit with error code if there are errors
    sys.exit(1 if summary.errors > 0 else 0)

if __name__ == "__main__":
    asyncio.run(main())
