#!/usr/bin/env python3

"""
@llm-type build-script
@llm-legend Simple script to generate static HTML registry for make start command
@llm-key Standalone script that calls registry builder without complex build system dependencies
@llm-map Entry point for Makefile to generate registry before control plane startup
@llm-axiom Must work independently of build system for simple make start workflow
@llm-contract Exits with 0 on success, 1 on failure for make integration
@llm-token registry-generator: Simple registry generation script for make start

Registry Generation Script

Simple standalone script that generates the static HTML registry
without requiring the full build system infrastructure.

Usage:
    python3 build/generate-registry.py

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from modules.registry_builder import RegistryBuilder
    
    # Simple context class
    class SimpleContext:
        def __init__(self):
            self.project_root = Path(__file__).parent.parent
            self.target_name = 'generate-registry'
    
    # Generate registry
    print("🔍 Scanning control/static_html directory...")
    rb = RegistryBuilder()
    ctx = SimpleContext()
    result = rb.build(ctx)
    
    if result.success:
        print("✅ Registry generated successfully")
        print(f"📊 Scanned {result.metrics.get('files_scanned', 0)} HTML files")
        print(f"⚡ Completed in {result.duration:.3f}s")
        sys.exit(0)
    else:
        print(f"❌ Registry generation failed: {result.error_message}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
