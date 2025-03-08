"""
Friend Point Service - Main Application

A system to track and measure friendship levels with a fuzzy point system.
"""

from friendship import FriendshipTracker

def main():
    tracker = FriendshipTracker()
    
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

if __name__ == "__main__":
    main()