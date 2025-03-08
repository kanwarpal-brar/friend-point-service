"""Data models for friendship tracking system."""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Friend:
    """Friend representation with methods to calculate various friendship metrics."""
    id: int
    name: str
    lower_bound: float
    fuzziness: float
    
    @staticmethod
    def calculate_rank(lower_bound: float) -> int:
        """Calculate the friend rank based on lower bound."""
        return math.floor(lower_bound)
    
    @property
    def friend_rank(self) -> int:
        """Get the current friend rank."""
        return self.calculate_rank(self.lower_bound)
    
    @property
    def fuzzy_points(self) -> Tuple[float, float]:
        """Return a fuzzy range of friendship points."""
        # The upper bound scales with the lower bound
        upper_bound = self.lower_bound + (self.fuzziness * (1 + self.lower_bound * 0.2))
        return (self.lower_bound, upper_bound)
    
    @property
    def display_points(self) -> str:
        """Human-readable representation of friend points."""
        lower, upper = self.fuzzy_points
        rank = self.friend_rank
        
        # Special case for new friendships
        if rank == 0:
            return f"Acquaintance (~{upper:.2f} potential)"
        
        # Map ranks to descriptive terms
        rank_terms = {
            1: "Casual Friend",
            2: "Friend",
            3: "Good Friend",
            4: "Close Friend", 
            5: "Best Friend",
            6: "Cherished Friend",
            7: "Lifelong Friend",
            8: "Soul Friend",
            9: "Legendary Friend"
        }
        
        term = rank_terms.get(rank, f"Transcendent Friend Level {rank}")
        return f"{term} ({lower:.2f}-{upper:.2f})"
