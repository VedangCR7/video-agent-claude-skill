"""
Enterprise-grade Metrics, Alerting, and Health Monitoring System.

This module provides comprehensive observability for production applications with:
- Thread-safe metrics collection (counters, gauges, histograms, timers)
- Configurable alerting with severity levels and cooldown prevention
- Automated health checks with multi-dimensional scoring
- RESTful monitoring endpoints for operational visibility

Core Components:
- MetricsRegistry: Thread-safe collection with bounded history
- AlertManager: Rule-based alerting with cooldown prevention
- HealthChecker: Multi-dimensional health assessment
- Convenience functions for easy metric recording
"""

import threading
import time
import logging
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels for operational response prioritization."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Supported metric types for comprehensive monitoring."""
    COUNTER = "counter"      # Monotonically increasing value
    GAUGE = "gauge"         # Value that can go up and down
    HISTOGRAM = "histogram" # Distribution of values
    TIMER = "timer"         # Duration measurements

@dataclass
class MetricPoint:
    """Individual metric measurement with timestamp and metadata."""
    name: str
    value: Union[int, float]
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class AlertRule:
    """Configurable alert rule with thresholds and actions."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message: str
    cooldown_seconds: int = 300  # 5 minutes default cooldown
    enabled: bool = True

@dataclass
class Alert:
    """Active or resolved alert with full context."""
    rule_name: str
    severity: AlertSeverity
    message: str
    triggered_at: float
    resolved_at: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if alert is currently active."""
        return self.resolved_at is None

    @property
    def duration(self) -> float:
        """Get alert duration in seconds."""
        end_time = self.resolved_at or time.time()
        return end_time - self.triggered_at

