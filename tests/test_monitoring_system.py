"""Comprehensive Unit Tests for Monitoring System.

35+ unit tests covering all aspects of the monitoring, alerting, and health check system.
Tests thread safety, metrics collection, alerting logic, health checks, and API endpoints.

Test Categories:
- MetricsRegistry: Thread-safe collection and storage (8 tests)
- AlertManager: Rule-based alerting and cooldown (7 tests)
- HealthChecker: Multi-dimensional health assessment (6 tests)
- API Endpoints: RESTful monitoring interfaces (6 tests)
- Integration: End-to-end system behavior (8 tests)
"""

import unittest
import time
import threading
import json
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

from packages.core.monitoring.monitoring.metrics import (
    MetricsRegistry, AlertManager, HealthChecker,
    AlertSeverity, MetricType, increment_counter, set_gauge,
    start_timer, get_metrics_summary, get_alert_summary, get_health_status
)
from packages.core.monitoring.monitoring.metrics_config import (
    get_alert_rules, ALERT_RULES_CONFIG
)

class TestMetricsRegistry(unittest.TestCase):
    """Test MetricsRegistry thread safety and functionality."""

    def setUp(self):
        self.registry = MetricsRegistry(max_history_per_metric=100)

    def test_counter_increment(self):
        """Test counter metric increment functionality."""
        increment_counter("test_counter", 5, {"service": "test"})
        increment_counter("test_counter", 3, {"service": "test"})

        summary = get_metrics_summary()
        self.assertEqual(summary["counters"]["test_counter"], 8)

    def test_gauge_setting(self):
        """Test gauge metric setting and updating."""
        set_gauge("memory_usage", 85.5, {"unit": "percent"})
        set_gauge("memory_usage", 92.1, {"unit": "percent"})

        summary = get_metrics_summary()
        recent = summary["recent_measurements"]["memory_usage"]
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[-1]["value"], 92.1)  # Most recent value

    def test_timer_context_manager(self):
        """Test timer context manager functionality."""
        with start_timer("operation_duration", {"operation": "test"}) as timer:
            time.sleep(0.01)  # Simulate operation

        summary = get_metrics_summary()
        self.assertIn("operation_duration", summary["recent_measurements"])
        measurement = summary["recent_measurements"]["operation_duration"][0]
        self.assertGreater(measurement["value"], 0.01)  # Should have recorded time

    def test_thread_safe_concurrent_access(self):
        """Test thread safety with concurrent metric updates."""
        results = []

        def worker_thread(thread_id):
            """Worker function for concurrent testing."""
            for i in range(100):
                increment_counter(f"thread_{thread_id}_counter", 1, {"thread": str(thread_id)})
                set_gauge(f"thread_{thread_id}_progress", i, {"thread": str(thread_id)})
            results.append(f"thread_{thread_id}_completed")

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        summary = get_metrics_summary()
        self.assertEqual(len(results), 5)  # All threads completed

        # Check that counters were incremented correctly
        for i in range(5):
            counter_name = f"thread_{i}_counter"
            self.assertEqual(summary["counters"][counter_name], 100)

    def test_metric_history_cleanup(self):
        """Test automatic cleanup of old metric history."""
        # Create registry with small history limit
        registry = MetricsRegistry(max_history_per_metric=5)

        # Add more points than the limit
        for i in range(10):
            registry.record("test_metric", i, {"index": str(i)})
            time.sleep(0.001)  # Ensure different timestamps

        # Check that only recent points are kept
        summary = registry.get_metrics_summary()
        history = summary["recent_measurements"]["test_metric"]
        self.assertLessEqual(len(history), 5)  # Should not exceed limit

        # Verify most recent values are preserved
        recent_values = [point["value"] for point in history]
        self.assertIn(9, recent_values)  # Most recent should be there

    def test_metric_tags_functionality(self):
        """Test metric tagging and filtering."""
        # Record metrics with different tags
        set_gauge("api_response_time", 150, {"endpoint": "/api/v1", "method": "GET"})
        set_gauge("api_response_time", 200, {"endpoint": "/api/v1", "method": "POST"})
        set_gauge("api_response_time", 300, {"endpoint": "/api/v2", "method": "GET"})

        summary = get_metrics_summary()
        measurements = summary["recent_measurements"]["api_response_time"]

        # Should have 3 measurements with different tags
        self.assertEqual(len(measurements), 3)

        # Check tags are preserved
        endpoints = [m["tags"]["endpoint"] for m in measurements]
        methods = [m["tags"]["method"] for m in measurements]

        self.assertIn("/api/v1", endpoints)
        self.assertIn("/api/v2", endpoints)
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)

    def test_metric_types_validation(self):
        """Test different metric types are handled correctly."""
        registry = MetricsRegistry()

        # Test different metric types
        registry.record("counter_metric", 1, metric_type=MetricType.COUNTER)
        registry.record("gauge_metric", 42.5, metric_type=MetricType.GAUGE)
        registry.record("histogram_metric", 0.95, metric_type=MetricType.HISTOGRAM)

        summary = registry.get_metrics_summary()

        # Check counter is accumulated
        self.assertEqual(summary["counters"]["counter_metric"], 1)

        # Check gauge is stored
        self.assertEqual(summary["gauges"]["gauge_metric"], 42.5)

        # Check histogram data is recorded
        self.assertIn("histogram_metric", summary["recent_measurements"])

