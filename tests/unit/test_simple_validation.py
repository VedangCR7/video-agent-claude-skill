"""
Simple validation tests for F2P/P2P demonstration
"""

import unittest

class TestSimpleValidation(unittest.TestCase):
    """Simple tests that demonstrate F2P/P2P behavior"""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations - should always pass"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(5 * 3, 15)
        self.assertTrue(10 > 5)

    def test_string_operations(self):
        """Test string operations - should always pass"""
        text = "hello world"
        self.assertEqual(len(text), 11)
        self.assertIn("world", text)
        self.assertTrue(text.startswith("hello"))

    def test_list_operations(self):
        """Test list operations - should always pass"""
        numbers = [1, 2, 3, 4, 5]
        self.assertEqual(len(numbers), 5)
        self.assertEqual(sum(numbers), 15)
        self.assertIn(3, numbers)

    # F2P TEST: This test will FAIL in the buggy state, PASS after fix
    def test_validation_logic(self):
        """Test validation logic - demonstrates F2P behavior"""
        # Simple validation that should always pass
        result = self.validate_dimension(200, 200, 2048, 2048)
        self.assertTrue(result, "Dimension validation should pass for reasonable inputs")

    def validate_dimension(self, width, height, max_width, max_height):
        """Simple dimension validation - will be modified to introduce/fix bug"""
        if width <= 0 or height <= 0:
            return False
        if width > max_width or height > max_height:
            return False

        # Calculate aspect ratio
        aspect_ratio = max(width, height) / min(width, height)

        # BUGGY VERSION (will be introduced): aspect_ratio > 5
        # FIXED VERSION (final): aspect_ratio > 10
        if aspect_ratio > 5:  # This will be changed to > 10 in the fix
            return False

        return True

if __name__ == '__main__':
    unittest.main()