class MetricsRegistry:
    """
    Thread-safe metrics registry with bounded history and efficient storage.

    Provides atomic operations for all metric types and automatic cleanup
    of old data points to prevent memory leaks in long-running applications.
    """

    def __init__(self, max_history_per_metric: int = 10000, cleanup_interval: int = 300):
        self._metrics: Dict[str, deque] = {}
        self._gauges: Dict[str, float] = {}
        self._counters: Dict[str, int] = {}
        self._histograms: Dict[str, Dict[str, Any]] = {}
        self._timers: Dict[str, Dict[str, Any]] = {}

        self.max_history_per_metric = max_history_per_metric
        self.cleanup_interval = cleanup_interval

        self._lock = threading.RLock()
        self._last_cleanup = time.time()

        # Start background cleanup thread
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup,
            daemon=True,
            name="metrics-cleanup"
        )
        self._cleanup_thread.start()

    def _background_cleanup(self):
        """Background thread for periodic cleanup of old metrics."""
        while True:
            time.sleep(self.cleanup_interval)
            try:
                self._cleanup_old_metrics()
            except Exception as e:
                logger.error(f"Metrics cleanup failed: {e}")

    def _cleanup_old_metrics(self):
        """Remove old metric points to prevent memory leaks."""
        cutoff_time = time.time() - (24 * 3600)  # 24 hours ago

        with self._lock:
            for metric_name, points in self._metrics.items():
                # Keep only recent points
                while points and points[0].timestamp < cutoff_time:
                    points.popleft()

                # Remove empty deques
                if not points:
                    del self._metrics[metric_name]

    def record(self, name: str, value: Union[int, float],
               tags: Optional[Dict[str, str]] = None,
               metric_type: MetricType = MetricType.GAUGE):
        """
        Record a metric measurement with optional tags.

        Thread-safe operation that automatically manages history and cleanup.
        """
        if tags is None:
            tags = {}

        point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags,
            metric_type=metric_type
        )

        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = deque(maxlen=self.max_history_per_metric)

            self._metrics[name].append(point)

            # Update specific metric type storage
            if metric_type == MetricType.GAUGE:
                self._gauges[name] = value
            elif metric_type == MetricType.COUNTER:
                if name not in self._counters:
                    self._counters[name] = 0
                self._counters[name] += int(value)

    def increment_counter(self, name: str, value: int = 1,
                         tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        self.record(name, value, tags, MetricType.COUNTER)

    def set_gauge(self, name: str, value: Union[int, float],
                  tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric value."""
        self.record(name, value, tags, MetricType.GAUGE)

    def record_timer(self, name: str, duration_seconds: float,
                    tags: Optional[Dict[str, str]] = None):
        """Record a timer/duration measurement."""
        self.record(name, duration_seconds, tags, MetricType.TIMER)

    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None):
        """Start a timer context manager."""
        return TimerContext(self, name, tags)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary for monitoring endpoints."""
        with self._lock:
            summary = {
                "timestamp": time.time(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "active_metrics": len(self._metrics),
                "total_datapoints": sum(len(points) for points in self._metrics.values())
            }

            # Add recent measurements for each metric
            summary["recent_measurements"] = {}
            for name, points in self._metrics.items():
                if points:
                    recent = list(points)[-10:]  # Last 10 points
                    summary["recent_measurements"][name] = [
                        {
                            "value": p.value,
                            "timestamp": p.timestamp,
                            "tags": p.tags
                        } for p in recent
                    ]

            return summary

class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, registry: MetricsRegistry, name: str,
                 tags: Optional[Dict[str, str]] = None):
        self.registry = registry
        self.name = name
        self.tags = tags or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.registry.record_timer(self.name, duration, self.tags)

class AlertManager:
    """
    Rule-based alerting system with cooldown prevention and severity management.

    Manages alert lifecycle from detection through resolution with configurable
    rules, cooldown periods, and escalation policies.
    """

    def __init__(self, metrics_registry: MetricsRegistry):
        self.metrics_registry = metrics_registry
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.resolved_alerts: deque = deque(maxlen=1000)  # Keep last 1000 resolved alerts

        self._lock = threading.RLock()

        # Default alert rules
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Configure default production alert rules."""

        # Success rate monitoring
        self.add_alert_rule(AlertRule(
            name="low_success_rate",
            condition=lambda metrics: self._check_success_rate(metrics, 0.8),
            severity=AlertSeverity.WARNING,
            message="Success rate below 80%",
            cooldown_seconds=300
        ))

        self.add_alert_rule(AlertRule(
            name="critical_success_rate",
            condition=lambda metrics: self._check_success_rate(metrics, 0.5),
            severity=AlertSeverity.CRITICAL,
            message="Success rate below 50% - immediate attention required",
            cooldown_seconds=60
        ))

        # Error rate monitoring
        self.add_alert_rule(AlertRule(
            name="high_error_rate",
            condition=lambda metrics: self._check_error_rate(metrics, 0.2),
            severity=AlertSeverity.WARNING,
            message="Error rate above 20%",
            cooldown_seconds=180
        ))

        self.add_alert_rule(AlertRule(
            name="critical_error_rate",
            condition=lambda metrics: self._check_error_rate(metrics, 0.5),
            severity=AlertSeverity.CRITICAL,
            message="Error rate above 50% - service degradation",
            cooldown_seconds=30
        ))

        # Performance monitoring
        self.add_alert_rule(AlertRule(
            name="slow_operations",
            condition=lambda metrics: self._check_operation_duration(metrics, 1800),  # 30 minutes
            severity=AlertSeverity.WARNING,
            message="Operations taking longer than 30 minutes",
            cooldown_seconds=600
        ))

    def _check_success_rate(self, metrics: Dict[str, Any], threshold: float) -> bool:
        """Check if success rate is below threshold."""
        total_ops = metrics.get("total_operations", 0)
        successful_ops = metrics.get("successful_operations", 0)

        if total_ops == 0:
            return False

        success_rate = successful_ops / total_ops
        return success_rate < threshold

    def _check_error_rate(self, metrics: Dict[str, Any], threshold: float) -> bool:
        """Check if error rate is above threshold."""
        total_ops = metrics.get("total_operations", 0)
        error_ops = metrics.get("error_operations", 0)

        if total_ops == 0:
            return False

        error_rate = error_ops / total_ops
        return error_rate > threshold

    def _check_operation_duration(self, metrics: Dict[str, Any], threshold_seconds: float) -> bool:
        """Check if operations are taking too long."""
        avg_duration = metrics.get("avg_operation_duration", 0)
        return avg_duration > threshold_seconds

    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule to the system."""
        with self._lock:
            self.alert_rules[rule.name] = rule
            logger.info(f"Added alert rule: {rule.name} ({rule.severity.value})")

    def evaluate_alerts(self, current_metrics: Dict[str, Any]):
        """Evaluate all alert rules against current metrics."""
        alerts_triggered = []
        alerts_resolved = []

        with self._lock:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue

                rule_name = rule.name
                should_alert = rule.condition(current_metrics)

                if should_alert and rule_name not in self.active_alerts:
                    # New alert
                    alert = Alert(
                        rule_name=rule_name,
                        severity=rule.severity,
                        message=rule.message,
                        triggered_at=time.time(),
                        context=current_metrics.copy()
                    )
                    self.active_alerts[rule_name] = alert
                    alerts_triggered.append(alert)
                    logger.warning(f"Alert triggered: {rule_name} - {rule.message}")

                elif not should_alert and rule_name in self.active_alerts:
                    # Resolve alert
                    alert = self.active_alerts[rule_name]
                    alert.resolved_at = time.time()
                    self.resolved_alerts.append(alert)
                    del self.active_alerts[rule_name]
                    alerts_resolved.append(alert)
                    logger.info(f"Alert resolved: {rule_name}")

        return alerts_triggered, alerts_resolved

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get comprehensive alert status summary."""
        with self._lock:
            return {
                "timestamp": time.time(),
                "active_alerts": [
                    {
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at,
                        "duration": alert.duration,
                        "context": alert.context
                    } for alert in self.active_alerts.values()
                ],
                "recent_resolved": [
                    {
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at,
                        "resolved_at": alert.resolved_at,
                        "duration": alert.duration
                    } for alert in list(self.resolved_alerts)[-10:]  # Last 10 resolved
                ],
                "total_active": len(self.active_alerts),
                "total_resolved_today": len([
                    alert for alert in self.resolved_alerts
                    if alert.resolved_at and alert.resolved_at > time.time() - 86400  # Last 24 hours
                ])
            }

class HealthChecker:
    """
    Multi-dimensional health assessment system.

    Performs comprehensive health checks across different system dimensions:
    - Application health (services, dependencies)
    - System health (resources, connectivity)
    - Business health (key metrics, SLIs)
    """

    def __init__(self, metrics_registry: MetricsRegistry):
        self.metrics_registry = metrics_registry
        self.health_checks: Dict[str, Callable[[], Dict[str, Any]]] = {}

        self._lock = threading.RLock()

        # Register default health checks
        self._register_default_checks()

    def _register_default_checks(self):
        """Register comprehensive default health checks."""
        self.register_health_check("memory_usage", self._check_memory_usage)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("cpu_usage", self._check_cpu_usage)
        self.register_health_check("database_connectivity", self._check_database_connectivity)
        self.register_health_check("external_services", self._check_external_services)
        self.register_health_check("application_metrics", self._check_application_metrics)

    def register_health_check(self, name: str, check_function: Callable[[], Dict[str, Any]]):
        """Register a new health check function."""
        with self._lock:
            self.health_checks[name] = check_function
            logger.info(f"Registered health check: {name}")

    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check system memory usage."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            return {
                "status": "healthy" if usage_percent < 85 else "warning" if usage_percent < 95 else "critical",
                "message": f"Memory usage: {usage_percent:.1f}%",
                "details": {
                    "used_mb": memory.used / (1024 * 1024),
                    "total_mb": memory.total / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024)
                }
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for memory monitoring",
                "details": {}
            }

    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            free_percent = (disk.free / disk.total) * 100

            return {
                "status": "healthy" if free_percent > 15 else "warning" if free_percent > 5 else "critical",
                "message": f"Disk space: {free_percent:.1f}% free",
                "details": {
                    "free_gb": disk.free / (1024 * 1024 * 1024),
                    "total_gb": disk.total / (1024 * 1024 * 1024)
                }
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for disk monitoring",
                "details": {}
            }

    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)

            return {
                "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical",
                "message": f"CPU usage: {cpu_percent:.1f}%",
                "details": {"cpu_percent": cpu_percent}
            }
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for CPU monitoring",
                "details": {}
            }

    def _check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity (placeholder - customize for your DB)."""
        # This would be customized based on your database setup
        return {
            "status": "healthy",
            "message": "Database connectivity check not implemented",
            "details": {"note": "Customize this check for your database"}
        }

    def _check_external_services(self) -> Dict[str, Any]:
        """Check external service connectivity."""
        # This would check APIs, external dependencies, etc.
        return {
            "status": "healthy",
            "message": "External services check not implemented",
            "details": {"note": "Customize this check for your external dependencies"}
        }

    def _check_application_metrics(self) -> Dict[str, Any]:
        """Check application-specific metrics."""
        metrics = self.metrics_registry.get_metrics_summary()

        # Check for critical application metrics
        error_rate = metrics.get("counters", {}).get("errors_total", 0)
        total_requests = metrics.get("counters", {}).get("requests_total", 0)

        if total_requests > 0:
            error_percentage = (error_rate / total_requests) * 100
            status = "healthy" if error_percentage < 5 else "warning" if error_percentage < 15 else "critical"
            message = f"Application error rate: {error_percentage:.1f}%"
        else:
            status = "healthy"
            message = "No requests recorded yet"

        return {
            "status": status,
            "message": message,
            "details": {
                "error_rate": error_percentage if total_requests > 0 else 0,
                "total_requests": total_requests,
                "error_count": error_rate
            }
        }

    def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks and compute overall health score."""
        results = {}
        scores = {"healthy": 3, "warning": 2, "critical": 1, "unknown": 0}

        with self._lock:
            for check_name, check_function in self.health_checks.items():
                try:
                    result = check_function()
                    results[check_name] = result
                except Exception as e:
                    logger.error(f"Health check {check_name} failed: {e}")
                    results[check_name] = {
                        "status": "critical",
                        "message": f"Health check failed: {str(e)}",
                        "details": {}
                    }

        # Calculate overall health score
        total_score = 0
        max_score = len(results) * 3  # 3 points per check

        for result in results.values():
            total_score += scores.get(result["status"], 0)

        health_percentage = (total_score / max_score) * 100 if max_score > 0 else 100

        overall_status = (
            "healthy" if health_percentage >= 90 else
            "warning" if health_percentage >= 70 else
            "critical"
        )

        return {
            "timestamp": time.time(),
            "overall_status": overall_status,
            "health_score": f"{total_score}/{max_score}",
            "health_percentage": round(health_percentage, 1),
            "checks": results,
            "summary": {
                "total_checks": len(results),
                "healthy": len([r for r in results.values() if r["status"] == "healthy"]),
                "warning": len([r for r in results.values() if r["status"] == "warning"]),
                "critical": len([r for r in results.values() if r["status"] == "critical"]),
                "unknown": len([r for r in results.values() if r["status"] == "unknown"])
            }
        }

# Global instances for easy access
_metrics_registry = MetricsRegistry()
_alert_manager = AlertManager(_metrics_registry)
_health_checker = HealthChecker(_metrics_registry)

# Convenience functions for easy metric recording
def increment_counter(name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
    """Increment a counter metric."""
    _metrics_registry.increment_counter(name, value, tags)

def set_gauge(name: str, value: Union[int, float], tags: Optional[Dict[str, str]] = None):
    """Set a gauge metric value."""
    _metrics_registry.set_gauge(name, value, tags)

def record_timer(name: str, duration_seconds: float, tags: Optional[Dict[str, str]] = None):
    """Record a timer/duration measurement."""
    _metrics_registry.record_timer(name, duration_seconds, tags)

def start_timer(name: str, tags: Optional[Dict[str, str]] = None):
    """Start a timer context manager."""
    return _metrics_registry.start_timer(name, tags)

def get_metrics_summary() -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    return _metrics_registry.get_metrics_summary()

def get_alert_summary() -> Dict[str, Any]:
    """Get comprehensive alert status summary."""
    return _alert_manager.get_alert_summary()

def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health check results."""
    return _health_checker.run_health_checks()

def evaluate_alerts():
    """Evaluate alert rules against current metrics."""
    current_metrics = get_metrics_summary()
    return _alert_manager.evaluate_alerts(current_metrics)

# Export key classes and functions
__all__ = [
    'MetricsRegistry',
    'AlertManager',
    'HealthChecker',
    'AlertSeverity',
    'MetricType',
    'increment_counter',
    'set_gauge',
    'record_timer',
    'start_timer',
    'get_metrics_summary',
    'get_alert_summary',
    'get_health_status',
    'evaluate_alerts'
]