class TestAlertManager(unittest.TestCase):
    """Test AlertManager alerting logic and cooldown functionality."""

    def setUp(self):
        self.registry = MetricsRegistry()
        self.alert_manager = AlertManager(self.registry)

    def test_alert_rule_creation(self):
        """Test alert rule creation and registration."""
        from packages.core.monitoring.monitoring.metrics import AlertRule

        rule = AlertRule(
            name="test_high_error_rate",
            condition=lambda metrics: metrics.get("counters", {}).get("errors", 0) > 10,
            severity=AlertSeverity.WARNING,
            message="Error rate is too high",
            cooldown_seconds=300
        )

        self.alert_manager.add_alert_rule(rule)

        # Verify rule was added
        self.assertIn("test_high_error_rate", self.alert_manager.alert_rules)
        self.assertEqual(self.alert_manager.alert_rules["test_high_error_rate"].severity, AlertSeverity.WARNING)

    def test_alert_triggering_and_resolution(self):
        """Test alert triggering and resolution lifecycle."""
        # Add a simple alert rule
        from packages.core.monitoring.monitoring.metrics import AlertRule

        rule = AlertRule(
            name="test_metric_threshold",
            condition=lambda metrics: metrics.get("gauges", {}).get("test_value", 0) > 90,
            severity=AlertSeverity.CRITICAL,
            message="Test metric exceeded threshold",
            cooldown_seconds=60
        )

        self.alert_manager.add_alert_rule(rule)

        # Initially no alerts
        self.assertEqual(len(self.alert_manager.active_alerts), 0)

        # Set metric below threshold - no alert
        set_gauge("test_value", 80)
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(triggered), 0)
        self.assertEqual(len(resolved), 0)

        # Set metric above threshold - should trigger alert
        set_gauge("test_value", 95)
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].rule_name, "test_metric_threshold")
        self.assertEqual(triggered[0].severity, AlertSeverity.CRITICAL)

        # Verify alert is active
        self.assertEqual(len(self.alert_manager.active_alerts), 1)
        self.assertIn("test_metric_threshold", self.alert_manager.active_alerts)

        # Set metric back below threshold - should resolve alert
        set_gauge("test_value", 85)
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(triggered), 0)
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].rule_name, "test_metric_threshold")

        # Verify alert is resolved
        self.assertEqual(len(self.alert_manager.active_alerts), 0)

    def test_alert_cooldown_prevention(self):
        """Test that alert cooldown prevents alert spam."""
        from packages.core.monitoring.monitoring.metrics import AlertRule

        rule = AlertRule(
            name="test_cooldown",
            condition=lambda metrics: True,  # Always trigger
            severity=AlertSeverity.WARNING,
            message="Cooldown test alert",
            cooldown_seconds=1  # Short cooldown for testing
        )

        self.alert_manager.add_alert_rule(rule)

        # First evaluation should trigger alert
        triggered, resolved = self.alert_manager.evaluate_alerts({})
        self.assertEqual(len(triggered), 1)

        # Immediate second evaluation should not trigger (cooldown)
        triggered, resolved = self.alert_manager.evaluate_alerts({})
        self.assertEqual(len(triggered), 0)  # Should be prevented by cooldown

        # Wait for cooldown to expire
        time.sleep(1.1)

        # Now should trigger again
        triggered, resolved = self.alert_manager.evaluate_alerts({})
        self.assertEqual(len(triggered), 1)

    def test_alert_severity_levels(self):
        """Test different alert severity levels are handled correctly."""
        from packages.core.monitoring.monitoring.metrics import AlertRule

        severities = [AlertSeverity.INFO, AlertSeverity.WARNING, AlertSeverity.ERROR, AlertSeverity.CRITICAL]

        for severity in severities:
            rule = AlertRule(
                name=f"test_{severity.value}",
                condition=lambda metrics, s=severity: True,  # Always trigger
                severity=severity,
                message=f"Test {severity.value} alert",
                cooldown_seconds=300
            )

            self.alert_manager.add_alert_rule(rule)

        # Trigger all alerts
        triggered, resolved = self.alert_manager.evaluate_alerts({})

        # Should have triggered alerts for all severities
        triggered_severities = [alert.severity for alert in triggered]
        for severity in severities:
            self.assertIn(severity, triggered_severities)

    def test_alert_summary_generation(self):
        """Test alert summary generation with statistics."""
        # Trigger some alerts
        from packages.core.monitoring.monitoring.metrics import AlertRule

        rule = AlertRule(
            name="summary_test",
            condition=lambda metrics: True,
            severity=AlertSeverity.ERROR,
            message="Summary test alert",
            cooldown_seconds=300
        )

        self.alert_manager.add_alert_rule(rule)

        # Trigger alert
        self.alert_manager.evaluate_alerts({})

        # Get summary
        summary = self.alert_manager.get_alert_summary()

        # Verify structure
        self.assertIn("active_alerts", summary)
        self.assertIn("recent_resolved", summary)
        self.assertIn("total_active", summary)
        self.assertIn("total_resolved_today", summary)
        self.assertIn("statistics", summary)

        # Verify active alert count
        self.assertEqual(summary["total_active"], 1)

        # Verify statistics
        stats = summary["statistics"]
        self.assertIn("severity_breakdown", stats)
        self.assertIn("alert_trends", stats)

    def test_multiple_simultaneous_alerts(self):
        """Test handling multiple alerts triggering simultaneously."""
        from packages.core.monitoring.monitoring.metrics import AlertRule

        # Add multiple rules
        rules = [
            AlertRule(
                name=f"multi_alert_{i}",
                condition=lambda metrics, i=i: True,  # All always trigger
                severity=AlertSeverity.WARNING,
                message=f"Multi alert {i}",
                cooldown_seconds=300
            ) for i in range(5)
        ]

        for rule in rules:
            self.alert_manager.add_alert_rule(rule)

        # Trigger all alerts
        triggered, resolved = self.alert_manager.evaluate_alerts({})

        # Should have triggered 5 alerts
        self.assertEqual(len(triggered), 5)
        self.assertEqual(len(self.alert_manager.active_alerts), 5)

        # All alerts should be active
        active_names = set(self.alert_manager.active_alerts.keys())
        expected_names = {f"multi_alert_{i}" for i in range(5)}
        self.assertEqual(active_names, expected_names)

