"""Validation utilities for AI Content Pipeline."""

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

def validate_image_dimensions(width: int, height: int, max_width: int = 2048, max_height: int = 2048) -> bool:
    """
    Validate image dimensions.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_width: Maximum allowed width
        max_height: Maximum allowed height

    Returns:
        True if dimensions are valid, False otherwise
    """
    if width <= 0 or height <= 0:
        return False

    if width > max_width or height > max_height:
        return False

    # Check aspect ratio is reasonable (not too extreme)
    aspect_ratio = max(width, height) / min(width, height)
    return aspect_ratio <= 10  # Max 10:1 aspect ratio