"""
Validation helper utilities for AI Content Pipeline
"""

def validate_positive_number(value, param_name="value"):
    """Validate that a value is a positive number."""
    try:
        num = float(value)
        return num > 0, "" if num > 0 else f"{param_name} must be positive"
    except (ValueError, TypeError):
        return False, f"{param_name} must be a number"

def validate_string_length(text, min_len=1, max_len=None, param_name="text"):
    """Validate string length constraints."""
    if not isinstance(text, str):
        return False, f"{param_name} must be a string"

    if len(text.strip()) < min_len:
        return False, f"{param_name} must be at least {min_len} characters"

    if max_len and len(text) > max_len:
        return False, f"{param_name} must be at most {max_len} characters"

    return True, ""
