"""Rate limiting for the API."""

import time
from functools import wraps
from collections import defaultdict
import logging
import threading
from flask import request, jsonify

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, limit=100, window=60):
        """
        Initialize the rate limiter.
        
        Args:
            limit: Maximum number of requests allowed in the time window
            window: Time window in seconds
        """
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key):
        """
        Check if a request from the given key is allowed.
        
        Args:
            key: Identifier for the client (e.g., IP address)
            
        Returns:
            tuple: (allowed, remaining, reset_time)
        """
        now = time.time()
        
        try:
            with self.lock:
                # Clean up old requests
                self.requests[key] = [req_time for req_time in self.requests[key] 
                                    if now - req_time < self.window]
                
                # Check if we're over the limit
                if len(self.requests[key]) >= self.limit:
                    # Calculate when the oldest request will expire
                    reset_time = self.requests[key][0] + self.window - now
                    logger.warning(f"Rate limit exceeded for {key}: {len(self.requests[key])} requests in {self.window}s window")
                    return False, 0, reset_time
                
                # Record this request
                self.requests[key].append(now)
                
                remaining = self.limit - len(self.requests[key])
                reset_time = self.window
                
                # Log request rate for debugging
                if len(self.requests[key]) % 10 == 0 or len(self.requests[key]) <= 5:
                    logger.debug(f"Client {key} has made {len(self.requests[key])} requests in current window, {remaining} remaining")
                
                return True, remaining, reset_time
        except Exception as e:
            # In case of error, allow the request to avoid blocking legitimate traffic
            # but log the error
            logger.error(f"Rate limiter error: {str(e)}")
            return True, 999, self.window  # Return dummy values

# Global rate limiter instance
limiter = RateLimiter()

def rate_limit(f):
    """
    Decorator to apply rate limiting to a route.
    
    This can be disabled by setting FRIENDSHIP_DISABLE_RATE_LIMIT=true in environment.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Get client identifier (IP address)
            client_ip = request.remote_addr
            
            # Only apply rate limiting if not disabled
            from ..config import get_config
            config = get_config()
            
            if config.get('DISABLE_RATE_LIMIT', False):
                # Skip rate limiting if disabled
                return f(*args, **kwargs)
            
            # Check rate limit
            allowed, remaining, reset_time = limiter.is_allowed(client_ip)
            
            # Set rate limit headers
            response = None
            
            if not allowed:
                # Return 429 Too Many Requests
                response = jsonify({
                    'status': 'error',
                    'message': f'Rate limit exceeded. Please try again in {reset_time:.1f} seconds.'
                })
                response.status_code = 429
            else:
                # Process the request normally
                response = f(*args, **kwargs)
            
            # Add rate limit headers to the response
            response.headers['X-RateLimit-Limit'] = str(limiter.limit)
            response.headers['X-RateLimit-Remaining'] = str(remaining)
            response.headers['X-RateLimit-Reset'] = str(int(reset_time))
            
            return response
        except Exception as e:
            # In case of any failure in the rate limiter, still process the request
            logger.error(f"Rate limit decorator error: {str(e)}")
            return f(*args, **kwargs)
    
    return decorated

def configure_rate_limiter(limit=100, window=60):
    """
    Configure the global rate limiter.
    
    Args:
        limit: Maximum number of requests allowed in the time window
        window: Time window in seconds
    """
    try:
        limiter.limit = limit
        limiter.window = window
        logger.info(f"Rate limiter configured: {limit} requests per {window} seconds")
    except Exception as e:
        logger.error(f"Failed to configure rate limiter: {str(e)}")
