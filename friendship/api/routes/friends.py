"""Friend-related API routes."""

from flask import Flask, jsonify, request, Blueprint

from ...tracker import FriendshipTracker
from ..rate_limit import rate_limit

def register_routes(blueprint, tracker: FriendshipTracker, auth_decorator):
    """Register friend-related routes with the Flask blueprint."""
    
    # GET all friends
    @blueprint.route('/friends', methods=['GET'])
    @auth_decorator
    @rate_limit
    def get_friends():
        """Get all friends and their statuses."""
        try:
            all_friends_text = tracker.get_all_friends()
            
            # Extract friend data for JSON response
            friend_data = _get_all_friends_data(tracker)
            return jsonify({
                'status': 'success',
                'message': all_friends_text,
                'friends': friend_data
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Failed to retrieve friends: {str(e)}"
            }), 500
    
    # GET or DELETE specific friend
    @blueprint.route('/friends/<name>', methods=['GET', 'DELETE'])
    @auth_decorator
    @rate_limit
    def get_friend(name):
        """Get a specific friend's status or delete a friend."""
        # Handle DELETE method
        if request.method == 'DELETE':
            return delete_friend(name)
        
        # Handle GET method
        try:
            friend = tracker.get_friend(name)
            if not friend:
                return jsonify({
                    'status': 'error',
                    'message': f"Friend '{name}' not found"
                }), 404
            
            status = tracker.get_friend_status(name)
            history = tracker.get_friend_history(name)
            visualization = tracker.visualize_friendship(name)
            
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
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Error retrieving friend details: {str(e)}"
            }), 500
    
    def delete_friend(name):
        """Delete a friend by name."""
        try:
            # Check if friend exists
            friend = tracker.get_friend(name)
            if not friend:
                return jsonify({
                    'status': 'error',
                    'message': f"Friend '{name}' not found"
                }), 404
            
            # Delete the friend
            success = tracker.delete_friend(name)
            if success:
                return jsonify({
                    'status': 'success',
                    'message': f"Friend '{name}' has been deleted"
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f"Failed to delete friend '{name}'"
                }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f"Error deleting friend: {str(e)}"
            }), 500

def _get_all_friends_data(tracker: FriendshipTracker) -> list:
    """Get all friends in a JSON-friendly format."""
    try:
        friend_data = tracker.db.get_all_friends()
        result = []
        
        for id, name, lower_bound, fuzziness in friend_data:
            friend = tracker.get_friend(name)
            if friend:  # Make sure the friend exists before accessing properties
                result.append({
                    'id': id,
                    'name': name,
                    'rank': friend.friend_rank,
                    'lower_bound': lower_bound,
                    'upper_bound': friend.fuzzy_points[1],
                    'display': friend.display_points
                })
        
        return result
    except Exception as e:
        # Log the error but return an empty list instead of crashing
        import logging
        logging.error(f"Error getting friend data: {str(e)}")
        return []
