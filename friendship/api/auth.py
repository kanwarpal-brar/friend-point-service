"""Authentication middleware for the API."""

import os
import logging
import secrets
import string
import re
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

# More secure default API key (64 chars)
DEFAULT_API_KEY = "change_me_in_production"

def generate_api_key(length=64):
    """Generate a cryptographically secure API key."""
    try:
        alphabet = string.ascii_letters + string.digits + "-_"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    except Exception as e:
        logger.error(f"Error generating API key: {str(e)}")
        # Return a fallback key if there's an error
        return "temp_fallback_key_please_regenerate_" + str(hash(str(e)))[:16]

def is_valid_api_key_format(key):
    """Check if the API key format is valid (min 32 chars, proper character set)."""
    try:
        if not key or len(key) < 32:
            return False
        
        # API key should only contain alphanumeric chars plus some special chars
        valid_pattern = re.compile(r'^[a-zA-Z0-9\-_]+$')
        return bool(valid_pattern.match(key))
    except Exception as e:
        logger.error(f"Error validating API key format: {str(e)}")
        return False

def get_api_key():
    """Get the API key from environment variables or use default for development."""
    try:
        key = os.environ.get("FRIENDSHIP_API_KEY", DEFAULT_API_KEY)
        
        # If the key is the default warning message, log a warning
        if key == DEFAULT_API_KEY:
            logger.warning(
                "Using default API key! This is insecure. "
                "Set FRIENDSHIP_API_KEY environment variable with a secure key."
            )
        
        # Check key format
        if not is_valid_api_key_format(key) and key != DEFAULT_API_KEY:
            logger.warning(
                "API key format is not secure! It should be at least 32 characters "
                "and contain only alphanumeric characters plus - and _"
            )
        
        return key
    except Exception as e:
        logger.error(f"Error retrieving API key: {str(e)}")
        return DEFAULT_API_KEY

def require_api_key(f):
    """Decorator to require valid API key for route access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get the API key from the request
            provided_key = request.headers.get("X-API-Key")
            
            # Get the expected API key
            expected_key = get_api_key()
            
            # Check if the key is valid
            if not provided_key or provided_key != expected_key:
                logger.warning("Unauthorized access attempt")
                return jsonify({
                    'status': 'error',
                    'message': 'Unauthorized. Valid API key required.'
                }), 401
                
            # If the key is valid, proceed with the route function
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error but don't expose details in the response
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Authentication error occurred'
            }), 500
    return decorated
