# Friend Point Service

A Python system to track and measure friendship levels with a fuzzy point system.

## Overview

This service provides a way to track your friendships through a point system where positive and negative interactions affect friendship levels. The system uses a "fuzzy" approach to friendship scoring, where each friend has:

- A lower bound (confirmed friendship level)
- A fuzziness factor (potential for growth)

## Features

- Add friends and track their friendship level
- Record positive and negative interactions with friends
- View friendship statuses and histories
- Visualize friendships with ASCII graphs
- Persistent storage using SQLite

## Usage

```python
from friendship import FriendshipTracker

# Create a tracker
tracker = FriendshipTracker()

# Add a friend
tracker.add_friend("Alex")

# Record interactions
print(tracker.record_interaction("Alex", 0.3, "helped me move apartments"))

# Check friendship status
print(tracker.get_friend_status("Alex"))

# Visualize the friendship
print(tracker.visualize_friendship("Alex"))

# Close the connection when done
tracker.close()
```

## Structure

- `friendship/` - Main package
  - `database.py` - Database management with SQLite
  - `models.py` - Data model for friends
  - `tracker.py` - Main friendship tracking functionality
- `main.py` - Example usage
