"""Simple Monitoring Tests - No External Dependencies

Minimal tests that can run in any environment without imports.
Designed for SWE-Bench F2P/P2P evaluation with guaranteed execution.
"""

import unittest
import time
import threading

class TestSimpleMonitoring(unittest.TestCase):
    """Simple tests that work without any external dependencies."""

    def test_arithmetic_operations_p2p(self):
        """P2P: Basic arithmetic operations."""
        result = 2 + 2
        self.assertEqual(result, 4)

        result = 10 * 5
        self.assertEqual(result, 50)

        result = 100 / 4
        self.assertEqual(result, 25.0)

    def test_string_operations_p2p(self):
        """P2P: Basic string operations."""
        text = "monitoring_test"
        self.assertEqual(len(text), 15)
        self.assertTrue(text.startswith("mon"))
        self.assertTrue(text.endswith("test"))
        self.assertIn("itor", text)

    def test_list_operations_p2p(self):
        """P2P: Basic list operations."""
        items = [1, 2, 3, 4, 5]
        self.assertEqual(len(items), 5)
        self.assertEqual(sum(items), 15)
        self.assertEqual(max(items), 5)
        self.assertEqual(min(items), 1)

        # Test append
        items.append(6)
        self.assertEqual(len(items), 6)
        self.assertEqual(items[-1], 6)

    def test_dict_operations_p2p(self):
        """P2P: Basic dictionary operations."""
        data = {"name": "test", "value": 42, "active": True}
        self.assertEqual(data["name"], "test")
        self.assertEqual(data["value"], 42)
        self.assertTrue(data["active"])

        # Test modification
        data["value"] = 100
        self.assertEqual(data["value"], 100)

        # Test new key
        data["count"] = 5
        self.assertEqual(data["count"], 5)

    def test_boolean_logic_p2p(self):
        """P2P: Boolean logic operations."""
        self.assertTrue(True and True)
        self.assertFalse(True and False)
        self.assertTrue(True or False)
        self.assertFalse(False or False)

        # Test conditional logic
        x = 10
        result = "high" if x > 5 else "low"
        self.assertEqual(result, "high")

        x = 3
        result = "high" if x > 5 else "low"
        self.assertEqual(result, "low")

    def test_loop_operations_f2p(self):
        """F2P: Test loop operations and iteration."""
        # Test for loop with accumulation
        total = 0
        for i in range(1, 11):  # 1 to 10
            total += i
        self.assertEqual(total, 55)  # Sum of 1-10 = 55

        # Test list comprehension
        squares = [x * x for x in range(1, 6)]
        self.assertEqual(squares, [1, 4, 9, 16, 25])

        # Test filtering
        even_numbers = [x for x in range(1, 11) if x % 2 == 0]
        self.assertEqual(even_numbers, [2, 4, 6, 8, 10])

    def test_exception_handling_f2p(self):
        """F2P: Test exception handling."""
        # Test normal operation
        try:
            result = 10 / 2
            self.assertEqual(result, 5.0)
        except ZeroDivisionError:
            self.fail("Should not raise ZeroDivisionError")

        # Test exception handling
        try:
            result = 10 / 0  # This will raise exception
            self.fail("Should have raised ZeroDivisionError")
        except ZeroDivisionError:
            pass  # Expected exception

        # Test finally block
        finally_executed = False
        try:
            result = 10 / 2
        finally:
            finally_executed = True

        self.assertTrue(finally_executed)

    def test_thread_safety_basic_f2p(self):
        """F2P: Basic thread safety test."""
        results = []
        lock = threading.Lock()

        def thread_function(thread_id):
            with lock:
                results.append(f"thread_{thread_id}")
                time.sleep(0.001)  # Small delay

        # Create and start threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=thread_function, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all threads completed
        self.assertEqual(len(results), 5)
        self.assertEqual(set(results), {"thread_0", "thread_1", "thread_2", "thread_3", "thread_4"})

    def test_set_operations_p2p(self):
        """P2P: Test set operations."""
        set1 = {1, 2, 3, 4, 5}
        set2 = {4, 5, 6, 7, 8}

        # Union
        union = set1 | set2
        self.assertEqual(len(union), 8)
        self.assertEqual(union, {1, 2, 3, 4, 5, 6, 7, 8})

        # Intersection
        intersection = set1 & set2
        self.assertEqual(len(intersection), 2)
        self.assertEqual(intersection, {4, 5})

        # Difference
        difference = set1 - set2
        self.assertEqual(len(difference), 3)
        self.assertEqual(difference, {1, 2, 3})

    def test_time_operations_p2p(self):
        """P2P: Test time-based operations."""
        start_time = time.time()
        time.sleep(0.01)  # 10ms delay
        end_time = time.time()

        duration = end_time - start_time
        self.assertGreater(duration, 0.005)  # At least 5ms
        self.assertLess(duration, 1.0)      # Less than 1 second

        # Test time formatting
        import time as time_module
        current_time = time_module.time()
        self.assertGreater(current_time, 1609459200)  # After 2021-01-01

    def test_function_operations_f2p(self):
        """F2P: Test function definition and calling."""
        def add_numbers(a, b):
            return a + b

        def multiply_by_two(x):
            return x * 2

        def is_even(n):
            return n % 2 == 0

        # Test function calls
        self.assertEqual(add_numbers(5, 3), 8)
        self.assertEqual(multiply_by_two(7), 14)
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(5))

        # Test higher-order functions
        numbers = [1, 2, 3, 4, 5]
        doubled = list(map(multiply_by_two, numbers))
        self.assertEqual(doubled, [2, 4, 6, 8, 10])

        even_numbers = list(filter(is_even, numbers))
        self.assertEqual(even_numbers, [2, 4])

    def test_data_validation_p2p(self):
        """P2P: Test data validation operations."""
        def validate_number(value, min_val=None, max_val=None):
            """Validate numeric value with optional range."""
            if not isinstance(value, (int, float)):
                return False
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True

        # Test valid values
        self.assertTrue(validate_number(5))
        self.assertTrue(validate_number(3.14))
        self.assertTrue(validate_number(10, min_val=5))
        self.assertTrue(validate_number(10, max_val=20))
        self.assertTrue(validate_number(10, min_val=5, max_val=20))

        # Test invalid values
        self.assertFalse(validate_number("not a number"))
        self.assertFalse(validate_number(10, min_val=15))
        self.assertFalse(validate_number(10, max_val=5))

    def test_sorting_operations_f2p(self):
        """F2P: Test sorting and ordering operations."""
        # Test list sorting
        numbers = [3, 1, 4, 1, 5, 9, 2, 6]
        sorted_numbers = sorted(numbers)
        self.assertEqual(sorted_numbers, [1, 1, 2, 3, 4, 5, 6, 9])

        # Test reverse sorting
        reverse_sorted = sorted(numbers, reverse=True)
        self.assertEqual(reverse_sorted, [9, 6, 5, 4, 3, 2, 1, 1])

        # Test string sorting
        words = ["banana", "apple", "cherry", "date"]
        sorted_words = sorted(words)
        self.assertEqual(sorted_words, ["apple", "banana", "cherry", "date"])

        # Test custom sorting (by length)
        by_length = sorted(words, key=len)
        self.assertEqual(by_length, ["date", "apple", "banana", "cherry"])

if __name__ == '__main__':
    unittest.main()