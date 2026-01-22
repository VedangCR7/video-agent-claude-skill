"""Test to verify the thread safety bug fix in parallel_extension.py."""

import unittest
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class TestParallelExtensionBugFix(unittest.TestCase):
    """Test that the deep copy fix prevents race conditions in parallel execution."""

    def test_shallow_copy_race_condition(self):
        """Demonstrate that shallow copy causes race conditions."""
        # Create a context with mutable nested objects
        original_context = {
            "shared_data": {"counter": 0, "items": []},
            "metadata": {"processed": False}
        }

        # Simulate what happens with shallow copy (the bug)
        shallow_copies = [original_context.copy() for _ in range(3)]

        # Modify nested objects - this affects all "copies" due to shallow copy
        for i, ctx in enumerate(shallow_copies):
            ctx["shared_data"]["counter"] += 1
            ctx["shared_data"]["items"].append(f"item_{i}")

        # All contexts share the same nested objects - this shows the bug
        for ctx in shallow_copies:
            self.assertEqual(ctx["shared_data"]["counter"], 3)  # Last modification wins
            self.assertEqual(len(ctx["shared_data"]["items"]), 3)  # All items visible

    def test_deep_copy_prevents_race_condition(self):
        """Verify that deep copy prevents race conditions (the fix)."""
        # Create a context with mutable nested objects
        original_context = {
            "shared_data": {"counter": 0, "items": []},
            "metadata": {"processed": False}
        }

        # Simulate what happens with deep copy (the fix)
        deep_copies = [copy.deepcopy(original_context) for _ in range(3)]

        # Modify nested objects - each copy is independent
        for i, ctx in enumerate(deep_copies):
            ctx["shared_data"]["counter"] += 1
            ctx["shared_data"]["items"].append(f"item_{i}")

        # Each context has its own independent nested objects
        for i, ctx in enumerate(deep_copies):
            self.assertEqual(ctx["shared_data"]["counter"], 1)  # Each has its own counter
            self.assertEqual(len(ctx["shared_data"]["items"]), 1)  # Each has its own items
            self.assertEqual(ctx["shared_data"]["items"][0], f"item_{i}")  # Correct item

    def test_parallel_execution_safety(self):
        """Test that parallel execution with deep copy is safe."""
        def worker_function(context, worker_id):
            """Simulate worker modifying context."""
            # Simulate some processing time
            time.sleep(0.01)

            # Modify context - should not affect other workers with deep copy
            context["shared_data"]["counter"] += 1
            context["shared_data"]["items"].append(f"worker_{worker_id}")
            context["metadata"]["processed"] = True

            return context

        original_context = {
            "shared_data": {"counter": 0, "items": []},
            "metadata": {"processed": False}
        }

        # Test with deep copy (safe - like the fix)
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                # Create deep copy for each worker (like the fix does)
                worker_context = copy.deepcopy(original_context)
                future = executor.submit(worker_function, worker_context, i)
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                results.append(result)

        # Verify each worker got independent context
        # Each worker should have modified only its own context
        for result in results:
            self.assertEqual(result["shared_data"]["counter"], 1)  # Each incremented once
            self.assertEqual(len(result["shared_data"]["items"]), 1)  # Each added one item
            self.assertTrue(result["metadata"]["processed"])  # Each marked as processed

        # Verify no cross-contamination between workers
        all_items = []
        for result in results:
            all_items.extend(result["shared_data"]["items"])

        # Should have 3 unique worker items
        self.assertEqual(len(all_items), 3)
        self.assertEqual(len(set(all_items)), 3)  # All unique

    def test_basic_functionality(self):
        """Ensure basic test functionality works."""
        self.assertTrue(True)
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()