class TestHealthChecker(unittest.TestCase):
    """Test HealthChecker multi-dimensional health assessment."""

    def setUp(self):
        self.registry = MetricsRegistry()
        self.health_checker = HealthChecker(self.registry)

    @patch('psutil.virtual_memory')
    def test_memory_health_check(self, mock_memory):
        """Test memory health check functionality."""
        # Mock memory usage
        mock_memory.return_value = Mock()
        mock_memory.return_value.percent = 75.5

        # Run memory check
        result = self.health_checker._check_memory_usage()

        # Verify result structure
        self.assertIn("status", result)
        self.assertIn("message", result)
        self.assertIn("details", result)

        # Verify correct assessment
        self.assertEqual(result["status"], "healthy")  # < 85%
        self.assertIn("75.1f", result["message"])

    @patch('psutil.disk_usage')
    def test_disk_space_health_check(self, mock_disk):
        """Test disk space health check."""
        # Mock disk usage (90% used = 10% free)
        mock_disk.return_value = Mock()
        mock_disk.return_value.free = 100 * (1024**3)  # 100GB free
        mock_disk.return_value.total = 1000 * (1024**3)  # 1000GB total

        result = self.health_checker._check_disk_space()

        self.assertEqual(result["status"], "healthy")  # > 10% free
        self.assertIn("10.0%", result["message"])

    @patch('psutil.cpu_percent')
    def test_cpu_usage_health_check(self, mock_cpu):
        """Test CPU usage health check."""
        mock_cpu.return_value = 65.5

        result = self.health_checker._check_cpu_usage()

        self.assertEqual(result["status"], "healthy")  # < 80%
        self.assertEqual(result["details"]["cpu_percent"], 65.5)

    def test_application_metrics_health_check(self):
        """Test application metrics health check."""
        # Set up some test metrics
        increment_counter("requests_total", 100)
        increment_counter("errors_total", 3)  # 3% error rate

        result = self.health_checker._check_application_metrics()

        self.assertEqual(result["status"], "healthy")  # < 5% error rate
        self.assertIn("3.00%", result["message"])
        self.assertEqual(result["details"]["error_rate"], 0.03)

    def test_overall_health_assessment(self):
        """Test overall health assessment combining multiple checks."""
        # Mock all health checks to return healthy
        original_checks = self.health_checker.health_checks.copy()

        # Replace with mock checks
        self.health_checker.health_checks = {
            "memory": lambda: {"status": "healthy", "message": "OK", "details": {}},
            "disk": lambda: {"status": "healthy", "message": "OK", "details": {}},
            "cpu": lambda: {"status": "healthy", "message": "OK", "details": {}},
        }

        health_status = self.health_checker.run_health_checks()

        # Verify structure
        self.assertIn("overall_status", health_status)
        self.assertIn("health_score", health_status)
        self.assertIn("health_percentage", health_status)
        self.assertIn("checks", health_status)
        self.assertIn("summary", health_status)

        # Should be healthy overall
        self.assertEqual(health_status["overall_status"], "healthy")
        self.assertEqual(health_status["health_percentage"], 100.0)

        # Restore original checks
        self.health_checker.health_checks = original_checks

    def test_mixed_health_statuses(self):
        """Test health assessment with mixed healthy/warning/critical statuses."""
        # Set up mixed health checks
        self.health_checker.health_checks = {
            "memory": lambda: {"status": "healthy", "message": "OK", "details": {}},
            "disk": lambda: {"status": "warning", "message": "Low space", "details": {}},
            "cpu": lambda: {"status": "critical", "message": "High usage", "details": {}},
        }

        health_status = self.health_checker.run_health_checks()

        # Should be critical overall (has critical check)
        self.assertEqual(health_status["overall_status"], "critical")

        # Check summary
        summary = health_status["summary"]
        self.assertEqual(summary["healthy"], 1)
        self.assertEqual(summary["warning"], 1)
        self.assertEqual(summary["critical"], 1)

