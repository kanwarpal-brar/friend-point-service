"""Main friendship tracking functionality."""

import random
import math
import datetime
from typing import Optional

from .database import FriendshipDatabase
from .models import Friend


class FriendshipTracker:
    """Main system to track and manage friendships."""
    
    def __init__(self, db_path="friendships.db"):
        self.db = FriendshipDatabase(db_path)
    
    def add_friend(self, name: str) -> Friend:
        """Add a new friend to the tracker."""
        existing = self.db.get_friend(name)
        if existing:
            return Friend(*existing)
        
        # New friends have slightly variable starting points and fuzziness
        initial_lower_bound = random.uniform(0.1, 0.3)
        fuzziness = random.uniform(0.2, 0.4)
        
        friend_id = self.db.add_friend(name, initial_lower_bound, fuzziness)
        return Friend(friend_id, name, initial_lower_bound, fuzziness)
    
    def get_friend(self, name: str) -> Optional[Friend]:
        """Get a friend by name."""
        result = self.db.get_friend(name)
        if not result:
            return None
        return Friend(*result)
    
    def delete_friend(self, name: str) -> bool:
        """
        Delete a friend from the tracker.
        
        Args:
            name: Friend's name
            
        Returns:
            Boolean indicating success or failure
        """
        friend = self.get_friend(name)
        if not friend:
            return False
            
        # Delete the friend from the database
        success = self.db.delete_friend(friend.id)
        return success
    
    def _calculate_point_change(self, current_bound: float, point_value: float) -> float:
        """
        Calculate the actual change to lower bound based on current friendship level.
        
        The scaling ensures higher friendships require more positive interactions to advance.
        """
        if point_value >= 0:
            # Positive interaction - harder to gain points at higher levels
            # Higher ranks experience diminishing returns
            
            # Apply more aggressive scaling factor to slow down progression
            rank_factor = 1.0 / (1.0 + current_bound * 0.7)  # Increased from 0.5 to 0.7
            
            # Additional exponential decay for higher ranks
            rank_penalty = math.exp(-0.4 * current_bound)  # Increased from 0.3 to 0.4
            
            # Add a general dampening factor to slow down all progression
            general_dampening = 0.65  # Only 65% of points awarded
            
            return point_value * rank_factor * rank_penalty * general_dampening
        else:
            # Negative interaction - higher friendships are more resilient
            # Protection increases with friendship rank
            protection_factor = 1.0 - math.tanh(current_bound * 0.3)
            
            # Stronger protection for deep friendships
            if current_bound > 5:
                protection_factor *= 0.7
            
            return point_value * protection_factor
    
    def record_interaction(self, name: str, point_value: float, message: str) -> str:
        """
        Record an interaction with a friend.
        
        Args:
            name: Friend's name
            point_value: Value of interaction (positive or negative)
            message: Description of the interaction
        
        Returns:
            String describing the result of the interaction
        """
        # Get or create the friend
        friend = self.get_friend(name)
        if not friend:
            friend = self.add_friend(name)
        
        previous_bound = friend.lower_bound
        previous_rank = friend.friend_rank
        
        # Calculate actual point change with scaling
        actual_change = self._calculate_point_change(previous_bound, point_value)
        
        # Update the lower bound (ensuring it doesn't go below 0)
        new_bound = max(0, previous_bound + actual_change)
        new_rank = Friend.calculate_rank(new_bound)
        
        # Update the database
        self.db.update_friend(friend.id, new_bound)
        self.db.log_interaction(
            friend.id, message, point_value, actual_change,
            previous_bound, new_bound, previous_rank, new_rank
        )
        
        # Get updated friend
        friend = Friend(friend.id, friend.name, new_bound, friend.fuzziness)
        
        # Format the result message
        sign = '+' if actual_change >= 0 else ''
        result = f"{name}: {message} ({sign}{actual_change:.2f} to lower bound) → {friend.display_points}"
        
        if new_rank > previous_rank:
            result += f"\n🎉 Friendship rank increased to {new_rank}! 🎉"
        elif new_rank < previous_rank:
            result += f"\n⚠️ Friendship rank decreased to {new_rank}! ⚠️"
        
        return result
    
    def get_friend_status(self, name: str) -> str:
        """Get the current status of a friendship."""
        friend = self.get_friend(name)
        if not friend:
            return f"{name} is not in your friends list."
        
        lower, upper = friend.fuzzy_points
        return f"{name}: {friend.display_points} (fuzzy range: {lower:.2f}-{upper:.2f})"
    
    def get_friend_history(self, name: str, limit: int = 5) -> str:
        """Get recent interaction history with a friend."""
        friend = self.get_friend(name)
        if not friend:
            return f"{name} is not in your friends list."
        
        interactions = self.db.get_friend_interactions(friend.id, limit)
        if not interactions:
            return f"No recorded interactions with {name}."
        
        result = [f"Recent interactions with {name}:"]
        for msg, points, change, old_bound, new_bound, old_rank, new_rank, timestamp in interactions:
            date = datetime.datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
            sign = '+' if change >= 0 else ''
            line = f"{date}: {msg} ({sign}{change:.2f} points)"
            if old_rank != new_rank:
                rank_change = "↑" if new_rank > old_rank else "↓"
                line += f" [Rank {old_rank} {rank_change} {new_rank}]"
            result.append(line)
        
        return "\n".join(result)
    
    def get_all_friends(self) -> str:
        """Get a list of all friends sorted by rank."""
        friend_data = self.db.get_all_friends()
        if not friend_data:
            return "You have no friends tracked yet."
        
        friends = [Friend(*data) for data in friend_data]
        
        result = ["Your Friends (by rank):"]
        for i, friend in enumerate(friends, 1):
            result.append(f"{i}. {friend.name}: {friend.display_points}")
        
        return "\n".join(result)
    
    def visualize_friendship(self, name: str) -> str:
        """Visualize the friendship with an ASCII art graph."""
        friend = self.get_friend(name)
        if not friend:
            return f"{name} is not in your friends list."
        
        lower, upper = friend.fuzzy_points
        
        # Create a simple ASCII bar chart
        chart_width = 40
        filled = int((lower / 10) * chart_width)  # Only fill up to the lower bound
        fuzzy_width = int(((upper - lower) / 10) * chart_width)
        
        # Create a bar with solid section for the lower bound and a fuzzy section
        bar = "█" * filled + "░" * fuzzy_width + " " * (chart_width - filled - fuzzy_width)
        
        # Show threshold markers
        thresholds = ""
        for i in range(11):
            pos = int((i / 10) * chart_width)
            thresholds += "|" if pos < chart_width else ""
            thresholds += " " * (chart_width // 10 - 1) if i < 10 else ""
        
        lines = [
            f"Friendship with {name}:",
            f"{friend.display_points}",
            "0" + " " * (chart_width-2) + "10",
            bar,
            f"Lower bound: {lower:.2f}  |  Potential upper bound: {upper:.2f}",
            thresholds
        ]
        
        return "\n".join(lines)
    
    def close(self):
        """Close the database connection."""
        self.db.close()
