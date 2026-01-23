
# Self-contained validation integration

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
def validate_image_dimensions_enhanced(width: int, height: int, max_width: int = 2048, max_height: int = 2048) -> tuple[bool, str]:
    """
    Enhanced image dimension validation with detailed error reporting.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_width: Maximum allowed width
        max_height: Maximum allowed height

    Returns:
        Tuple of (is_valid, detailed_error_message)
    """
    # Type validation
    if not isinstance(width, int) or not isinstance(height, int):
        return False, f"Dimensions must be integers, got {type(width).__name__} and {type(height).__name__}"

    # Range validation
    if width <= 0 or height <= 0:
        return False, f"Dimensions must be positive, got {width}x{height}"

    # Size limits
    if width > max_width:
        return False, f"Width {width} exceeds maximum {max_width}"
    if height > max_height:
        return False, f"Height {height} exceeds maximum {max_height}"

    # Aspect ratio validation
    aspect_ratio = max(width, height) / min(width, height)
    if aspect_ratio > 10.0:
        return False, f"Aspect ratio {aspect_ratio:.1f}:1 exceeds maximum 10:1"

    return True, "Dimensions are valid"

def validate_processing_parameters(params: dict) -> tuple[bool, str]:
    """
    Validate processing parameters dictionary.

    Args:
        params: Dictionary of processing parameters

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(params, dict):
        return False, "Parameters must be a dictionary"

    # Validate common parameters
    if 'model' in params:
        if not isinstance(params['model'], str) or not params['model'].strip():
            return False, "Model name must be a non-empty string"

    if 'duration' in params:
        try:
            duration = float(params['duration'])
            if duration <= 0 or duration > 300:  # Max 5 minutes
                return False, "Duration must be between 0.1 and 300 seconds"
        except (ValueError, TypeError):
            return False, "Duration must be a number"

    return True, "Parameters are valid"

def validate_simple_input(value) -> bool:
    """Simple input validation function."""
    if value is None:
        return False
    if isinstance(value, str) and len(value.strip()) == 0:
        return False
    if isinstance(value, (int, float)) and value <= 0:
        return False
    return True
