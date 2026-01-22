"""
Monitoring Server - Production-grade metrics and health monitoring API.

Provides RESTful endpoints for operational visibility and monitoring:
- /metrics - Real-time metrics and statistics
- /health - Comprehensive health status with checks
- /alerts - Active and resolved alerts

Designed for production deployment with proper error handling,
logging, and performance optimizations.
"""

import os
import logging

# Optional Flask imports
try:
    from flask import Flask, request, jsonify
    from werkzeug.exceptions import HTTPException
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Create stub classes when Flask is not available
    class Flask:
        def __init__(self, *args, **kwargs):
            pass
        def register_blueprint(self, *args, **kwargs):
            pass
        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def errorhandler(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def before_request(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def after_request(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def run(self, *args, **kwargs):
            pass

    def jsonify(data):
        import json
        return json.dumps(data)

    class request:
        start_time = 0
        path = '/'
        method = 'GET'

    class HTTPException(Exception):
        def __init__(self, description="", code=500):
            self.description = description
            self.code = code

from .api import register_monitoring_endpoints, get_monitoring_routes
from .metrics_config import is_monitoring_enabled, METRICS_CONFIG

logger = logging.getLogger(__name__)

def create_monitoring_app() -> Flask:
    """
    Create and configure the monitoring Flask application.

    Returns:
        Configured Flask application with monitoring endpoints
    """
    app = Flask(__name__)

    # Configure Flask app
    app.config['JSON_SORT_KEYS'] = False  # Preserve key order
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    # Register monitoring endpoints
    register_monitoring_endpoints(app)

    # Add root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information."""
        return jsonify({
            "service": "AI Content Pipeline Monitoring",
            "version": "1.0.0",
            "description": "Production-grade monitoring and alerting system",
            "endpoints": get_monitoring_routes(),
            "status": "operational" if is_monitoring_enabled() else "monitoring_disabled"
        })

    # Add readiness probe endpoint
    @app.route('/ready', methods=['GET'])
    def readiness():
        """Kubernetes readiness probe endpoint."""
        if is_monitoring_enabled():
            return jsonify({"status": "ready"}), 200
        else:
            return jsonify({"status": "not ready", "reason": "monitoring_disabled"}), 503

    # Add liveness probe endpoint
    @app.route('/live', methods=['GET'])
    def liveness():
        """Kubernetes liveness probe endpoint."""
        return jsonify({"status": "alive"}), 200

    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler for all endpoints."""
        logger.error(f"Unhandled exception: {e}", exc_info=True)

        if isinstance(e, HTTPException):
            return jsonify({
                "error": e.description,
                "code": e.code,
                "timestamp": __import__('time').time()
            }), e.code

        return jsonify({
            "error": "Internal server error",
            "timestamp": __import__('time').time()
        }), 500

    # Request logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming requests for monitoring."""
        if request.path.startswith('/monitoring/'):
            logger.info(f"Monitoring request: {request.method} {request.path}")

    # Response time tracking
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        if request.path.startswith('/monitoring/'):
            response_time = __import__('time').time() - request.start_time
            logger.info(".3f")
        return response

    return app

def run_monitoring_server(
    host: str = "0.0.0.0",
    port: int = None,
    debug: bool = False
):
    """
    Run the monitoring server.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: from METRICS_CONFIG)
        debug: Enable debug mode
    """
    if port is None:
        port = METRICS_CONFIG["export"]["prometheus_port"]

    app = create_monitoring_app()

    logger.info(f"Starting monitoring server on {host}:{port}")
    logger.info(f"Monitoring enabled: {is_monitoring_enabled()}")
    logger.info(f"Debug mode: {debug}")

    # Print available endpoints
    print("\n" + "="*50)
    print("MONITORING SERVER STARTED")
    print("="*50)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Monitoring: {'ENABLED' if is_monitoring_enabled() else 'DISABLED'}")
    print("\nAvailable endpoints:")
    for route in get_monitoring_routes():
        methods = ", ".join(route["methods"])
        print(f"  {methods} {route['path']} - {route['description']}")

    print("\nAdditional endpoints:")
    print("  GET  / - API information")
    print("  GET  /ready - Readiness probe")
    print("  GET  /live - Liveness probe")
    print("="*50 + "\n")

    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True,
        use_reloader=False
    )

def main():
    """Main entry point for running the monitoring server."""
    import argparse

    parser = argparse.ArgumentParser(description="Monitoring Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        run_monitoring_server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        logger.info("Monitoring server stopped by user")
    except Exception as e:
        logger.error(f"Monitoring server failed: {e}")
        raise

if __name__ == "__main__":
    main()