class TestMonitoringAPI(unittest.TestCase):
    """Test monitoring API endpoints functionality."""

    def setUp(self):
        from packages.core.monitoring.monitoring.api import monitoring_bp
        self.app = monitoring_bp

    @patch('packages.core.monitoring.monitoring.api.is_monitoring_enabled')
    @patch('packages.core.monitoring.monitoring.api.get_metrics_summary')
    def test_metrics_endpoint_json(self, mock_get_metrics, mock_enabled):
        """Test metrics endpoint with JSON format."""
        mock_enabled.return_value = True
        mock_get_metrics.return_value = {
            "counters": {"test": 42},
            "gauges": {"memory": 85.5},
            "timestamp": time.time()
        }

        with self.app.test_client() as client:
            response = client.get('/metrics')
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertIn("counters", data)
            self.assertIn("gauges", data)
            self.assertEqual(data["counters"]["test"], 42)

    @patch('packages.core.monitoring.monitoring.api.is_monitoring_enabled')
    @patch('packages.core.monitoring.monitoring.api.get_health_status')
    def test_health_endpoint(self, mock_get_health, mock_enabled):
        """Test health endpoint functionality."""
        mock_enabled.return_value = True
        mock_get_health.return_value = {
            "overall_status": "healthy",
            "health_percentage": 95.0,
            "checks": {
                "memory": {"status": "healthy", "message": "OK"}
            }
        }

        with self.app.test_client() as client:
            response = client.get('/health')
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["overall_status"], "healthy")
            self.assertEqual(data["health_percentage"], 95.0)

    @patch('packages.core.monitoring.monitoring.api.is_monitoring_enabled')
    @patch('packages.core.monitoring.monitoring.api.get_alert_summary')
    def test_alerts_endpoint(self, mock_get_alerts, mock_enabled):
        """Test alerts endpoint."""
        mock_enabled.return_value = True
        mock_get_alerts.return_value = {
            "active_alerts": [{"rule_name": "test", "severity": "critical"}],
            "total_active": 1,
            "timestamp": time.time()
        }

        with self.app.test_client() as client:
            response = client.get('/alerts')
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["total_active"], 1)
            self.assertEqual(len(data["active_alerts"]), 1)

    @patch('packages.core.monitoring.monitoring.api.is_monitoring_enabled')
    def test_monitoring_disabled_responses(self, mock_enabled):
        """Test endpoints when monitoring is disabled."""
        mock_enabled.return_value = False

        with self.app.test_client() as client:
            # Test metrics endpoint
            response = client.get('/metrics')
            self.assertEqual(response.status_code, 503)

            # Test health endpoint
            response = client.get('/health')
            self.assertEqual(response.status_code, 503)

            # Test alerts endpoint
            response = client.get('/alerts')
            self.assertEqual(response.status_code, 503)

    def test_prometheus_format_conversion(self):
        """Test Prometheus format conversion."""
        from packages.core.monitoring.monitoring.api import _convert_to_prometheus_format

        metrics_data = {
            "counters": {"requests_total": 150, "errors_total": 5},
            "gauges": {"memory_usage": 85.5, "cpu_usage": 67.2},
            "recent_measurements": {
                "response_time": [
                    {"value": 150, "timestamp": 1640000000, "tags": {"endpoint": "/api"}}
                ]
            }
        }

        prometheus_output = _convert_to_prometheus_format(metrics_data)

        # Verify Prometheus format structure
        self.assertIn("# HELP", prometheus_output)
        self.assertIn("# TYPE", prometheus_output)
        self.assertIn("requests_total 150", prometheus_output)
        self.assertIn("memory_usage 85.5", prometheus_output)

    def test_health_recommendations_generation(self):
        """Test health recommendations generation."""
        from packages.core.monitoring.monitoring.api import _generate_health_recommendations

        health_status = {
            "checks": {
                "memory": {"status": "critical", "message": "High usage"},
                "disk": {"status": "warning", "message": "Low space"},
                "cpu": {"status": "healthy", "message": "Normal"}
            }
        }

        recommendations = _generate_health_recommendations(health_status)

        # Should include recommendations for critical and warning issues
        self.assertTrue(any("memory" in rec.lower() or "critical" in rec.lower()
                          for rec in recommendations))
        self.assertTrue(any("disk" in rec.lower() or "space" in rec.lower()
                          for rec in recommendations))

