"""
Test for image dimension validation bug fix.

This test demonstrates F2P/P2P behavior:
- BASE state: Test fails due to validation bug
- HEAD state: Test passes after bug fix
"""

import unittest
import sys
import os

# Add the package path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))

class TestImageDimensionValidation(unittest.TestCase):
    """Test image dimension validation bug fix"""

    def test_dimension_validation_bug_f2p(self):
        """F2P test: This test FAILS in BASE state, PASSES after fix"""
        # Import the validation function
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # Test case that should pass but currently fails due to bug
        # This tests a 10:1 aspect ratio (200x20) which is reasonable
        result = validate_image_dimensions(200, 20, 2048, 2048)

        # In BASE state: This returns False (bug - rejects valid ratio)
        # In HEAD state: This returns True (fixed - accepts valid ratio)
        self.assertTrue(result[0], f"10:1 aspect ratio should be valid but got: {result[1]}")

    def test_normal_dimensions_p2p(self):
        """P2P test: Normal dimensions that should always pass"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # These should always pass regardless of the fix
        test_cases = [
            (1920, 1080, "16:9 HD"),
            (1024, 1024, "1:1 square"),
            (800, 600, "4:3 standard"),
        ]

        for width, height, desc in test_cases:
            with self.subTest(width=width, height=height, desc=desc):
                result = validate_image_dimensions(width, height, 2048, 2048)
                self.assertTrue(result[0], f"{desc} dimensions should be valid but got: {result[1]}")

    def test_extreme_dimensions_always_fail(self):
        """Test that extreme dimensions always fail (regression protection)"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # These should always fail (too extreme aspect ratios)
        test_cases = [
            (5000, 100, "50:1 too wide"),
            (100, 5000, "1:50 too tall"),
        ]

        for width, height, desc in test_cases:
            with self.subTest(width=width, height=height, desc=desc):
                result = validate_image_dimensions(width, height, 2048, 2048)
                self.assertFalse(result[0], f"{desc} should be rejected")

    def test_invalid_dimensions_always_fail(self):
        """Test invalid dimensions always fail"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # These should always fail (invalid inputs)
        invalid_cases = [
            (0, 100, "zero width"),
            (100, 0, "zero height"),
            (-100, 100, "negative width"),
            (100, -100, "negative height"),
        ]

        for width, height, desc in invalid_cases:
            with self.subTest(width=width, height=height, desc=desc):
                result = validate_image_dimensions(width, height, 2048, 2048)
                self.assertFalse(result[0], f"{desc} should be rejected")

if __name__ == '__main__':
    unittest.main()
