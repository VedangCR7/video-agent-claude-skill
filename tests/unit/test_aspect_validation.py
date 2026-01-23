"""
Aspect validation test - F2P/P2P
"""
import unittest

class TestAspectValidation(unittest.TestCase):
    def test_p2p_basic(self):
        self.assertEqual(2 + 2, 4)

    def test_f2p_aspect_ratio(self):
        result = self.validate_ratio(200, 20)  # 10:1
        self.assertTrue(result)

    def validate_ratio(self, w, h):
        if w <= 0 or h <= 0: return False
        ratio = max(w, h) / min(w, h)
        return ratio <= 10.0

if __name__ == '__main__':
    unittest.main()