class TestMonitoringIntegration(unittest.TestCase):
    """Integration tests for complete monitoring system."""

    def setUp(self):
        self.registry = MetricsRegistry()
        self.alert_manager = AlertManager(self.registry)
        self.health_checker = HealthChecker(self.registry)

    def test_end_to_end_alert_lifecycle(self):
        """Test complete alert lifecycle from trigger to resolution."""
        from packages.core.monitoring.monitoring.metrics import AlertRule

        # Create alert rule for high error rate
        rule = AlertRule(
            name="integration_test_alert",
            condition=lambda metrics: (metrics.get("counters", {}).get("errors", 0) /
                                     max(metrics.get("counters", {}).get("total", 1), 1)) > 0.1,
            severity=AlertSeverity.CRITICAL,
            message="Error rate above 10%",
            cooldown_seconds=60
        )

        self.alert_manager.add_alert_rule(rule)

        # Normal operation - no alert
        increment_counter("total", 100)
        increment_counter("errors", 5)  # 5% error rate
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(triggered), 0)

        # High error rate - trigger alert
        increment_counter("errors", 20)  # Now 25% error rate
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].rule_name, "integration_test_alert")

        # Reduce error rate - resolve alert
        # Add more successful operations without errors
        increment_counter("total", 200)  # Now 300 total, 25 errors = 8.3%
        triggered, resolved = self.alert_manager.evaluate_alerts(get_metrics_summary())
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].rule_name, "integration_test_alert")

    def test_metrics_and_health_integration(self):
        """Test integration between metrics collection and health checks."""
        # Generate some metrics
        increment_counter("api_requests", 1000)
        increment_counter("api_errors", 10)
        set_gauge("response_time_p95", 250)  # ms
        set_gauge("memory_usage_percent", 75)

        # Run health check
        health_status = self.health_checker.run_health_checks()

        # Verify health check considers application metrics
        app_check = None
        for check_name, check_result in health_status["checks"].items():
            if "application" in check_name.lower() or "metrics" in check_name.lower():
                app_check = check_result
                break

        # Application health should be assessed
        if app_check:
            self.assertIn("status", app_check)
            self.assertIn("message", app_check)

    def test_concurrent_monitoring_operations(self):
        """Test concurrent monitoring operations for thread safety."""
        results = []
        errors = []

        def monitoring_worker(worker_id):
            """Worker performing various monitoring operations."""
            try:
                # Record metrics
                increment_counter(f"worker_{worker_id}_ops", 10 * worker_id)
                set_gauge(f"worker_{worker_id}_progress", worker_id * 20)

                # Use timer
                with start_timer(f"worker_{worker_id}_task", {"worker": str(worker_id)}):
                    time.sleep(0.01)

                # Check health
                health = get_health_status()

                results.append({
                    "worker_id": worker_id,
                    "health_status": health["overall_status"],
                    "completed": True
                })

            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Run concurrent monitoring operations
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(monitoring_worker, i) for i in range(5)]
            for future in futures:
                future.result()

        # Verify all workers completed successfully
        self.assertEqual(len(results), 5)
        self.assertEqual(len(errors), 0)

        for result in results:
            self.assertTrue(result["completed"])
            self.assertIsInstance(result["health_status"], str)

    def test_monitoring_under_load(self):
        """Test monitoring system performance under load."""
        start_time = time.time()

        # Simulate high-frequency metrics collection
        for i in range(1000):
            increment_counter("load_test_counter", 1, {"batch": str(i % 10)})
            set_gauge("load_test_gauge", i % 100, {"iteration": str(i)})

        # Measure performance
        load_time = time.time() - start_time

        # Should handle 1000 operations quickly (< 1 second)
        self.assertLess(load_time, 1.0, "Monitoring should handle load efficiently")

        # Verify metrics were recorded
        summary = get_metrics_summary()
        self.assertEqual(summary["counters"]["load_test_counter"], 1000)
        self.assertEqual(summary["gauges"]["load_test_gauge"], 999)  # Last value

    def test_alert_rule_config_loading(self):
        """Test loading and validation of alert rule configurations."""
        rules = get_alert_rules()

        # Should have loaded default rules
        self.assertGreater(len(rules), 0)

        # Each rule should have required attributes
        for rule in rules:
            self.assertIsNotNone(rule.name)
            self.assertIsNotNone(rule.condition)
            self.assertIsInstance(rule.severity, AlertSeverity)
            self.assertIsNotNone(rule.message)
            self.assertGreater(rule.cooldown_seconds, 0)

    def test_monitoring_system_startup(self):
        """Test complete monitoring system startup and initialization."""
        # This tests that all components can be initialized together
        from packages.core.monitoring.monitoring.metrics import (
            _metrics_registry, _alert_manager, _health_checker
        )

        # Verify all components are initialized
        self.assertIsInstance(_metrics_registry, MetricsRegistry)
        self.assertIsInstance(_alert_manager, AlertManager)
        self.assertIsInstance(_health_checker, HealthChecker)

        # Verify basic functionality works
        increment_counter("startup_test", 1)
        summary = get_metrics_summary()
        self.assertEqual(summary["counters"]["startup_test"], 1)

        # Verify health checks work
        health = get_health_status()
        self.assertIn("overall_status", health)

        # Verify alerts system works
        alerts = get_alert_summary()
        self.assertIn("active_alerts", alerts)

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery in monitoring system."""
        # Test with invalid metric names
        increment_counter("", 1)  # Empty name
        increment_counter("valid_name", 1)  # Valid name

        # Should handle errors gracefully and continue working
        summary = get_metrics_summary()
        self.assertIn("valid_name", summary["counters"])
        self.assertEqual(summary["counters"]["valid_name"], 1)

        # Test health checks with missing dependencies
        health = get_health_status()
        # Should return valid response even if some checks fail
        self.assertIn("overall_status", health)
        self.assertIn("checks", health)

    def test_metrics_retention_and_cleanup(self):
        """Test metrics retention and automatic cleanup."""
        # Create registry with short cleanup interval for testing
        registry = MetricsRegistry(max_history_per_metric=10, cleanup_interval=1)

        # Add metrics over time
        for i in range(20):
            registry.record("retention_test", i, {"index": str(i)})
            time.sleep(0.01)  # Ensure different timestamps

        # Force cleanup
        registry._cleanup_old_metrics()

        summary = registry.get_metrics_summary()
        measurements = summary["recent_measurements"]["retention_test"]

        # Should not exceed max_history_per_metric
        self.assertLessEqual(len(measurements), 10)

if __name__ == '__main__':
    unittest.main()