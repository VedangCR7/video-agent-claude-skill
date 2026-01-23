"""Unit tests for validation utilities."""

import pytest
from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import (
    validate_file_extension,
    validate_image_dimensions,
)


class TestFileExtensionValidation:
    """Test file extension validation."""

    def test_valid_image_extensions(self):
        """Test valid image file extensions."""
        assert validate_file_extension("photo.jpg", ["jpg", "png", "gif"])
        assert validate_file_extension("image.PNG", ["jpg", "png", "gif"])
        assert validate_file_extension("picture.gif", ["jpg", "png", "gif"])

    def test_invalid_image_extensions(self):
        """Test invalid image file extensions."""
        assert not validate_file_extension("document.txt", ["jpg", "png", "gif"])
        assert not validate_file_extension("script.py", ["jpg", "png", "gif"])

    def test_no_extension_files(self):
        """Test files without extensions."""
        assert not validate_file_extension("README", ["jpg", "png", "gif"])
        assert not validate_file_extension("Makefile", ["jpg", "png", "gif"])

    def test_empty_inputs(self):
        """Test empty or None inputs."""
        assert not validate_file_extension("", ["jpg", "png", "gif"])
        assert not validate_file_extension("file.jpg", [])
        assert not validate_file_extension(None, ["jpg", "png", "gif"])


class TestImageDimensionValidation:
    """Test image dimension validation."""

    def test_valid_dimensions(self):
        """Test valid image dimensions."""
        assert validate_image_dimensions(1920, 1080)  # 16:9 HD
        assert validate_image_dimensions(1024, 1024)  # Square
        assert validate_image_dimensions(800, 600)    # 4:3

    def test_invalid_dimensions_zero_negative(self):
        """Test invalid dimensions (zero or negative)."""
        assert not validate_image_dimensions(0, 100)
        assert not validate_image_dimensions(100, 0)
        assert not validate_image_dimensions(-100, 100)
        assert not validate_image_dimensions(100, -100)

    def test_too_large_dimensions(self):
        """Test dimensions that are too large."""
        assert not validate_image_dimensions(3000, 2000)  # Too wide
        assert not validate_image_dimensions(2000, 3000)  # Too tall

    def test_extreme_aspect_ratios(self):
        """Test images with extreme aspect ratios."""
        assert not validate_image_dimensions(10000, 10)  # Too wide
        assert not validate_image_dimensions(10, 10000)  # Too tall
        assert validate_image_dimensions(2000, 200)      # 10:1 ratio (max allowed)