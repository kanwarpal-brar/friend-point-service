"""Route registration for the API."""

from flask import Flask

from ...tracker import FriendshipTracker
from . import friends, interactions

def register_routes(app: Flask, tracker: FriendshipTracker):
    """Register all API routes with the Flask app."""
    # Register friend-related routes
    friends.register_routes(app, tracker)
    
    # Register interaction-related routes
    interactions.register_routes(app, tracker)
