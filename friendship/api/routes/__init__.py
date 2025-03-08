"""Route registration for the API."""

from flask import Flask, jsonify, Blueprint

from ...tracker import FriendshipTracker
from .. import auth
from . import friends, interactions

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
    
    # Register the blueprint with the app
    app.register_blueprint(api_bp)
