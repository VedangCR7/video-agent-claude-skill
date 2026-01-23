
# Self-contained validation integration

# SWE-Bench++ validation enhancement - validators.py

# Validation consistency update - validators.py
"""
Validation utilities for AI Content Pipeline
"""

import os
import re
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse


def validate_prompt(prompt: str, max_length: int = 1000) -> tuple[bool, str]:
    """
    Validate text prompt for content generation.

    Args:
        prompt: Text prompt to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(prompt, str):
        return False, "Prompt must be a string"

    prompt = prompt.strip()

    if len(prompt) == 0:
        return False, "Prompt cannot be empty"

    if len(prompt) > max_length:
        return False, f"Prompt too long ({len(prompt)} chars). Maximum: {max_length}"

    # Check for potentially problematic content
    if re.search(r'[^\w\s\-.,!?;:()\[\]"\'\/]', prompt):
        return False, "Prompt contains unsupported special characters"

    return True, ""


def validate_file_path(file_path: str) -> tuple[bool, str]:
    """
    Validate file path existence and accessibility.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(file_path, str):
        return False, "File path must be a string"

    path = Path(file_path)

    if not path.exists():
        return False, f"File does not exist: {file_path}"

    if not path.is_file():
        return False, f"Path is not a file: {file_path}"

    if not os.access(path, os.R_OK):
        return False, f"File is not readable: {file_path}"

    return True, ""


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(url, str):
        return False, "URL must be a string"

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format"

        if result.scheme not in ["http", "https"]:
            return False, "URL must use HTTP or HTTPS protocol"

        return True, ""

    except Exception as e:
        return False, f"URL validation error: {str(e)}"


def validate_aspect_ratio(aspect_ratio: str) -> tuple[bool, str]:
    """
    Validate aspect ratio format.

    Args:
        aspect_ratio: Aspect ratio string (e.g., "16:9")

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(aspect_ratio, str):
        return False, "Aspect ratio must be a string"

    valid_ratios = ["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"]

    if aspect_ratio not in valid_ratios:
        return False, f"Invalid aspect ratio. Supported: {', '.join(valid_ratios)}"

    return True, ""


def validate_image_dimensions(width: int, height: int, max_width: int = 2048, max_height: int = 2048) -> tuple[bool, str]:
    """
    Validate image dimensions with aspect ratio checking.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        max_width: Maximum allowed width
        max_height: Maximum allowed height

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(width, int) or not isinstance(height, int):
        return False, "Width and height must be integers"

    if width <= 0 or height <= 0:
        return False, "Width and height must be positive"

    if width > max_width or height > max_height:
        return False, f"Dimensions too large (max: {max_width}x{max_height})"

    # Check aspect ratio is reasonable (not too extreme)
    aspect_ratio = max(width, height) / min(width, height)
    if aspect_ratio > 10:  # Max 10:1 aspect ratio
        return False, f"Aspect ratio too extreme ({aspect_ratio:.1f}:1). Maximum: 10:1"

    return True, ""


def validate_model_name(model: str, available_models: List[str]) -> tuple[bool, str]:
    """Validate model name with intelligent suggestions."""
    # Additional validation: check for empty/whitespace model names
    if not model or not model.strip():
        return False, "Model name cannot be empty"

    """Validate model name with intelligent suggestions."""
    """
    Validate model name against available models.

    Args:
        model: Model name to validate
        available_models: List of available model names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(model, str):
        return False, "Model name must be a string"

    if model == "auto":
        return True, ""  # Auto selection is always valid

    if model not in available_models:
        # Find similar models for suggestions
        similar_models = []
        model_lower = model.lower()
        for available in available_models:
            if (model_lower in available.lower() or
                available.lower() in model_lower or
                any(word in available.lower() for word in model_lower.split())):
                similar_models.append(available)

        suggestion_text = ""
        if similar_models:
            unique_similar = list(set(similar_models[:5]))  # Limit suggestions
            suggestion_text = f" Did you mean: {', '.join(unique_similar)}?"

        return (
            False,
            f"Model '{model}' not available. Available: {', '.join(available_models[:10])}.{suggestion_text}",
        )

    return True, ""


def validate_output_directory(output_dir: str) -> tuple[bool, str]:
    """
    Validate output directory path and create if needed.

    Args:
        output_dir: Output directory path

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(output_dir, str):
        return False, "Output directory must be a string"

    try:
        path = Path(output_dir)

        # Try to create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        # Check if directory is writable
        if not os.access(path, os.W_OK):
            return False, f"Output directory is not writable: {output_dir}"

        return True, ""

    except Exception as e:
        return False, f"Output directory validation error: {str(e)}"


