"""Database module for friendship tracking system."""

import sqlite3
import datetime


class FriendshipDatabase:
    """SQLite database manager for friendship tracking system."""
    
    def __init__(self, db_path="friendships.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        # Friends table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            lower_bound REAL NOT NULL,
            fuzziness REAL NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        ''')
        
        # Interactions table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            point_value REAL NOT NULL,
            actual_change REAL NOT NULL,
            previous_bound REAL NOT NULL,
            new_bound REAL NOT NULL,
            previous_rank INTEGER NOT NULL,
            new_rank INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (friend_id) REFERENCES friends (id)
        )
        ''')
        
        self.conn.commit()
    
    def get_friend(self, name):
        """Retrieve a friend from the database."""
        self.cursor.execute("SELECT id, name, lower_bound, fuzziness FROM friends WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result
    
    def add_friend(self, name, lower_bound=0.1, fuzziness=0.3):
        """Add a new friend to the database."""
        now = datetime.datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO friends (name, lower_bound, fuzziness, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (name, lower_bound, fuzziness, now, now)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Friend already exists
            self.cursor.execute("SELECT id FROM friends WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
    
    def update_friend(self, friend_id, lower_bound):
        """Update a friend's lower bound."""
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            "UPDATE friends SET lower_bound = ?, updated_at = ? WHERE id = ?",
            (lower_bound, now, friend_id)
        )
        self.conn.commit()
    
    def log_interaction(self, friend_id, message, point_value, actual_change, 
                        previous_bound, new_bound, previous_rank, new_rank):
        """Log an interaction with a friend."""
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            """INSERT INTO interactions 
               (friend_id, message, point_value, actual_change, previous_bound, new_bound, 
                previous_rank, new_rank, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (friend_id, message, point_value, actual_change, previous_bound, new_bound, 
             previous_rank, new_rank, now)
        )
        self.conn.commit()
    
    def get_all_friends(self):
        """Get all friends sorted by lower bound."""
        self.cursor.execute(
            "SELECT id, name, lower_bound, fuzziness FROM friends ORDER BY lower_bound DESC"
        )
        return self.cursor.fetchall()
    
    def get_friend_interactions(self, friend_id, limit=10):
        """Get recent interactions with a friend."""
        self.cursor.execute(
            """SELECT message, point_value, actual_change, previous_bound, new_bound, 
                     previous_rank, new_rank, timestamp 
               FROM interactions 
               WHERE friend_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (friend_id, limit)
        )
        return self.cursor.fetchall()
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
