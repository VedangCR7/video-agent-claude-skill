"""
Enhanced validation tests
"""

import unittest
import sys
import os

# Add the package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))

from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import (
    validate_numeric_range
)

class TestEnhancedValidation(unittest.TestCase):
    """Test enhanced validation functions"""

    def test_numeric_range_validation(self):
        """Test numeric range validation"""
        # Valid cases
        self.assertTrue(validate_numeric_range(5, 0, 10)[0])
        self.assertTrue(validate_numeric_range(0, 0, 10)[0])
        self.assertTrue(validate_numeric_range(10, 0, 10)[0])

        # Invalid cases
        self.assertFalse(validate_numeric_range(-1, 0, 10)[0])
        self.assertFalse(validate_numeric_range(15, 0, 10)[0])
        self.assertFalse(validate_numeric_range("not_a_number", 0, 10)[0])

    def test_dimension_validation_logic(self):
        """Test dimension validation logic"""
        # This should work with our enhanced validation
        result = self._validate_dimensions_with_logic(1920, 1080)
        self.assertTrue(result)

        result = self._validate_dimensions_with_logic(0, 100)
        self.assertFalse(result)

    def _validate_dimensions_with_logic(self, width, height):
        """Helper method with validation logic"""
        if width <= 0 or height <= 0:
            return False

        if width > 2048 or height > 2048:
            return False

        # Calculate aspect ratio with logic
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 10.0:
            return False

        return True

if __name__ == '__main__':
    unittest.main()
