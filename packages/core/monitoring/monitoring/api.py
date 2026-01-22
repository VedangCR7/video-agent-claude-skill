"""
Monitoring API Endpoints for Operational Visibility.

Provides RESTful endpoints for metrics, health checks, and alerting:
- GET /metrics - Real-time metrics and statistics
- GET /health - Comprehensive health status with checks
- GET /alerts - Active and resolved alerts

All endpoints return JSON responses suitable for monitoring dashboards
and automated alerting systems.
"""

import json
import time
from typing import Dict, Any, Optional, List

# Optional Flask imports
try:
    from flask import Blueprint, jsonify, request, Response
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Create stub objects for when Flask is not available
    class Blueprint:
        def __init__(self, *args, **kwargs):
            pass
        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    def jsonify(data):
        return json.dumps(data)

    class request:
        args = {}

    class Response:
        def __init__(self, data, mimetype=None):
            self.data = data
            self.mimetype = mimetype

from .metrics import get_metrics_summary, get_alert_summary, get_health_status, evaluate_alerts
from .metrics_config import is_monitoring_enabled

# Create Flask blueprint for monitoring endpoints
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

@monitoring_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """
    Real-time metrics endpoint.

    Returns comprehensive metrics summary including:
    - Counters (monotonically increasing values)
    - Gauges (point-in-time measurements)
    - Recent measurements with timestamps and tags
    - Active metric counts and data points

    Query parameters:
    - format: 'json' (default) or 'prometheus'
    - include_history: 'true' to include full measurement history
    """
    if not is_monitoring_enabled():
        return jsonify({
            "error": "Monitoring is disabled",
            "timestamp": time.time()
        }), 503

    try:
        metrics = get_metrics_summary()
        format_type = request.args.get('format', 'json')
        include_history = request.args.get('include_history', 'false').lower() == 'true'

        if format_type == 'prometheus':
            # Convert to Prometheus format
            prometheus_output = _convert_to_prometheus_format(metrics, include_history)
            return Response(prometheus_output, mimetype='text/plain; charset=utf-8')

        # Filter history if not requested
        if not include_history and 'recent_measurements' in metrics:
            # Keep only summary stats, remove detailed history
            filtered_metrics = metrics.copy()
            filtered_metrics.pop('recent_measurements', None)
            return jsonify(filtered_metrics)

        return jsonify(metrics)

    except Exception as e:
        return jsonify({
            "error": f"Failed to retrieve metrics: {str(e)}",
            "timestamp": time.time()
        }), 500

@monitoring_bp.route('/health', methods=['GET'])
def get_health():
    """
    Comprehensive health check endpoint.

    Performs multi-dimensional health assessment including:
    - System resources (memory, disk, CPU)
    - Application metrics and error rates
    - Database connectivity
    - External service dependencies
    - Overall health score and status

    Response includes detailed check results and recommendations.
    """
    if not is_monitoring_enabled():
        return jsonify({
            "status": "unknown",
            "message": "Monitoring is disabled",
            "timestamp": time.time()
        }), 503

    try:
        health_status = get_health_status()

        # Determine HTTP status code based on health
        status_code = 200  # OK
        if health_status["overall_status"] == "warning":
            status_code = 200  # Still OK, but with warnings
        elif health_status["overall_status"] == "critical":
            status_code = 503  # Service Unavailable

        # Add recommendations based on health status
        health_status["recommendations"] = _generate_health_recommendations(health_status)

        return jsonify(health_status), status_code

    except Exception as e:
        return jsonify({
            "status": "critical",
            "message": f"Health check failed: {str(e)}",
            "timestamp": time.time(),
            "recommendations": ["Investigate monitoring system failure"]
        }), 503

