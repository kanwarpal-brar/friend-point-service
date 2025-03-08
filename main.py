"""
Friend Point Service - Main Application

A system to track and measure friendship levels with a fuzzy point system.
"""

import argparse
import logging

from friendship import FriendshipTracker, create_api
from friendship.config import get_config

logger = logging.getLogger(__name__)

def run_example():
    """Run the example interaction."""
    config = get_config()
    tracker = FriendshipTracker(config['DB_PATH'])
    
    # Add some friends
    tracker.add_friend("Alex")
    tracker.add_friend("Taylor")
    
    # Record some interactions with custom messages and point values
    print(tracker.record_interaction("Alex", 0.3, "helped me move apartments"))
    print(tracker.record_interaction("Alex", 0.4, "remembered my birthday"))
    print(tracker.record_interaction("Taylor", 0.5, "supported me during a tough time"))
    print(tracker.record_interaction("Alex", -0.2, "forgot our dinner plans"))
    
    # Check statuses
    print("\n" + tracker.get_friend_status("Alex"))
    print(tracker.get_friend_history("Alex"))
    
    # Show all friends
    print("\n" + tracker.get_all_friends())
    
    # Visualize a friendship
    print("\n" + tracker.visualize_friendship("Alex"))
    
    # Clean up
    tracker.close()

def run_api_server():
    """Run the REST API server."""
    config = get_config()
    logger.info(f"Starting API server on {config['API_HOST']}:{config['API_PORT']}")
    logger.info(f"Using database at {config['DB_PATH']}")
    
    api = create_api(config['DB_PATH'])
    api.run(host=config['API_HOST'], port=config['API_PORT'], debug=config['DEBUG'])

def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description='Friend Point Service')
    parser.add_argument('--api', action='store_true', help='Run the REST API server')
    parser.add_argument('--example', action='store_true', help='Run the example interaction')
    
    args = parser.parse_args()
    
    if args.api:
        run_api_server()
    elif args.example:
        run_example()
    else:
        # Default to API server
        run_api_server()

if __name__ == "__main__":
    main()