"""REST API server for friendship tracking system."""

from flask import Flask, request, jsonify

from .tracker import FriendshipTracker

class FriendshipAPI:
    """Flask-based REST API for the friendship tracking system."""
    
    def __init__(self, tracker: FriendshipTracker):
        """Initialize the API with a tracker instance."""
        self.app = Flask(__name__)
        self.tracker = tracker
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Set up the API endpoints."""
        # GET friendship statuses
        @self.app.route('/friends', methods=['GET'])
        def get_friends():
            """Get all friends and their statuses."""
            all_friends_text = self.tracker.get_all_friends()
            
            # Extract friend data for JSON response
            friend_data = self.db_get_all_friends()
            return jsonify({
                'status': 'success',
                'message': all_friends_text,
                'friends': friend_data
            })
        
        @self.app.route('/friends/<name>', methods=['GET'])
        def get_friend(name):
            """Get a specific friend's status."""
            friend = self.tracker.get_friend(name)
            if not friend:
                return jsonify({
                    'status': 'error',
                    'message': f"Friend '{name}' not found"
                }), 404
            
            status = self.tracker.get_friend_status(name)
            history = self.tracker.get_friend_history(name)
            visualization = self.tracker.visualize_friendship(name)
            
            return jsonify({
                'status': 'success',
                'name': name,
                'rank': friend.friend_rank,
                'lower_bound': friend.lower_bound,
                'upper_bound': friend.fuzzy_points[1],
                'display': friend.display_points,
                'status_text': status,
                'history_text': history,
                'visualization': visualization
            })
        
        # POST to record interaction
        @self.app.route('/friends/interaction', methods=['POST'])
        def record_interaction():
            """Record a new interaction with a friend."""
            data = request.json
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No JSON data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['name', 'points', 'message']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'message': f"Missing required field: '{field}'"
                    }), 400
            
            # Record the interaction
            try:
                name = data['name']
                points = float(data['points'])
                message = data['message']
                
                result = self.tracker.record_interaction(name, points, message)
                friend = self.tracker.get_friend(name)
                
                return jsonify({
                    'status': 'success',
                    'message': result,
                    'name': name,
                    'rank': friend.friend_rank,
                    'lower_bound': friend.lower_bound,
                    'display': friend.display_points
                })
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid points value'
                }), 400
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
    
    def db_get_all_friends(self) -> list:
        """Get all friends in a JSON-friendly format."""
        friend_data = self.tracker.db.get_all_friends()
        result = []
        
        for id, name, lower_bound, fuzziness in friend_data:
            friend = self.tracker.get_friend(name)
            result.append({
                'id': id,
                'name': name,
                'rank': friend.friend_rank,
                'lower_bound': lower_bound,
                'upper_bound': friend.fuzzy_points[1],
                'display': friend.display_points
            })
        
        return result
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask application."""
        self.app.run(host=host, port=port, debug=debug)

def create_api(db_path="friendships.db"):
    """Factory function to create the API instance."""
    tracker = FriendshipTracker(db_path)
    api = FriendshipAPI(tracker)
    return api
