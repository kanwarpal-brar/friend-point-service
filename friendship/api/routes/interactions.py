"""Interaction-related API routes."""

from flask import Flask, request, jsonify

from ...tracker import FriendshipTracker

def register_routes(app: Flask, tracker: FriendshipTracker):
    """Register interaction-related routes with the Flask app."""
    
    # POST to record interaction
    @app.route('/friends/interaction', methods=['POST'])
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
            
            result = tracker.record_interaction(name, points, message)
            friend = tracker.get_friend(name)
            
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
