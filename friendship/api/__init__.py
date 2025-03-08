"""REST API package for friendship tracking system."""

from flask import Flask

from .routes import register_routes
from .rate_limit import configure_rate_limiter
from ..tracker import FriendshipTracker
from ..config import get_config

class FriendshipAPI:
    """Flask-based REST API for the friendship tracking system."""
    
    def __init__(self, tracker: FriendshipTracker):
        """Initialize the API with a tracker instance."""
        self.app = Flask(__name__)
        
        # Set URL prefix for all routes
        self.app.config['APPLICATION_ROOT'] = '/api'
        
        self.tracker = tracker
        
        # Configure rate limiter from environment or defaults
        config = get_config()
        rate_limit = config.get('RATE_LIMIT', 30)
        rate_window = config.get('RATE_WINDOW', 60)
        configure_rate_limiter(limit=rate_limit, window=rate_window)
        
        # Register all routes defined in route modules
        register_routes(self.app, self.tracker)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        self.app.run(host=host, port=port, debug=debug)

def create_api(db_path="friendships.db"):
    """Factory function to create the API instance."""
    tracker = FriendshipTracker(db_path)
    api = FriendshipAPI(tracker)
    return api