@monitoring_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Alert status endpoint.

    Returns active and recently resolved alerts with:
    - Alert severity and messages
    - Trigger and resolution timestamps
    - Alert context and metadata
    - Statistical summaries

    Query parameters:
    - status: 'active' (default), 'resolved', or 'all'
    - limit: Maximum number of resolved alerts to return (default: 50)
    """
    if not is_monitoring_enabled():
        return jsonify({
            "error": "Monitoring is disabled",
            "timestamp": time.time()
        }), 503

    try:
        alerts = get_alert_summary()
        status_filter = request.args.get('status', 'active')
        limit = int(request.args.get('limit', 50))

        # Filter alerts based on status
        if status_filter == 'active':
            filtered_alerts = {
                "active_alerts": alerts["active_alerts"],
                "total_active": alerts["total_active"],
                "timestamp": alerts["timestamp"]
            }
        elif status_filter == 'resolved':
            filtered_alerts = {
                "resolved_alerts": alerts["recent_resolved"][:limit],
                "total_resolved_recent": len(alerts["recent_resolved"]),
                "total_resolved_today": alerts["total_resolved_today"],
                "timestamp": alerts["timestamp"]
            }
        else:  # 'all'
            filtered_alerts = alerts.copy()
            if "recent_resolved" in filtered_alerts:
                filtered_alerts["recent_resolved"] = filtered_alerts["recent_resolved"][:limit]

        # Add alert statistics
        filtered_alerts["statistics"] = {
            "severity_breakdown": _calculate_severity_breakdown(alerts),
            "alert_trends": _calculate_alert_trends(alerts),
            "avg_resolution_time": _calculate_avg_resolution_time(alerts)
        }

        return jsonify(filtered_alerts)

    except Exception as e:
        return jsonify({
            "error": f"Failed to retrieve alerts: {str(e)}",
            "timestamp": time.time()
        }), 500

@monitoring_bp.route('/alerts/evaluate', methods=['POST'])
def evaluate_alert_rules():
    """
    Manually trigger alert rule evaluation.

    Forces evaluation of all alert rules against current metrics.
    Returns triggered and resolved alerts.

    This endpoint is useful for testing alert configurations
    and manual health assessments.
    """
    if not is_monitoring_enabled():
        return jsonify({
            "error": "Monitoring is disabled",
            "timestamp": time.time()
        }), 503

    try:
        triggered, resolved = evaluate_alerts()

        return jsonify({
            "timestamp": time.time(),
            "evaluation_result": {
                "alerts_triggered": len(triggered),
                "alerts_resolved": len(resolved),
                "triggered_details": [
                    {
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "triggered_at": alert.triggered_at
                    } for alert in triggered
                ],
                "resolved_details": [
                    {
                        "rule_name": alert.rule_name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "duration": alert.duration
                    } for alert in resolved
                ]
            }
        })

    except Exception as e:
        return jsonify({
            "error": f"Alert evaluation failed: {str(e)}",
            "timestamp": time.time()
        }), 500

def _convert_to_prometheus_format(metrics: Dict[str, Any], include_history: bool = False) -> str:
    """Convert metrics to Prometheus exposition format."""
    lines = []

    # Add HELP and TYPE comments for Prometheus
    lines.append("# HELP monitoring_system_metrics_total Total number of metrics being tracked")
    lines.append("# TYPE monitoring_system_metrics_total gauge")
    lines.append(f"monitoring_system_metrics_total {metrics['active_metrics']}")

    lines.append("# HELP monitoring_datapoints_total Total number of metric data points")
    lines.append("# TYPE monitoring_datapoints_total gauge")
    lines.append(f"monitoring_datapoints_total {metrics['total_datapoints']}")

    # Add counter metrics
    for name, value in metrics.get('counters', {}).items():
        clean_name = name.replace('_', '').replace('-', '')
        lines.append(f"# HELP {clean_name}_total Counter metric: {name}")
        lines.append(f"# TYPE {clean_name}_total counter")
        lines.append(f"{clean_name}_total {value}")

    # Add gauge metrics
    for name, value in metrics.get('gauges', {}).items():
        clean_name = name.replace('_', '').replace('-', '')
        lines.append(f"# HELP {clean_name} Gauge metric: {name}")
        lines.append(f"# TYPE {clean_name} gauge")
        lines.append(f"{clean_name} {value}")

    # Add recent measurements if requested
    if include_history and 'recent_measurements' in metrics:
        for metric_name, measurements in metrics['recent_measurements'].items():
            clean_name = metric_name.replace('_', '').replace('-', '')
            for measurement in measurements:
                # Add labels for tags
                labels = ""
                if measurement.get('tags'):
                    label_parts = [f'{k}="{v}"' for k, v in measurement['tags'].items()]
                    labels = f"{{{','.join(label_parts)}}}"

                lines.append(f"{clean_name}{labels} {measurement['value']} {int(measurement['timestamp'] * 1000)}")

    return '\n'.join(lines) + '\n'

def _generate_health_recommendations(health_status: Dict[str, Any]) -> List[str]:
    """Generate actionable health recommendations based on check results."""
    recommendations = []

    checks = health_status.get('checks', {})

    # Memory recommendations
    memory_check = checks.get('memory_usage', {})
    if memory_check.get('status') == 'critical':
        recommendations.append("URGENT: High memory usage detected. Consider scaling or memory optimization.")
    elif memory_check.get('status') == 'warning':
        recommendations.append("Monitor memory usage closely. Consider memory profiling.")

    # Disk recommendations
    disk_check = checks.get('disk_space', {})
    if disk_check.get('status') == 'critical':
        recommendations.append("CRITICAL: Low disk space. Free up space or scale storage immediately.")
    elif disk_check.get('status') == 'warning':
        recommendations.append("Disk space running low. Plan for storage cleanup or expansion.")

    # CPU recommendations
    cpu_check = checks.get('cpu_usage', {})
    if cpu_check.get('status') == 'critical':
        recommendations.append("CRITICAL: High CPU usage. Investigate performance bottlenecks.")
    elif cpu_check.get('status') == 'warning':
        recommendations.append("Elevated CPU usage. Monitor for performance degradation.")

    # Application metrics recommendations
    app_check = checks.get('application_metrics', {})
    if app_check.get('status') == 'critical':
        recommendations.append("CRITICAL: High application error rates. Immediate investigation required.")
    elif app_check.get('status') == 'warning':
        recommendations.append("Elevated error rates detected. Review application logs.")

    # Database recommendations
    db_check = checks.get('database_connectivity', {})
    if db_check.get('status') == 'critical':
        recommendations.append("CRITICAL: Database connectivity issues. Check database status.")

    # External services recommendations
    ext_check = checks.get('external_services', {})
    if ext_check.get('status') == 'critical':
        recommendations.append("CRITICAL: External service dependencies failing. Check service status.")

    if not recommendations:
        recommendations.append("All systems operating normally.")

    return recommendations

def _calculate_severity_breakdown(alerts: Dict[str, Any]) -> Dict[str, int]:
    """Calculate alert count by severity level."""
    breakdown = {"info": 0, "warning": 0, "error": 0, "critical": 0}

    for alert in alerts.get('active_alerts', []):
        severity = alert.get('severity', 'unknown')
        if severity in breakdown:
            breakdown[severity] += 1

    return breakdown

def _calculate_alert_trends(alerts: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate alert trends and patterns."""
    resolved_today = alerts.get('total_resolved_today', 0)
    active_count = alerts.get('total_active', 0)

    # Simple trend analysis
    trend = "stable"
    if active_count > 5:
        trend = "elevated"
    elif active_count > 10:
        trend = "critical"

    return {
        "trend": trend,
        "active_to_resolved_ratio": active_count / max(resolved_today, 1),
        "resolution_rate": resolved_today / max(active_count + resolved_today, 1)
    }

