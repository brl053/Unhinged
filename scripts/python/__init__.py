"""
Unhinged Python Scripts Package

This package contains Python automation scripts for the Unhinged monorepo.
Python is the primary scripting language for new automation, with shell scripts
maintained for backward compatibility but considered legacy.

Philosophy:
- Japanese approach to development: intentional, high-quality work
- Precise "hand tools" rather than generic, scalable solutions
- Reusable and well-understood techniques
- LLM-oriented documentation with clear examples

Script Categories:
- Theme and Design System utilities
- Build system automation
- Development workflow tools
- Testing and validation scripts
- Deployment and maintenance utilities

Usage:
    python scripts/python/script_name.py [options]

Standards:
- All scripts should follow Python docstring conventions
- Include usage examples and parameter descriptions
- Maintain compatibility with existing build system
- Use type hints for better LLM understanding

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-06
"""

__version__ = "1.0.0"
__author__ = "Unhinged Team"

# Script registry for build system integration
PYTHON_SCRIPTS = {
    "fix_theme_properties": {
        "path": "scripts/python/fix_theme_properties.py",
        "description": "Fix theme property access patterns to match design system structure",
        "category": "theme",
        "usage": "python scripts/python/fix_theme_properties.py [--dry-run] [--pattern PATTERN] [--replacement REPLACEMENT]",
        "examples": [
            "python scripts/python/fix_theme_properties.py --dry-run",
            "python scripts/python/fix_theme_properties.py",
        ]
    },
    "analyze_migration": {
        "path": "scripts/python/analyze_migration.py",
        "description": "Analyze component migration metrics with precise LOC, design token coverage, and TypeScript safety scores",
        "category": "analysis",
        "usage": "python scripts/python/analyze_migration.py --component ComponentName [--compare] [--save]",
        "examples": [
            "python scripts/python/analyze_migration.py --component PromptSurgeryPanel --compare",
            "python scripts/python/analyze_migration.py --all-components --save",
            "python scripts/python/analyze_migration.py --component EventFeed --pre-migration",
        ]
    },
    # Future scripts will be registered here
}

# Legacy shell scripts (maintained for compatibility)
LEGACY_SHELL_SCRIPTS = {
    "add-version-headers": {
        "path": "scripts/add-version-headers.sh",
        "description": "Add version headers to files (LEGACY - consider Python migration)",
        "status": "legacy"
    },
    "health-check": {
        "path": "scripts/health-check.sh", 
        "description": "System health checks (LEGACY - consider Python migration)",
        "status": "legacy"
    },
    "start-cdc-system": {
        "path": "scripts/start-cdc-system.sh",
        "description": "Start CDC system (LEGACY - consider Python migration)", 
        "status": "legacy"
    },
    "test-cdc-e2e": {
        "path": "scripts/test-cdc-e2e.sh",
        "description": "CDC end-to-end tests (LEGACY - consider Python migration)",
        "status": "legacy"
    },
    "validate-generated": {
        "path": "scripts/validate-generated.sh",
        "description": "Validate generated files (LEGACY - consider Python migration)",
        "status": "legacy"
    },
    "version-manager": {
        "path": "scripts/version-manager.sh",
        "description": "Version management (LEGACY - consider Python migration)",
        "status": "legacy"
    }
}

def list_available_scripts():
    """List all available scripts (Python and legacy shell)."""
    print("🐍 Python Scripts (Primary):")
    for name, info in PYTHON_SCRIPTS.items():
        print(f"  {name}: {info['description']}")
        print(f"    Usage: {info['usage']}")
    
    print("\n🐚 Shell Scripts (Legacy):")
    for name, info in LEGACY_SHELL_SCRIPTS.items():
        print(f"  {name}: {info['description']}")

def get_script_info(script_name: str):
    """Get information about a specific script."""
    if script_name in PYTHON_SCRIPTS:
        return PYTHON_SCRIPTS[script_name]
    elif script_name in LEGACY_SHELL_SCRIPTS:
        return LEGACY_SHELL_SCRIPTS[script_name]
    else:
        return None
