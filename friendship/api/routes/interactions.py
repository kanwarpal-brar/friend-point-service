"""Interaction-related API routes."""

from flask import Flask, request, jsonify, Blueprint

from ...tracker import FriendshipTracker
from ..rate_limit import rate_limit

def register_routes(blueprint, tracker: FriendshipTracker, auth_decorator):
    """Register interaction-related routes with the Flask blueprint."""
    
    # POST to record interaction
    @blueprint.route('/friends/interaction', methods=['POST'])
    @auth_decorator
    @rate_limit
    def record_interaction():
        """Record a new interaction with a friend."""
        try:
            data = request.json
            
            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No JSON data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['name', 'points', 'message']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({
                    'status': 'error',
                    'message': f"Missing required fields: {', '.join(missing_fields)}"
                }), 400
            
            # Validate data types
            name = data['name']
            message = data['message']
            
            try:
                points = float(data['points'])
            except (ValueError, TypeError):
                return jsonify({
                    'status': 'error',
                    'message': f"Invalid points value: '{data['points']}'. Must be a number."
                }), 400
            
            if not isinstance(name, str) or not name.strip():
                return jsonify({
                    'status': 'error',
                    'message': "Name must be a non-empty string"
                }), 400
                
            if not isinstance(message, str) or not message.strip():
                return jsonify({
                    'status': 'error',
                    'message': "Message must be a non-empty string"
                }), 400
            
            # Record the interaction
            result = tracker.record_interaction(name, points, message)
            friend = tracker.get_friend(name)
            
            if not friend:
                return jsonify({
                    'status': 'error',
                    'message': f"Failed to find or create friend '{name}'"
                }), 500
            
            return jsonify({
                'status': 'success',
                'message': result,
                'name': name,
                'rank': friend.friend_rank,
                'lower_bound': friend.lower_bound,
                'display': friend.display_points
            })
        except ValueError as e:
            return jsonify({
                'status': 'error',
                'message': f"Invalid value: {str(e)}"
            }), 400
        except TypeError as e:
            return jsonify({
                'status': 'error',
                'message': f"Type error: {str(e)}"
            }), 400
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Error processing interaction: {str(e)}"
            }), 500
