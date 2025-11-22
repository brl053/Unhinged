#!/usr/bin/env python3
"""
@llm-type util.typing
@llm-purpose Reusable type guards for dynamic data validation

Type guards extracted from 179 mypy error fixes. These patterns handle
inherently dynamic operations (YAML, JSON, DB) with runtime validation.
"""

from typing import Any, TypeGuard


def is_dict(value: Any) -> TypeGuard[dict[str, Any]]:
    """
    Type guard for dictionary validation.
    
    Use after yaml.safe_load(), json.loads(), or other dynamic parsing.
    
    Example:
        result = yaml.safe_load(f)
        if not is_dict(result):
            raise ValueError("Expected dictionary")
        return result  # mypy knows it's dict[str, Any]
    """
    return isinstance(value, dict)


def is_str_dict(value: Any) -> TypeGuard[dict[str, str]]:
    """
    Type guard for string-only dictionaries.
    
    Validates that all keys and values are strings.
    """
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def is_list(value: Any) -> TypeGuard[list[Any]]:
    """
    Type guard for list validation.
    
    Use after parsing operations that might return non-list types.
    """
    return isinstance(value, list)


def is_str_list(value: Any) -> TypeGuard[list[str]]:
    """
    Type guard for string list validation.
    
    Validates that all elements are strings.
    """
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def ensure_dict(value: Any, error_msg: str = "Expected dictionary") -> dict[str, Any]:
    """
    Ensure value is a dictionary, raise ValueError if not.
    
    Use for YAML/JSON parsing with clear error messages.
    
    Example:
        config = ensure_dict(yaml.safe_load(f), "Config must be a dictionary")
    """
    if not isinstance(value, dict):
        raise ValueError(error_msg)
    return value


def ensure_list(value: Any, error_msg: str = "Expected list") -> list[Any]:
    """
    Ensure value is a list, raise ValueError if not.
    """
    if not isinstance(value, list):
        raise ValueError(error_msg)
    return value


def safe_dict_get(d: dict[str, Any], key: str, expected_type: type, default: Any = None) -> Any:
    """
    Safely get dictionary value with type checking.
    
    Args:
        d: Dictionary to access
        key: Key to retrieve
        expected_type: Expected type of value
        default: Default value if key missing or wrong type
    
    Returns:
        Value if exists and correct type, otherwise default
    
    Example:
        order = safe_dict_get(config, "order", int, 0)
    """
    value = d.get(key, default)
    if value is not None and not isinstance(value, expected_type):
        return default
    return value


# Common type aliases for documentation
ConfigDict = dict[str, Any]
"""Dictionary for configuration data (mixed types)"""

SpecDict = dict[str, Any]
"""Dictionary for specification data (YAML/JSON)"""

MetadataDict = dict[str, str]
"""Dictionary for metadata (string keys and values only)"""


__all__ = [
    "is_dict",
    "is_str_dict",
    "is_list",
    "is_str_list",
    "ensure_dict",
    "ensure_list",
    "safe_dict_get",
    "ConfigDict",
    "SpecDict",
    "MetadataDict",
]

