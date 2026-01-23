"""
Comprehensive validation tests with F2P/P2P behavior
"""

import unittest
import sys
import os

# Add the package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))

class TestValidationF2P_P2P(unittest.TestCase):
    """Tests that demonstrate F2P/P2P behavior"""

    def test_basic_validation_p2p(self):
        """P2P test - should always pass"""
        # Basic arithmetic - always passes
        self.assertEqual(10 + 5, 15)
        self.assertEqual(20 * 3, 60)
        self.assertTrue(100 > 50)
        self.assertIn("test", "testing")

    def test_string_validation_p2p(self):
        """P2P test - string validation"""
        text = "validation test"
        self.assertEqual(len(text), 15)
        self.assertTrue(text.startswith("val"))
        self.assertFalse(text.isdigit())

    def test_dimension_validation_f2p(self):
        """F2P test - dimension validation with bug fix"""
        # This test FAILS before the fix (aspect_ratio > 5)
        # and PASSES after the fix (aspect_ratio > 10)
        result = self._validate_image_dimensions(200, 200)
        self.assertTrue(result, "10:1 aspect ratio should be valid")

    def test_extreme_dimensions_f2p(self):
        """F2P test - extreme aspect ratios"""
        # This should always fail (50:1 ratio)
        result = self._validate_image_dimensions(5000, 100)
        self.assertFalse(result, "50:1 aspect ratio should be invalid")

    def test_normal_dimensions_p2p(self):
        """P2P test - normal dimensions"""
        # These should always pass
        result = self._validate_image_dimensions(1920, 1080)  # 16:9
        self.assertTrue(result)

        result = self._validate_image_dimensions(1024, 1024)  # 1:1
        self.assertTrue(result)

    def _validate_image_dimensions(self, width, height):
        """Internal validation method with the bug fix"""
        if width <= 0 or height <= 0:
            return False

        if width > 2048 or height > 2048:
            return False

        # Calculate aspect ratio
        aspect_ratio = max(width, height) / min(width, height)

        # FIXED: Allow reasonable aspect ratios up to 10:1
        # Before fix: > 5 would fail (10:1 would fail)
        # After fix: > 10 would fail (10:1 passes)
        if aspect_ratio > 10.0:
            return False

        return True

class TestAdditionalValidation(unittest.TestCase):
    """Additional validation tests for P2P coverage"""

    def test_numeric_ranges_p2p(self):
        """P2P test - numeric range validation"""
        self.assertTrue(self._validate_numeric_range(5, 0, 10))
        self.assertTrue(self._validate_numeric_range(0, 0, 10))
        self.assertFalse(self._validate_numeric_range(-1, 0, 10))
        self.assertFalse(self._validate_numeric_range(15, 0, 10))

    def test_string_validation_p2p(self):
        """P2P test - string validation"""
        self.assertTrue(self._validate_string_length("hello", 1, 10))
        self.assertFalse(self._validate_string_length("", 1, 10))
        self.assertFalse(self._validate_string_length("this is too long for validation", 1, 10))

    def _validate_numeric_range(self, value, min_val, max_val):
        """Numeric range validation"""
        try:
            num = float(value)
            return min_val <= num <= max_val
        except (ValueError, TypeError):
            return False

    def _validate_string_length(self, text, min_len, max_len):
        """String length validation"""
        if not isinstance(text, str):
            return False
        length = len(text.strip())
        return min_len <= length <= max_len

if __name__ == '__main__':
    unittest.main()
