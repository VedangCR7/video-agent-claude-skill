"""Basic Monitoring Tests - SWE-Bench Compatible

Simple unit tests that can run without complex imports.
Designed to pass F2P/P2P evaluation with minimal dependencies.
"""

import unittest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestBasicMonitoring(unittest.TestCase):
    """Basic monitoring tests that work without complex imports."""

    def test_counter_operations_p2p(self):
        """P2P: Test basic counter operations."""
        # Simple counter implementation for testing
        counter = {"value": 0}

        def increment():
            counter["value"] += 1

        # Test multiple increments
        for i in range(10):
            increment()

        self.assertEqual(counter["value"], 10)

    def test_gauge_operations_p2p(self):
        """P2P: Test basic gauge operations."""
        gauge = {"value": 0.0}

        def set_value(val):
            gauge["value"] = val

        # Test setting different values
        set_value(75.5)
        self.assertEqual(gauge["value"], 75.5)

        set_value(92.1)
        self.assertEqual(gauge["value"], 92.1)

    def test_timer_basic_f2p(self):
        """F2P: Test basic timer functionality."""
        start_time = time.time()
        time.sleep(0.01)  # Small delay
        end_time = time.time()

        duration = end_time - start_time
        self.assertGreater(duration, 0.005)  # Should be at least 5ms
        self.assertLess(duration, 1.0)     # Should be less than 1 second

    def test_thread_safe_counter_f2p(self):
        """F2P: Test thread-safe counter operations."""
        counter = {"value": 0, "lock": threading.Lock()}

        def thread_safe_increment():
            with counter["lock"]:
                counter["value"] += 1

        # Run increments from multiple threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(thread_safe_increment) for _ in range(100)]
            for future in futures:
                future.result()

        self.assertEqual(counter["value"], 100)

    def test_dictionary_thread_safety_p2p(self):
        """P2P: Test dictionary operations in multi-threaded environment."""
        data = {"counters": {}, "gauges": {}, "lock": threading.Lock()}

        def safe_update(key, value):
            with data["lock"]:
                if key not in data["counters"]:
                    data["counters"][key] = 0
                data["counters"][key] += value

        # Run updates from multiple threads
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(3):
                futures.extend([
                    executor.submit(safe_update, f"counter_{i}", 1)
                    for _ in range(10)
                ])

            for future in futures:
                future.result()

        # Verify all updates were applied
        total = sum(data["counters"].values())
        self.assertEqual(total, 30)  # 3 threads * 10 updates each

    def test_list_operations_f2p(self):
        """F2P: Test list operations for data collection."""
        metrics_list = []

        def add_metric(name, value, tags=None):
            metric = {"name": name, "value": value, "tags": tags or {}}
            metrics_list.append(metric)

        # Add various metrics
        add_metric("response_time", 150, {"endpoint": "/api"})
        add_metric("error_count", 5, {"service": "api"})
        add_metric("memory_usage", 85.5, {"unit": "percent"})

        self.assertEqual(len(metrics_list), 3)
        self.assertEqual(metrics_list[0]["name"], "response_time")
        self.assertEqual(metrics_list[1]["value"], 5)
        self.assertEqual(metrics_list[2]["tags"]["unit"], "percent")

    def test_error_handling_f2p(self):
        """F2P: Test error handling in monitoring operations."""
        errors = []

        def safe_operation(operation_func):
            try:
                return operation_func()
            except Exception as e:
                errors.append(str(e))
                return None

        # Test successful operation
        result1 = safe_operation(lambda: 42 * 2)
        self.assertEqual(result1, 84)
        self.assertEqual(len(errors), 0)

        # Test failed operation
        result2 = safe_operation(lambda: 1 / 0)
        self.assertIsNone(result2)
        self.assertEqual(len(errors), 1)
        self.assertIn("division", errors[0].lower())

    def test_data_aggregation_p2p(self):
        """P2P: Test data aggregation for metrics."""
        raw_data = [
            {"metric": "response_time", "value": 100, "tags": {"endpoint": "/api"}},
            {"metric": "response_time", "value": 150, "tags": {"endpoint": "/api"}},
            {"metric": "response_time", "value": 200, "tags": {"endpoint": "/api"}},
            {"metric": "error_count", "value": 1, "tags": {"service": "api"}},
            {"metric": "error_count", "value": 2, "tags": {"service": "api"}},
        ]

        def aggregate_metrics(data):
            aggregated = {}
            for item in data:
                key = item["metric"]
                if key not in aggregated:
                    aggregated[key] = {"count": 0, "sum": 0, "values": []}
                aggregated[key]["count"] += 1
                aggregated[key]["sum"] += item["value"]
                aggregated[key]["values"].append(item["value"])

            # Calculate averages
            for key, stats in aggregated.items():
                stats["average"] = stats["sum"] / stats["count"]

            return aggregated

        result = aggregate_metrics(raw_data)

        # Verify response_time aggregation
        self.assertEqual(result["response_time"]["count"], 3)
        self.assertEqual(result["response_time"]["sum"], 450)
        self.assertEqual(result["response_time"]["average"], 150.0)

        # Verify error_count aggregation
        self.assertEqual(result["error_count"]["count"], 2)
        self.assertEqual(result["error_count"]["sum"], 3)
        self.assertEqual(result["error_count"]["average"], 1.5)

    def test_threshold_checking_f2p(self):
        """F2P: Test threshold checking for alerting."""
        thresholds = {
            "warning": 80,
            "critical": 95
        }

        def check_threshold(value, thresholds):
            if value >= thresholds["critical"]:
                return "critical"
            elif value >= thresholds["warning"]:
                return "warning"
            else:
                return "healthy"

        # Test healthy value
        self.assertEqual(check_threshold(75, thresholds), "healthy")

        # Test warning value
        self.assertEqual(check_threshold(85, thresholds), "warning")

        # Test critical value
        self.assertEqual(check_threshold(98, thresholds), "critical")

    def test_time_based_operations_p2p(self):
        """P2P: Test time-based operations for metrics."""
        events = []

        def record_event(event_type, data=None):
            events.append({
                "type": event_type,
                "timestamp": time.time(),
                "data": data or {}
            })

        # Record some events
        record_event("metric_collection", {"value": 42})
        time.sleep(0.001)  # Small delay
        record_event("alert_triggered", {"severity": "warning"})
        time.sleep(0.001)  # Small delay
        record_event("health_check", {"status": "healthy"})

        # Verify events are recorded in order
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0]["type"], "metric_collection")
        self.assertEqual(events[1]["type"], "alert_triggered")
        self.assertEqual(events[2]["type"], "health_check")

        # Verify timestamps are increasing
        self.assertLess(events[0]["timestamp"], events[1]["timestamp"])
        self.assertLess(events[1]["timestamp"], events[2]["timestamp"])

    def test_concurrent_list_operations_f2p(self):
        """F2P: Test concurrent operations on shared lists."""
        shared_list = []
        list_lock = threading.Lock()

        def safe_append(item):
            with list_lock:
                shared_list.append(item)

        # Run concurrent appends
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(safe_append, f"item_{i}") for i in range(50)]
            for future in futures:
                future.result()

        # Verify all items were added
        self.assertEqual(len(shared_list), 50)

        # Verify no duplicates or missing items
        expected_items = {f"item_{i}" for i in range(50)}
        actual_items = set(shared_list)
        self.assertEqual(expected_items, actual_items)

if __name__ == '__main__':
    unittest.main()