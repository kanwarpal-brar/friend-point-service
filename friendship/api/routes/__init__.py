"""Route registration for the API."""

from flask import Flask, jsonify, Blueprint, request
import logging

from ...tracker import FriendshipTracker
from .. import auth
from . import friends, interactions

logger = logging.getLogger(__name__)

def register_routes(app: Flask, tracker: FriendshipTracker):
    """Register all API routes with the Flask app."""
    # Register the API key as required for all routes
    app.config['AUTH_DECORATOR'] = auth.require_api_key
    auth_decorator = auth.require_api_key
    
    # Create a Blueprint with the /api prefix
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    # Register a simple health check endpoint that doesn't require authentication
    @api_bp.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Kubernetes probes."""
        return jsonify({
            'status': 'ok',
            'message': 'Friendship service is running'
        })
    
    # Also register a root health check for Kubernetes probes
    @app.route('/health', methods=['GET'])
    def root_health_check():
        """Root health check endpoint for Kubernetes probes."""
        return jsonify({
            'status': 'ok',
            'message': 'Friendship service is running'
        })
    
    # Register friend-related routes (pass the auth_decorator directly)
    friends.register_routes(api_bp, tracker, auth_decorator)
    
    # Register interaction-related routes (pass the auth_decorator directly)
    interactions.register_routes(api_bp, tracker, auth_decorator)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        path = request.path
        logger.warning(f"404 Not Found: {path}")
        return jsonify({
            'status': 'error',
            'message': f"Endpoint not found: {path}"
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        """Handle 405 errors."""
        method = request.method
        path = request.path
        logger.warning(f"405 Method Not Allowed: {method} {path}")
        return jsonify({
            'status': 'error',
            'message': f"Method {method} not allowed for endpoint: {path}"
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 errors."""
        logger.error(f"500 Internal Server Error: {error}")
        return jsonify({
            'status': 'error',
            'message': "Internal server error"
        }), 500

    # Register a catch-all for unhandled exceptions
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unhandled exceptions."""
        logger.exception(f"Unhandled exception: {error}")
        return jsonify({
            'status': 'error',
            'message': "An unexpected error occurred"
        }), 500
    
    # Register the blueprint with the app
    app.register_blueprint(api_bp)
