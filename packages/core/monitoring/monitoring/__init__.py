"""Core monitoring system for enterprise applications."""

from .metrics import (
    MetricsRegistry,
    AlertManager,
    HealthChecker,
    AlertSeverity,
    MetricType,
    increment_counter,
    set_gauge,
    record_timer,
    start_timer,
    get_metrics_summary,
    get_alert_summary,
    get_health_status,
    evaluate_alerts
)

from .metrics_config import (
    ALERT_RULES_CONFIG,
    CIRCUIT_BREAKER_CONFIG,
    PERFORMANCE_THRESHOLDS,
    HEALTH_CHECK_CONFIG,
    METRICS_CONFIG,
    NOTIFICATION_CONFIG,
    get_alert_rules,
    get_circuit_breaker_config,
    get_performance_thresholds,
    is_monitoring_enabled
)

# Optional Flask-dependent imports
try:
    from .api import (
        monitoring_bp,
        register_monitoring_endpoints,
        get_monitoring_routes
    )
    from .server import (
        create_monitoring_app,
        run_monitoring_server
    )
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Provide stubs when Flask is not available
    monitoring_bp = None
    def register_monitoring_endpoints(app): pass
    def get_monitoring_routes(): return []
    def create_monitoring_app(): return None
    def run_monitoring_server(*args, **kwargs): pass

from .server import (
    create_monitoring_app,
    run_monitoring_server
)

# Conditionally include Flask-dependent items
__all__ = [
    # Core classes
    'MetricsRegistry',
    'AlertManager',
    'HealthChecker',
    'AlertSeverity',
    'MetricType',

    # Convenience functions
    'increment_counter',
    'set_gauge',
    'record_timer',
    'start_timer',
    'get_metrics_summary',
    'get_alert_summary',
    'get_health_status',
    'evaluate_alerts',

    # Configuration
    'ALERT_RULES_CONFIG',
    'CIRCUIT_BREAKER_CONFIG',
    'PERFORMANCE_THRESHOLDS',
    'HEALTH_CHECK_CONFIG',
    'METRICS_CONFIG',
    'NOTIFICATION_CONFIG',
    'get_alert_rules',
    'get_circuit_breaker_config',
    'get_performance_thresholds',
    'is_monitoring_enabled',
]

# Only include Flask-dependent items if available
if FLASK_AVAILABLE:
    __all__.extend([
        # API
        'monitoring_bp',
        'register_monitoring_endpoints',
        'get_monitoring_routes',

        # Server
        'create_monitoring_app',
        'run_monitoring_server'
    ])