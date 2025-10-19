#!/usr/bin/env python3
"""Type definitions and contracts for LLM comment system.

@llm-type contract
@llm-legend Defines data structures and interfaces for LLM comment extraction/validation
@llm-context Central type system ensuring consistency across extraction and validation pipeline
"""

from typing import TypedDict, Optional, List, Dict, Literal
from dataclasses import dataclass
from pathlib import Path

# Supported languages for extraction
LanguageType = Literal["typescript", "python", "kotlin", "yaml", "javascript"]

# LLM tag names
TagType = Literal[
    "llm_type", 
    "llm_legend", 
    "llm_key", 
    "llm_map", 
    "llm_axiom", 
    "llm_contract", 
    "llm_token",
    "llm_context"  # NEW
]

@dataclass
class LLMComment:
    """Single LLM comment with all possible tags."""
    file_path: str
    line_number: int
    language: LanguageType
    element_name: str = "unknown"
    type: Optional[str] = None
    legend: Optional[str] = None
    key: Optional[str] = None
    map: Optional[str] = None
    axiom: Optional[str] = None
    contract: Optional[str] = None
    token: Optional[str] = None
    context: Optional[str] = None  # generic context
    llm_context: Optional[str] = None  # NEW: specific @llm-context tag
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

# Tag parsing patterns
TAG_PATTERNS = {
    'llm_type': r'@llm-type\s+(\w+)',
    'llm_legend': r'@llm-legend\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_key': r'@llm-key\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_map': r'@llm-map\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_axiom': r'@llm-axiom\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_contract': r'@llm-contract\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_token': r'@llm-token\s+(.+?)(?=@llm-|\n\n|\Z)',
    'llm_context': r'@llm-context\s+(.+?)(?=@llm-|\n\n|\Z)'  # NEW
}

# Required tags by element type
REQUIRED_TAGS = {
    'service': ['type', 'legend'],
    'function': ['type', 'legend'],
    'class': ['type', 'legend'],
    'component': ['type', 'legend'],
    'config': ['type', 'legend'],
    'repository': ['type', 'legend'],
    'endpoint': ['type', 'legend', 'contract'],
}

# Valid values for llm_type
VALID_TYPES = {
    'function', 'class', 'service', 'config', 'type-definition',
    'constant', 'interface', 'endpoint', 'repository', 'entity',
    'component', 'validator', 'contract', 'test', 'tool'
}