def _calculate_avg_resolution_time(alerts: Dict[str, Any]) -> float:
    """Calculate average alert resolution time."""
    resolved_alerts = alerts.get('recent_resolved', [])
    if not resolved_alerts:
        return 0.0

    total_time = 0.0
    count = 0

    for alert in resolved_alerts:
        if alert.get('resolved_at') and alert.get('triggered_at'):
            total_time += alert['resolved_at'] - alert['triggered_at']
            count += 1

    return total_time / max(count, 1)

# Convenience functions for registering the blueprint
def register_monitoring_endpoints(app):
    """Register monitoring endpoints with a Flask application."""
    app.register_blueprint(monitoring_bp)

def get_monitoring_routes():
    """Get list of available monitoring routes."""
    return [
        {"path": "/monitoring/metrics", "methods": ["GET"], "description": "Real-time metrics"},
        {"path": "/monitoring/health", "methods": ["GET"], "description": "Health status checks"},
        {"path": "/monitoring/alerts", "methods": ["GET"], "description": "Alert status"},
        {"path": "/monitoring/alerts/evaluate", "methods": ["POST"], "description": "Manual alert evaluation"}
    ]

# Export key functions and classes
__all__ = [
    'monitoring_bp',
    'register_monitoring_endpoints',
    'get_monitoring_routes'
]