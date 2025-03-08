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
- REST API endpoints for integration
- Docker and Kubernetes support

## Usage

### Python Library

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

### REST API

Run the API server:

```bash
python main.py --api
```

#### Get all friends:
```bash
curl http://localhost:5000/friends
```

#### Get a specific friend:
```bash
curl http://localhost:5000/friends/Alex
```

#### Record an interaction:
```bash
curl -X POST http://localhost:5000/friends/interaction \
  -H "Content-Type: application/json" \
  -d '{"name": "Alex", "points": 0.5, "message": "helped me with a project"}'
```

## Docker

Build the Docker image:

```bash
docker build -t friendship-service .
```

Run the container:

```bash
docker run -p 5000:5000 -v $(pwd)/data:/data friendship-service
```

## Kubernetes

Deploy to Kubernetes:

```bash
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

## Structure

- `friendship/` - Main package
  - `database.py` - Database management with SQLite
  - `models.py` - Data model for friends
  - `tracker.py` - Main friendship tracking functionality
  - `api.py` - REST API implementation
  - `config.py` - Configuration management
- `main.py` - Command line interface
- `kubernetes/` - Kubernetes deployment files
- `Dockerfile` - Docker configuration
