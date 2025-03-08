"""Route registration for the API."""

from flask import Flask, jsonify

from ...tracker import FriendshipTracker
from .. import auth
from . import friends, interactions

def register_routes(app: Flask, tracker: FriendshipTracker):
    """Register all API routes with the Flask app."""
    # Register the API key as required for all routes
    app.config['AUTH_DECORATOR'] = auth.require_api_key
    
    # Register a simple health check endpoint that doesn't require authentication
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Kubernetes probes."""
        return jsonify({
            'status': 'ok',
            'message': 'Friendship service is running'
        })
    
    # Register friend-related routes
    friends.register_routes(app, tracker)
    
    # Register interaction-related routes
    interactions.register_routes(app, tracker)
