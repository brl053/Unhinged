#!/usr/bin/env python3
"""
@llm-type config.build
@llm-does defines data structures and interfaces for llm
"""

from typing import TypedDict, Optional, List, Dict, Literal
from dataclasses import dataclass
from pathlib import Path

# Supported languages for extraction
LanguageType = Literal["typescript", "python", "kotlin", "yaml", "javascript"]

# LLM tag names - Evolved 3-tag format
TagType = Literal[
    "llm_type",   # Hierarchical category (required)
    "llm_does",   # Action description (required)
    "llm_rule"    # Critical constraint (optional)
]

@dataclass
class LLMComment:
    """Single LLM comment with evolved 3-tag format."""
    file_path: str
    line_number: int
    language: LanguageType
    element_name: str = "unknown"
    type: Optional[str] = None      # @llm-type: hierarchical category
    does: Optional[str] = None      # @llm-does: action description
    rule: Optional[str] = None      # @llm-rule: critical constraint
    raw_comment: str = ""

class ExtractionResult(TypedDict):
    """Result of extracting comments from codebase."""
    comments: List[LLMComment]
    total_files_scanned: int
    files_with_comments: int
    extraction_timestamp: str

class ValidationIssue(TypedDict):
    """Single validation issue found."""
    file_path: str
    line_number: int
    issue_type: str
    message: str
    severity: Literal["error", "warning", "info"]

class ValidationResult(TypedDict):
    """Result of validating LLM comments."""
    issues: List[ValidationIssue]
    total_comments_validated: int
    passed: bool
    validation_timestamp: str

# Tag parsing patterns - Evolved 3-tag format
TAG_PATTERNS = {
    'llm_type': r'@llm-type\s+([^\n]+)',
    'llm_does': r'@llm-does\s+([^\n]+)',
    'llm_rule': r'@llm-rule\s+([^\n]+)'
}

# Required tags by element type - Evolved format
REQUIRED_TAGS = {
    'service': ['type', 'does'],
    'function': ['type', 'does'],
    'class': ['type', 'does'],
    'component': ['type', 'does'],
    'config': ['type', 'does'],
    'repository': ['type', 'does'],
    'endpoint': ['type', 'does'],
}

# Valid values for llm_type
VALID_TYPES = {
    'function', 'class', 'service', 'config', 'type-definition',
    'constant', 'interface', 'endpoint', 'repository', 'entity',
    'component', 'validator', 'contract', 'test', 'tool'
}
