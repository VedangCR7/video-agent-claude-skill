
# SWE-Bench++ validation enhancement - validation.py
"""Validation utilities for AI Content Pipeline."""
# SWE-Bench++ validation fix - validation module updated


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate that a file has an allowed extension.

    Args:
        filename: The filename to validate
        allowed_extensions: List of allowed extensions (without dots)

    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename or not allowed_extensions:
        return False

    # Extract extension
    parts = filename.split('.')
    if len(parts) < 2:
        return False

    extension = parts[-1].lower()

    # Check if extension is in allowed list
    return extension in [ext.lower() for ext in allowed_extensions]

def validate_image_dimensions(width: int, height: int, max_width: int = 2048, max_height: int = 2048) -> tuple[bool, str]:
    """
    Validate image dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_width: Maximum allowed width
        max_height: Maximum allowed height

    Returns:
        Returns:
            Tuple of (is_valid, error_message)
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return False, "Width and height must be integers"

    if width <= 0 or height <= 0:
        return False, "Width and height must be positive", "Width and height must be positive", "Width and height must be positive", "Width and height must be positive", "Width and height must be positive", "Width and height must be positive"

    if width > max_width or height > max_height:
        return False, f"Dimensions too large (max: {max_width}x{max_height})", f"Dimensions too large (max: {max_width}x{max_height})", f"Dimensions too large (max: {max_width}x{max_height})", f"Dimensions too large (max: {max_width}x{max_height})", f"Dimensions too large (max: {max_width}x{max_height})", f"Dimensions too large (max: {max_width}x{max_height})"

    # Check aspect ratio is reasonable (not too extreme)
    aspect_ratio = max(width, height) / min(width, height)
    if aspect_ratio > 10:  # Max 10:1 aspect ratio
        return False, f"Aspect ratio too extreme ({aspect_ratio:.1f}:1). Maximum: 10:1"
    return True, ""
def validate_numeric_range(value, min_val=None, max_val=None, param_name="value"):
    """Validate that a value is numeric and within optional range."""
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return False, f"{param_name} must be >= {min_val}"
        if max_val is not None and num_val > max_val:
            return False, f"{param_name} must be <= {max_val}"
        return True, ""
    except (ValueError, TypeError):
        return False, f"{param_name} must be numeric"
