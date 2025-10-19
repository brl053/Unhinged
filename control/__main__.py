#!/usr/bin/env python3

"""
@llm-type main-entry
@llm-legend Main entry point for control package execution
@llm-key Enables python -m control execution
@llm-map Package main entry that delegates to control.__init__.main()
@llm-axiom Package must be executable via python -m control
@llm-contract Provides command-line interface for control plane
@llm-token control-main: Main entry point for control package

Control Package Main Entry

Enables execution via:
- python -m control
- python -m control --test
- python -m control --sample

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

from . import main

if __name__ == "__main__":
    main()
