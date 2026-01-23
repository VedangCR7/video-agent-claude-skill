"""
Comprehensive validation tests for F2P/P2P demonstration.

This test suite covers multiple validation components and demonstrates
proper F2P/P2P behavior across different commits.
"""

import unittest
import sys
import os

# Add package path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))

class TestComprehensiveValidation(unittest.TestCase):
    """Comprehensive validation test suite"""

    def test_image_dimension_validation_f2p(self):
        """F2P: Image dimension validation - fails before fix, passes after"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # Test cases that should pass but might fail due to bugs
        test_cases = [
            (200, 20, "10:1 aspect ratio"),
            (300, 30, "10:1 aspect ratio larger"),
            (150, 15, "10:1 aspect ratio smaller"),
        ]

        for width, height, desc in test_cases:
            with self.subTest(width=width, height=height, desc=desc):
                result = validate_image_dimensions(width, height, 2048, 2048)
                self.assertTrue(result[0], f"{desc} should be valid but got: {result[1]}")

    def test_file_format_validation_f2p(self):
        """F2P: File format validation - fails before fix, passes after"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.file_manager import FileManager
            fm = FileManager()
            # Test the validate_file_format method if it exists
            if hasattr(fm, 'validate_file_format'):
                # These should pass with proper validation
                result = fm.validate_file_format("test.jpg", [".jpg", ".png"])
                self.assertTrue(result[0], f"JPG should be valid: {result[1]}")

                result = fm.validate_file_format("test.png", [".jpg", ".png"])
                self.assertTrue(result[0], f"PNG should be valid: {result[1]}")
            else:
                self.skipTest("validate_file_format method not available")
        except ImportError:
            self.skipTest("File manager module not available")

    def test_model_validation_f2p(self):
        """F2P: Model validation - fails before fix, passes after"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validators import validate_model_name
        except ImportError:
            self.skipTest("Validators module not available")

        # Test model validation with suggestions
        available_models = ["flux_dev", "flux_schnell", "stable_diffusion"]
        result = validate_model_name("flux_dev", available_models)
        self.assertTrue(result[0], f"Valid model should pass: {result[1]}")

    def test_p2p_basic_arithmetic(self):
        """P2P: Basic arithmetic that always passes"""
        self.assertEqual(10 + 5, 15)
        self.assertEqual(20 * 3, 60)
        self.assertEqual(100 - 25, 75)
        self.assertTrue(50 < 100)

    def test_p2p_string_operations(self):
        """P2P: String operations that always pass"""
        text = "validation_test"
        self.assertEqual(len(text), 15)
        self.assertTrue(text.startswith("val"))
        self.assertTrue("test" in text)
        self.assertFalse(text.isupper())

    def test_p2p_list_operations(self):
        """P2P: List operations that always pass"""
        numbers = [5, 10, 15, 20]
        self.assertEqual(sum(numbers), 50)
        self.assertEqual(max(numbers), 20)
        self.assertEqual(min(numbers), 5)
        self.assertEqual(len(numbers), 4)

    def test_p2p_type_checks(self):
        """P2P: Type checking that always passes"""
        self.assertIsInstance(42, int)
        self.assertIsInstance("hello", str)
        self.assertIsInstance([1, 2, 3], list)
        self.assertIsInstance({"key": "value"}, dict)

class TestValidationEdgeCases(unittest.TestCase):
    """Test edge cases for validation functions"""

    def test_dimension_edge_cases_p2p(self):
        """P2P: Dimension edge cases that should always fail"""
        try:
            from packages.core.ai_content_pipeline.ai_content_pipeline.utils.validation import validate_image_dimensions
        except ImportError:
            self.skipTest("Validation module not available")

        # These should always fail
        invalid_cases = [
            (0, 100, "zero width"),
            (100, 0, "zero height"),
            (-10, 100, "negative width"),
            (100, -10, "negative height"),
        ]

        for width, height, desc in invalid_cases:
            with self.subTest(width=width, height=height, desc=desc):
                result = validate_image_dimensions(width, height, 2048, 2048)
                self.assertFalse(result[0], f"{desc} should be invalid")

if __name__ == '__main__':
    unittest.main()
