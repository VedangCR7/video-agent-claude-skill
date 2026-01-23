"""
Input validation utilities for AI Content Pipeline
"""

from typing import Any, Dict, List, Union

def validate_numeric_input(value: Any, min_val: float = None, max_val: float = None, param_name: str = "value") -> tuple[bool, str]:
    """
    Validate that input is numeric and within optional range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)
        param_name: Parameter name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False, f"{param_name} must be a number, got {type(value).__name__}"

    if min_val is not None and num_value < min_val:
        return False, f"{param_name} must be >= {min_val}, got {num_value}"

    if max_val is not None and num_value > max_val:
        return False, f"{param_name} must be <= {max_val}, got {num_value}"

    return True, ""

def validate_string_input(value: Any, min_length: int = 1, max_length: int = None, param_name: str = "value") -> tuple[bool, str]:
    """
    Validate that input is a string with length constraints.

    Args:
        value: Value to validate
        min_length: Minimum string length
        max_length: Maximum string length (optional)
        param_name: Parameter name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, str):
        return False, f"{param_name} must be a string, got {type(value).__name__}"

    if len(value.strip()) < min_length:
        return False, f"{param_name} must be at least {min_length} characters long"

    if max_length is not None and len(value) > max_length:
        return False, f"{param_name} must be at most {max_length} characters long"

    return True, ""

def validate_list_input(value: Any, min_items: int = 0, max_items: int = None, param_name: str = "value") -> tuple[bool, str]:
    """
    Validate that input is a list with size constraints.

    Args:
        value: Value to validate
        min_items: Minimum number of items
        max_items: Maximum number of items (optional)
        param_name: Parameter name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(value, list):
        return False, f"{param_name} must be a list, got {type(value).__name__}"

    if len(value) < min_items:
        return False, f"{param_name} must have at least {min_items} items, got {len(value)}"

    if max_items is not None and len(value) > max_items:
        return False, f"{param_name} must have at most {max_items} items, got {len(value)}"

    return True, ""
