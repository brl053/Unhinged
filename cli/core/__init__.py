"""Core CLI infrastructure for Unhinged.

This module provides the main Click application and shared utilities
for all CLI commands across the project.
"""

from cli.core.app import cli

__all__ = ["cli"]
__version__ = "0.1.0"
