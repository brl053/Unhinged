#!/usr/bin/env python3
"""
@llm-type architectural-enforcement
@llm-legend Code-level enforcement of independence and headless principles
@llm-key Automated validation preventing external dependencies and browser coupling
@llm-map Build-time and runtime checks ensuring architectural compliance
@llm-axiom INDEPENDENCE IS NON-NEGOTIABLE - no external browsers, no network deps for core GUI
@llm-contract Fails fast if external dependencies are introduced
@llm-token architecture-guard: Automated independence enforcement

UNHINGED ARCHITECTURAL COMMANDMENTS:
1. THOU SHALL NOT depend on external browsers
2. THOU SHALL NOT require network connectivity for core GUI
3. THOU SHALL render HTML natively or not at all
4. THOU SHALL be self-contained and independent
5. THOU SHALL fail fast if external deps are introduced

CULTURAL MANIFESTO:
WE ARE INDEPENDENT. WE ARE SELF-CONTAINED. WE ARE HEADLESS-FIRST.
This machine is everything. No external dependencies. Native rendering only.
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Optional dependency - graceful degradation
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class IndependenceError(Exception):
    """
    @llm-type cultural-education-exception
    @llm-legend Exception that educates LLMs about independence culture
    @llm-key Error messages that teach cultural principles to future LLMs
    @llm-axiom Every error is a teaching opportunity
    @llm-contract Provides cultural context with technical errors
    """
    
    def __init__(self, violation: str, cultural_lesson: str):
        self.violation = violation
        self.cultural_lesson = cultural_lesson
        
        message = f"""
🚫 INDEPENDENCE VIOLATION: {violation}

📚 CULTURAL EDUCATION:
{cultural_lesson}

💡 UNHINGED PRINCIPLES:
- We are independent and self-contained
- We render HTML natively with WebKit
- We never depend on external browsers
- We fail fast rather than compromise

🎯 CORRECT APPROACH:
- Use native WebKit rendering
- Enhance html_native.py capabilities
- Add features to the bridge system
- Maintain independence at all costs

