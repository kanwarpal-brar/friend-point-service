"""REST API package for friendship tracking system."""

from flask import Flask

from .routes import register_routes
from ..tracker import FriendshipTracker

class FriendshipAPI:
    """Flask-based REST API for the friendship tracking system."""
    
    def __init__(self, tracker: FriendshipTracker):
        """Initialize the API with a tracker instance."""
        self.app = Flask(__name__)
        self.tracker = tracker
        
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
