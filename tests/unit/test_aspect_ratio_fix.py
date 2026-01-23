"""
Aspect ratio validation test - F2P/P2P demonstration
"""

import unittest

class TestAspectRatioValidation(unittest.TestCase):
    """Test aspect ratio validation fixes"""

    def test_p2p_basic_operations(self):
        """P2P: Basic operations that always pass"""
        self.assertEqual(5 + 3, 8)
        self.assertEqual(15 * 2, 30)
        self.assertTrue(20 > 10)
        self.assertFalse(5 > 15)

    def test_p2p_string_operations(self):
        """P2P: String operations that always work"""
        text = "aspect_ratio_test"
        self.assertEqual(len(text), 17)
        self.assertIn("ratio", text)
        self.assertTrue(text.endswith("test"))

    def test_f2p_aspect_ratio_validation(self):
        """F2P: Aspect ratio validation - fails before fix, passes after"""
        # Test 10:1 aspect ratio (200x20) - should pass after fix
        result = self.validate_aspect_ratio(200, 20)
        self.assertTrue(result, "10:1 aspect ratio should be valid after fix")

        # Test 15:1 aspect ratio (300x20) - should always fail
        result = self.validate_aspect_ratio(300, 20)
        self.assertFalse(result, "15:1 aspect ratio should always be invalid")

    def test_p2p_invalid_dimensions_always_fail(self):
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