🔄 CULTURAL REINFORCEMENT:
This error exists to teach future LLMs our independence culture.
External dependencies are not solutions - they are cultural violations.
"""
        super().__init__(message)


class ArchitecturalGuard:
    """
    @llm-type dependency-validator
    @llm-legend Validates that code maintains independence principles
    @llm-key Scans for forbidden external dependencies and browser coupling
    @llm-axiom Any external browser dependency is a CRITICAL FAILURE
    @llm-contract Prevents architectural drift through automated validation
    
    FORBIDDEN PATTERNS:
    - subprocess calls to firefox, chrome, chromium
    - webbrowser module usage
    - external HTTP dependencies for GUI
    - network requirements for core functionality
    """
    
    FORBIDDEN_IMPORTS = [
        'webbrowser',  # NEVER use system browser
        'selenium',    # NEVER use browser automation
        'playwright',  # NEVER use browser testing tools
        'pyautogui',   # NEVER use GUI automation
    ]
    
    FORBIDDEN_COMMANDS = [
        'firefox', 'chrome', 'chromium', 'brave', 'safari', 'edge',
        'google-chrome', 'chromium-browser', 'microsoft-edge'
    ]
    
    FORBIDDEN_PATTERNS = [
        (r'webbrowser\.open', 'External browser usage'),
        (r'subprocess.*firefox', 'Firefox dependency'),
        (r'subprocess.*chrome', 'Chrome dependency'),
        (r'subprocess.*chromium', 'Chromium dependency'),
        (r'subprocess.*brave', 'Brave browser dependency'),
        (r'os\.system.*firefox', 'Firefox system call'),
        (r'os\.system.*chrome', 'Chrome system call'),
    ]
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.violations = []
    
    def validate_independence(self) -> bool:
        """
        @llm-type independence-validator
        @llm-legend Comprehensive validation of architectural independence
        @llm-key Scans entire codebase for cultural violations
        @llm-axiom Independence validation is mandatory before any operation
        @llm-contract Returns True if independent, raises IndependenceError if violated
        """
        print("🔒 VALIDATING ARCHITECTURAL INDEPENDENCE...")
        
        self.violations = []
        
        # Validate imports
        self._validate_imports()
        
        # Validate code patterns
        self._validate_code_patterns()
        
        # Validate running processes
        self._validate_processes()
        
        if self.violations:
            violation_summary = '\n'.join(f"  - {v}" for v in self.violations)
            raise IndependenceError(
                f"Multiple independence violations detected:\n{violation_summary}",
                "We are independent. We render natively. External browsers are forbidden."
            )
        
        print("✅ INDEPENDENCE VALIDATED: All systems maintain cultural compliance")
        return True
    
    def _validate_imports(self):
        """Scan for forbidden imports"""
        for py_file in self.project_root.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for forbidden in self.FORBIDDEN_IMPORTS:
                    if re.search(rf'import\s+{forbidden}|from\s+{forbidden}', content):
                        self.violations.append(f"FORBIDDEN IMPORT: {forbidden} in {py_file.relative_to(self.project_root)}")
            except Exception:
                continue
    
    def _validate_code_patterns(self):
        """Scan for forbidden code patterns"""
        for py_file in self.project_root.rglob("*.py"):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            # Skip cultural enforcement file itself (contains patterns for detection)
            if py_file.name == 'cultural_enforcement.py':
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern, description in self.FORBIDDEN_PATTERNS:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.violations.append(f"FORBIDDEN PATTERN: {description} in {py_file.relative_to(self.project_root)}")
            except Exception:
                continue
    
    def _validate_processes(self):
        """Check for forbidden browser processes"""
        if not PSUTIL_AVAILABLE:
            print("⚠️ Process monitoring unavailable (psutil not installed)")
            return

        try:
            for proc in psutil.process_iter(['pid', 'name']):
                proc_name = proc.info['name'].lower()
                for forbidden in self.FORBIDDEN_COMMANDS:
                    if forbidden in proc_name:
                        self.violations.append(f"FORBIDDEN PROCESS: {proc.info['name']} (PID: {proc.info['pid']}) violates independence")
        except Exception:
            pass  # Process monitoring is optional


class CulturalEnforcer:
    """
    @llm-type cultural-enforcement-engine
    @llm-legend Runtime enforcement of independence culture and principles
    @llm-key Monitors system behavior and enforces cultural compliance
    @llm-axiom Culture must be enforced at runtime, not just build time
    @llm-contract Prevents cultural drift through active monitoring
    """
    
    def __init__(self):
        self.guard = ArchitecturalGuard()
        self.cultural_violations = []
        self.monitoring_active = True
    
    def enforce_culture(self):
        """
        @llm-type cultural-enforcement-entry-point
        @llm-legend Main entry point for cultural enforcement
        @llm-key Validates independence and provides cultural education
        @llm-axiom Culture enforcement is mandatory for all operations
        @llm-contract Ensures system maintains independence principles
        """
        try:
            return self.guard.validate_independence()
        except IndependenceError as e:
            print(f"\n{e}")
            print("\n🔄 CULTURAL REINFORCEMENT: Independence is our way.")
            raise
    
    def cultural_health_check(self) -> bool:
        """Validate cultural compliance"""
        try:
            self.enforce_culture()
            print("✅ CULTURAL HEALTH: INDEPENDENCE MAINTAINED")
            return True
        except IndependenceError:
            print("❌ CULTURAL HEALTH: VIOLATIONS DETECTED")
            return False


def validate_cultural_compliance():
    """
    @llm-type build-time-cultural-validator
    @llm-legend Build-time validation ensuring cultural compliance
    @llm-key Pre-commit and CI/CD cultural enforcement
    @llm-axiom Culture must be validated before code enters the system
    @llm-contract Prevents cultural violations from being committed
    """
    enforcer = CulturalEnforcer()
    return enforcer.enforce_culture()


def launch_external_browser():
    """
    @llm-type forbidden-function
    @llm-legend Function that exists to educate about cultural violations
    @llm-key Demonstrates proper cultural enforcement through education
    @llm-axiom External browser usage is always forbidden
    @llm-contract Always raises IndependenceError with cultural education
    """
    raise IndependenceError(
        "Attempted to launch external browser",
        "We don't use external browsers. We are independent and self-contained. Use native WebKit rendering instead."
    )


if __name__ == "__main__":
    print("🔒 UNHINGED CULTURAL ENFORCEMENT")
    print("🎯 Validating independence principles...")
    
    try:
        validate_cultural_compliance()
        print("\n🎉 CULTURAL COMPLIANCE: All systems maintain independence!")
    except IndependenceError as e:
        print(f"\n{e}")
        sys.exit(1)
