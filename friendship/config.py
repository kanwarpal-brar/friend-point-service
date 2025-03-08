"""Configuration module for friendship tracking system."""

import os
import logging

# Default configuration
DEFAULT_CONFIG = {
    'DB_PATH': 'friendships.db',
    'API_HOST': '0.0.0.0',
    'API_PORT': 5000,
    'DEBUG': False,
    'LOG_LEVEL': 'INFO',
    'API_KEY': 'change_me_in_production',
    'RATE_LIMIT': 100,     # Increased from 30 to 100 requests per windows per window
    'RATE_WINDOW': 60,    # 60 seconds time windoww
    'DISABLE_RATE_LIMIT': False,  # Option to disable rate limiting entirely
}

def get_config():
    """Get configuration from environment variables, with defaults."""
    config = DEFAULT_CONFIG.copy()
    
    # Override from environment variables
    if 'FRIENDSHIP_DB_PATH' in os.environ:
        config['DB_PATH'] = os.environ['FRIENDSHIP_DB_PATH']
    
    if 'FRIENDSHIP_API_PORT' in os.environ:
        config['API_PORT'] = int(os.environ['FRIENDSHIP_API_PORT'])
    
    if 'FRIENDSHIP_API_HOST' in os.environ:
        config['API_HOST'] = os.environ['FRIENDSHIP_API_HOST']
    
    if 'FRIENDSHIP_DEBUG' in os.environ:
        config['DEBUG'] = os.environ['FRIENDSHIP_DEBUG'].lower() in ('true', '1', 'yes')
    
    if 'FRIENDSHIP_LOG_LEVEL' in os.environ:
        config['LOG_LEVEL'] = os.environ['FRIENDSHIP_LOG_LEVEL']
    
    if 'FRIENDSHIP_API_KEY' in os.environ:
        config['API_KEY'] = os.environ['FRIENDSHIP_API_KEY']
    
    # Rate limiting configuration
    if 'FRIENDSHIP_RATE_LIMIT' in os.environ:
        config['RATE_LIMIT'] = int(os.environ['FRIENDSHIP_RATE_LIMIT'])
    
    if 'FRIENDSHIP_RATE_WINDOW' in os.environ:
        config['RATE_WINDOW'] = int(os.environ['FRIENDSHIP_RATE_WINDOW'])
    
    # Option to disable rate limiting entirely
    if 'FRIENDSHIP_DISABLE_RATE_LIMIT' in os.environ:
        config['DISABLE_RATE_LIMIT'] = os.environ['FRIENDSHIP_DISABLE_RATE_LIMIT'].lower() in ('true', '1', 'yes')
    
    # Configure logging
    log_level = getattr(logging, config['LOG_LEVEL'].upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return config
