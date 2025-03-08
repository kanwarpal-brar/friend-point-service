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
    
    def __init__(self, limit=30, window=60):
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
        
        with self.lock:
            # Clean up old requests
            self.requests[key] = [req_time for req_time in self.requests[key] 
                                if now - req_time < self.window]
            
            # Check if we're over the limit
            if len(self.requests[key]) >= self.limit:
                # Calculate when the oldest request will expire
                reset_time = self.requests[key][0] + self.window - now
                return False, 0, reset_time
            
            # Record this request
            self.requests[key].append(now)
            
            remaining = self.limit - len(self.requests[key])
            reset_time = self.window
            
            return True, remaining, reset_time

# Global rate limiter instance
limiter = RateLimiter()

def rate_limit(f):
    """
    Decorator to apply rate limiting to a route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get client identifier (IP address)
        client_ip = request.remote_addr
        
        # Check rate limit
        allowed, remaining, reset_time = limiter.is_allowed(client_ip)
        
        # Set rate limit headers
        response = None
        
        if not allowed:
            # Return 429 Too Many Requests
            response = jsonify({
                'status': 'error',
                'message': 'Rate limit exceeded. Please try again later.'
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
    
    return decorated

def configure_rate_limiter(limit=30, window=60):
    """
    Configure the global rate limiter.
    
    Args:
        limit: Maximum number of requests allowed in the time window
        window: Time window in seconds
    """
    limiter.limit = limit
    limiter.window = window
    logger.info(f"Rate limiter configured: {limit} requests per {window} seconds")