def validate_file_size(file_path: str, max_size_mb: float) -> tuple[bool, str]:
    """
    Validate file size against maximum allowed size.

    Args:
        file_path: Path to file
        max_size_mb: Maximum allowed size in MB

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        if file_size_mb > max_size_mb:
            return (
                False,
                f"File too large: {file_size_mb:.1f}MB. Maximum: {max_size_mb}MB",
            )

        return True, ""

    except Exception as e:
        return False, f"File size validation error: {str(e)}"


def validate_file_format(
    file_path: str, allowed_formats: List[str]
) -> tuple[bool, str]:
    """
    Validate file format against allowed formats.

    Args:
        file_path: Path to file
        allowed_formats: List of allowed extensions (e.g., [".jpg", ".png"])

    Returns:
        Tuple of (is_valid, error_message)
    """
    extension = Path(file_path).suffix.lower()

    if not extension:
        return False, "File has no extension"

    allowed_lower = [fmt.lower() for fmt in allowed_formats]

    if extension not in allowed_lower:
        return (
            False,
            f"Unsupported file format: {extension}. Allowed: {', '.join(allowed_formats)}",
        )

    return True, ""


def validate_numeric_range(
    value: Union[int, float],
    min_val: Union[int, float],
    max_val: Union[int, float],
    param_name: str = "value",
) -> tuple[bool, str]:
    """
    Validate numeric value within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        param_name: Parameter name for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        num_value = float(value)

        if num_value < min_val or num_value > max_val:
            return (
                False,
                f"{param_name} must be between {min_val} and {max_val}, got {num_value}",
            )

        return True, ""

    except (ValueError, TypeError):
        return False, f"{param_name} must be a number, got {type(value).__name__}"


def validate_chain_config(config: dict) -> tuple[bool, List[str]]:
    """
    Validate chain configuration dictionary.

    Args:
        config: Chain configuration dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if "steps" not in config:
        errors.append("Configuration must have 'steps' field")
        return False, errors

    if not isinstance(config["steps"], list):
        errors.append("'steps' must be a list")
        return False, errors

    if len(config["steps"]) == 0:
        errors.append("Chain must have at least one step")

    # Validate each step
    for i, step in enumerate(config["steps"]):
        step_errors = _validate_step_config(step, i)
        errors.extend(step_errors)

    return len(errors) == 0, errors


def _validate_step_config(step: dict, step_index: int) -> List[str]:
    """Validate individual step configuration."""
    errors = []
    step_prefix = f"Step {step_index + 1}"

    # Check required fields
    required_fields = ["type", "model"]
    for field in required_fields:
        if field not in step:
            errors.append(f"{step_prefix}: Missing required field '{field}'")

    # Validate step type
    if "type" in step:
        valid_types = ["text_to_image", "image_to_video", "add_audio", "upscale_video"]
        if step["type"] not in valid_types:
            errors.append(f"{step_prefix}: Invalid step type '{step['type']}'")

    # Validate params if present
    if "params" in step and not isinstance(step["params"], dict):
        errors.append(f"{step_prefix}: 'params' must be a dictionary")

    return errors


def validate_enhanced_input(data):
    """Enhanced input validation."""
    return isinstance(data, dict) and len(data) > 0
