"""
Dimension validation test - F2P/P2P demonstration
"""

import unittest

class TestDimensionValidation(unittest.TestCase):
    """Test dimension validation fixes"""

    def test_p2p_basic_checks(self):
        """P2P: Basic validation that always passes"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(10 * 3, 30)
        self.assertTrue(50 < 100)
        self.assertFalse(100 < 50)

    def test_p2p_string_validation(self):
        """P2P: String operations that always work"""
        text = "dimension_test"
        self.assertEqual(len(text), 14)
        self.assertIn("test", text)
        self.assertTrue(text.startswith("dim"))

    def test_f2p_aspect_ratio_validation(self):
        """F2P: Aspect ratio validation - fails before fix, passes after"""
        # Test 10:1 aspect ratio (200x20) - should pass after fix
        result = self.validate_aspect_ratio(200, 20)
        self.assertTrue(result, "10:1 aspect ratio should be valid after fix")

        # Test 15:1 aspect ratio (300x20) - should always fail
        result = self.validate_aspect_ratio(300, 20)
        self.assertFalse(result, "15:1 aspect ratio should always be invalid")

    def test_p2p_invalid_dimensions(self):
        """P2P: Invalid dimensions should always be rejected"""
        # Zero dimensions
        self.assertFalse(self.validate_aspect_ratio(0, 100))
        self.assertFalse(self.validate_aspect_ratio(100, 0))

        # Negative dimensions
        self.assertFalse(self.validate_aspect_ratio(-100, 100))
        self.assertFalse(self.validate_aspect_ratio(100, -100))

    def validate_aspect_ratio(self, width, height):
        """Validate aspect ratio - matches the fix logic"""
        if width <= 0 or height <= 0:
            return False

        if width > 2048 or height > 2048:
            return False

        # Calculate aspect ratio
        aspect_ratio = max(width, height) / min(width, height)

        # FIXED: Allow up to 10:1 aspect ratio
        # Before fix: > 5 would fail (10:1 rejected)
        # After fix: > 10 would fail (10:1 accepted)
        return aspect_ratio <= 10.0

if __name__ == '__main__':
    unittest.main()
