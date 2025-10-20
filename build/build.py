#!/usr/bin/env python3

"""
@llm-type service
@llm-legend Main entry point for the Unhinged build system (v1)
@llm-key Provides unified access to intelligent build orchestration with caching, parallelism, and AI assistance
@llm-map Primary build system entry point with clean v1 interface
@llm-axiom Build system must be simple, fast, and provide clear feedback
@llm-contract Provides clean v1 interface for all build operations
@llm-token build-v1: Main entry point for v1 build system

Unhinged Build System (v1)

Primary entry point for the consolidated build system with:
- Intelligent caching and parallel execution
- AI-powered development assistance
- Performance monitoring and optimization
- Clean, simple interface

Usage:
    python build/build.py build dev-fast        # Fast development build
    python build/build.py status                # Show build status
    python build/build.py list                  # List all targets
    python build/build.py explain dev-fast      # Explain build target

Author: Unhinged Team
Version: 1.0.0 (Consolidated)
Date: 2025-10-19
"""

import sys
import os
from pathlib import Path

# Add the build directory to Python path
build_dir = Path(__file__).parent
sys.path.insert(0, str(build_dir))

# Import v1 build system
try:
    from cli import BuildCLI, main as cli_main
    BUILD_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Build system not available: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install pyyaml psutil")
    BUILD_SYSTEM_AVAILABLE = False

def show_help():
    """Show help for v1 build system"""
    print("""
🚀 Unhinged Build System (v1)

USAGE:
    python build/build.py <command> [options]

CORE COMMANDS:
    build <targets...>     Build one or more targets
    status                 Show build system status
    list                   List available targets
    explain <target>       Explain what a target does
    clean [options]        Clean build artifacts
    watch <target>         Watch mode with auto-rebuild

AI-POWERED FEATURES:
    llm context           Generate AI context for development
    llm onboard           Generate developer onboarding guide
    llm explain-error     Get AI explanation for build errors

PERFORMANCE TOOLS:
    performance report    Generate performance report
    performance metrics   Show current performance metrics

KEY FEATURES:
    ⚡ Intelligent caching with content-based keys
    🔄 Parallel execution with dependency awareness
    📊 Build performance monitoring and metrics
    🧠 AI-powered development assistance
    🎯 Incremental builds for faster development

EXAMPLES:
    python build/build.py build dev-fast --parallel
    python build/build.py status
    python build/build.py explain dev-fast --dependencies
    python build/build.py watch backend-compile
    python build/build.py clean --smart

For more information, see: build/README.md
""")



def main():
    """Main entry point for v1 build system"""

    # Handle help requests
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']):
        show_help()
        return 0

    # Check if build system is available
    if not BUILD_SYSTEM_AVAILABLE:
        print("❌ Build system not available!")
        print("Please install dependencies: pip install pyyaml psutil")
        return 1

    try:
        # Map common commands for convenience
        args = sys.argv[1:]

        if len(args) >= 1:
            command = args[0]

            # Map convenient shortcuts to full commands
            if command == 'dev':
                # Convert 'dev' to 'build dev-fast'
                sys.argv = ['build.py', 'build', 'dev-fast', '--parallel']
            elif command == 'test':
                # Convert 'test' to 'build test-fast'
                sys.argv = ['build.py', 'build', 'test-fast', '--parallel']
            # For other commands, pass through to CLI

        return cli_main()

    except Exception as e:
        print(f"❌ Build system failed: {e}")
        print("Try running with --verbose for more details")
        return 1

if __name__ == '__main__':
    sys.exit(main())
