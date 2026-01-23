"""
Monitoring Configuration and Alert Rules.

This module defines comprehensive configuration for the monitoring system:
- Alert rule definitions with customizable thresholds
- Circuit breaker configurations for different components
- Performance monitoring thresholds and policies
- Health check intervals and timeouts

All configurations are designed for production deployment with sensible defaults
and environment-specific overrides.
"""

import os
from typing import Dict, List, Any
from .metrics import AlertRule, AlertSeverity

# Environment-based configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Alert rule configurations with environment-specific thresholds
ALERT_RULES_CONFIG = {
    # Success rate monitoring
    "success_rate_warning": {
        "threshold": 0.85 if IS_PRODUCTION else 0.75,  # Stricter in prod
        "cooldown_seconds": 300,  # 5 minutes
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "success_rate_critical": {
        "threshold": 0.60 if IS_PRODUCTION else 0.50,
        "cooldown_seconds": 60,   # 1 minute - faster response
        "severity": AlertSeverity.CRITICAL,
        "enabled": True
    },

    # Error rate monitoring
    "error_rate_warning": {
        "threshold": 0.15 if IS_PRODUCTION else 0.25,
        "cooldown_seconds": 180,  # 3 minutes
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "error_rate_critical": {
        "threshold": 0.40 if IS_PRODUCTION else 0.50,
        "cooldown_seconds": 30,   # 30 seconds - immediate response
        "severity": AlertSeverity.CRITICAL,
        "enabled": True
    },

    # Performance monitoring
    "slow_sync_operations": {
        "threshold_seconds": 1800 if IS_PRODUCTION else 3600,  # 30min prod, 1hr dev
        "cooldown_seconds": 600,  # 10 minutes
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "very_slow_operations": {
        "threshold_seconds": 3600,  # 1 hour
        "cooldown_seconds": 300,   # 5 minutes
        "severity": AlertSeverity.ERROR,
        "enabled": IS_PRODUCTION  # Only in production
    },

    # Data freshness monitoring
    "data_staleness_warning": {
        "threshold_hours": 6,
        "cooldown_seconds": 1800,  # 30 minutes
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "data_staleness_critical": {
        "threshold_hours": 24,
        "cooldown_seconds": 900,   # 15 minutes
        "severity": AlertSeverity.CRITICAL,
        "enabled": True
    },

    # Resource monitoring
    "high_memory_usage": {
        "threshold_percent": 85,
        "cooldown_seconds": 300,
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "critical_memory_usage": {
        "threshold_percent": 95,
        "cooldown_seconds": 60,
        "severity": AlertSeverity.CRITICAL,
        "enabled": True
    },

    "low_disk_space": {
        "threshold_percent": 85,  # Less than 15% free
        "cooldown_seconds": 1800,  # 30 minutes
        "severity": AlertSeverity.WARNING,
        "enabled": True
    },
    "critical_disk_space": {
        "threshold_percent": 95,  # Less than 5% free
        "cooldown_seconds": 300,   # 5 minutes
        "severity": AlertSeverity.CRITICAL,
        "enabled": True
    },

    "high_cpu_usage": {
        "threshold_percent": 90,
        "cooldown_seconds": 180,
        "severity": AlertSeverity.WARNING,
        "enabled": True
    }
}

# Circuit breaker configurations
CIRCUIT_BREAKER_CONFIG = {
    "default": {
        "failure_threshold": 5,      # Failures before opening
        "recovery_timeout": 60,      # Seconds before attempting recovery
        "success_threshold": 3,      # Successes needed to close
        "monitoring_window": 300    # Rolling window in seconds
    },

    "api_endpoints": {
        "failure_threshold": 3,
        "recovery_timeout": 30,
        "success_threshold": 2,
        "monitoring_window": 180
    },

    "database_connections": {
        "failure_threshold": 5,
        "recovery_timeout": 120,
        "success_threshold": 3,
        "monitoring_window": 600
    },

    "external_services": {
        "failure_threshold": 3,
        "recovery_timeout": 90,
        "success_threshold": 2,
        "monitoring_window": 300
    }
}

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS = {
    "api_response_time": {
        "warning_ms": 1000,    # 1 second
        "critical_ms": 5000,   # 5 seconds
        "p95_target_ms": 500   # 95th percentile target
    },

    "database_query_time": {
        "warning_ms": 100,     # 100ms
        "critical_ms": 1000,   # 1 second
        "p95_target_ms": 50    # 95th percentile target
    },

    "sync_operation_time": {
        "warning_seconds": 300,    # 5 minutes
        "critical_seconds": 1800,  # 30 minutes
        "p95_target_seconds": 120   # 95th percentile target
    },

    "file_processing_time": {
        "warning_seconds": 60,     # 1 minute per file
        "critical_seconds": 300,   # 5 minutes per file
        "p95_target_seconds": 30    # 95th percentile target
    }
}

# Health check configurations
HEALTH_CHECK_CONFIG = {
    "intervals": {
        "memory_check": 60,      # Every minute
        "disk_check": 300,       # Every 5 minutes
        "cpu_check": 30,         # Every 30 seconds
        "database_check": 60,    # Every minute
        "external_services": 180, # Every 3 minutes
        "application_metrics": 30 # Every 30 seconds
    },

    "timeouts": {
        "memory_check": 5,
        "disk_check": 10,
        "cpu_check": 5,
        "database_check": 10,
        "external_services": 15,
        "application_metrics": 5
    },

    "retries": {
        "database_check": 2,
        "external_services": 3,
        "default": 1
    }
}

# Metrics collection configuration
METRICS_CONFIG = {
    "collection": {
        "enabled": True,
        "buffer_size": 10000,      # Max points per metric
        "cleanup_interval": 300,   # 5 minutes
        "retention_days": 7        # Keep metrics for 7 days
    },

    "export": {
        "prometheus_enabled": True,
        "prometheus_port": int(os.getenv("METRICS_PORT", "9090")),
        "json_endpoint": True,
        "csv_export": IS_PRODUCTION  # Only in production
    },

    "sampling": {
        "high_frequency_metrics": 1.0,    # Sample 100%
        "normal_metrics": 0.1,            # Sample 10%
        "debug_metrics": 0.01 if IS_PRODUCTION else 1.0  # 1% in prod, 100% in dev
    }
}

# Notification configurations (for future alerting integrations)
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": IS_PRODUCTION,
        "smtp_server": os.getenv("SMTP_SERVER", ""),
        "recipients": os.getenv("ALERT_EMAILS", "").split(",") if os.getenv("ALERT_EMAILS") else [],
        "critical_only": True
    },

    "slack": {
        "enabled": bool(os.getenv("SLACK_WEBHOOK")),
        "webhook_url": os.getenv("SLACK_WEBHOOK", ""),
        "channel": os.getenv("SLACK_CHANNEL", "#alerts"),
        "username": "Monitoring System"
    },

    "pagerduty": {
        "enabled": bool(os.getenv("PAGERDUTY_KEY")),
        "integration_key": os.getenv("PAGERDUTY_KEY", ""),
        "severity_mapping": {
            AlertSeverity.INFO.value: "info",
            AlertSeverity.WARNING.value: "warning",
            AlertSeverity.ERROR.value: "error",
            AlertSeverity.CRITICAL.value: "critical"
        }
    }
}

# Service discovery and dependency configuration
SERVICE_DISCOVERY = {
    "services": {
        "api_server": {
            "health_endpoint": "/health",
            "metrics_endpoint": "/metrics",
            "timeout": 10
        },
        "database": {
            "connection_check": True,
            "query_timeout": 5,
            "pool_monitoring": True
        },
        "cache": {
            "health_check": True,
            "hit_rate_monitoring": True,
            "memory_usage": True
        },
        "message_queue": {
            "connection_check": True,
            "queue_depth_monitoring": True,
            "processing_rate": True
        }
    },

    "dependencies": {
        "critical": ["database", "cache"],
        "important": ["message_queue"],
        "optional": ["external_apis"]
    }
}

def get_alert_rules() -> List[AlertRule]:
    """
    Generate alert rules from configuration.

    Returns:
        List of configured AlertRule objects
    """
    rules = []

    # Success rate alerts
    success_config = ALERT_RULES_CONFIG["success_rate_warning"]
    rules.append(AlertRule(
        name="success_rate_warning",
        condition=lambda metrics: _check_success_rate(metrics, success_config["threshold"]),
        severity=success_config["severity"],
        message=f"Success rate below {success_config['threshold']*100:.0f}%",
        cooldown_seconds=success_config["cooldown_seconds"],
        enabled=success_config["enabled"]
    ))

    success_critical = ALERT_RULES_CONFIG["success_rate_critical"]
    rules.append(AlertRule(
        name="success_rate_critical",
        condition=lambda metrics: _check_success_rate(metrics, success_critical["threshold"]),
        severity=success_critical["severity"],
        message=f"Success rate below {success_critical['threshold']*100:.0f}% - IMMEDIATE ACTION REQUIRED",
        cooldown_seconds=success_critical["cooldown_seconds"],
        enabled=success_critical["enabled"]
    ))

    # Error rate alerts
    error_config = ALERT_RULES_CONFIG["error_rate_warning"]
    rules.append(AlertRule(
        name="error_rate_warning",
        condition=lambda metrics: _check_error_rate(metrics, error_config["threshold"]),
        severity=error_config["severity"],
        message=f"Error rate above {error_config['threshold']*100:.0f}%",
        cooldown_seconds=error_config["cooldown_seconds"],
        enabled=error_config["enabled"]
    ))

    return rules

def _check_success_rate(metrics: Dict[str, Any], threshold: float) -> bool:
    """Check if success rate is below threshold."""
    total = metrics.get("counters", {}).get("operations_total", 0)
    successful = metrics.get("counters", {}).get("operations_successful", 0)

    if total == 0:
        return False

    return (successful / total) < threshold

def _check_error_rate(metrics: Dict[str, Any], threshold: float) -> bool:
    """Check if error rate is above threshold."""
    total = metrics.get("counters", {}).get("operations_total", 0)
    errors = metrics.get("counters", {}).get("operations_errors", 0)

    if total == 0:
        return False

    return (errors / total) > threshold

def get_circuit_breaker_config(service_name: str) -> Dict[str, Any]:
    """Get circuit breaker configuration for a specific service."""
    return CIRCUIT_BREAKER_CONFIG.get(service_name, CIRCUIT_BREAKER_CONFIG["default"])

def get_performance_thresholds(metric_name: str) -> Dict[str, Any]:
    """Get performance thresholds for a specific metric."""
    return PERFORMANCE_THRESHOLDS.get(metric_name, {})

def is_monitoring_enabled() -> bool:
    """Check if monitoring is enabled."""
    return METRICS_CONFIG["collection"]["enabled"]

def should_sample_metric(metric_name: str, metric_type: str = "normal") -> bool:
    """
    Determine if a metric should be sampled based on configuration.

    Returns True if the metric should be collected, False if it should be skipped.
    """
    import random
    sample_rate = METRICS_CONFIG["sampling"].get(f"{metric_type}_metrics", 1.0)
    return random.random() < sample_rate

# Export configuration objects
__all__ = [
    'ALERT_RULES_CONFIG',
    'CIRCUIT_BREAKER_CONFIG',
    'PERFORMANCE_THRESHOLDS',
    'HEALTH_CHECK_CONFIG',
    'METRICS_CONFIG',
    'NOTIFICATION_CONFIG',
    'SERVICE_DISCOVERY',
    'get_alert_rules',
    'get_circuit_breaker_config',
    'get_performance_thresholds',
    'is_monitoring_enabled',
    'should_sample_metric'
]