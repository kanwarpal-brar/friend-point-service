"""Database module for friendship tracking system."""

import sqlite3
import datetime
import threading
import logging

logger = logging.getLogger(__name__)

class FriendshipDatabase:
    """SQLite database manager for friendship tracking system."""
    
    def __init__(self, db_path="friendships.db"):
        self.db_path = db_path
        self._local = threading.local()
        # Initialize in the current thread
        self._get_connection()
    
    def _get_connection(self):
        """Get or create a thread-local database connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            logger.debug(f"Creating new SQLite connection in thread {threading.get_ident()}")
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._local.cursor = self._local.conn.cursor()
            self._create_tables()
        return self._local.conn, self._local.cursor
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist."""
        conn, cursor = self._get_connection()
        
        # Friends table
        cursor.execute('''
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
        cursor.execute('''
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
        
        conn.commit()
    
    def get_friend(self, name):
        """Retrieve a friend from the database."""
        _, cursor = self._get_connection()
        cursor.execute("SELECT id, name, lower_bound, fuzziness FROM friends WHERE name = ?", (name,))
        result = cursor.fetchone()
        return result
    
    def add_friend(self, name, lower_bound=0.1, fuzziness=0.3):
        """Add a new friend to the database."""
        conn, cursor = self._get_connection()
        now = datetime.datetime.now().isoformat()
        try:
            cursor.execute(
                "INSERT INTO friends (name, lower_bound, fuzziness, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (name, lower_bound, fuzziness, now, now)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Friend already exists
            cursor.execute("SELECT id FROM friends WHERE name = ?", (name,))
            return cursor.fetchone()[0]
    
    def update_friend(self, friend_id, lower_bound):
        """Update a friend's lower bound."""
        conn, cursor = self._get_connection()
        now = datetime.datetime.now().isoformat()
        cursor.execute(
            "UPDATE friends SET lower_bound = ?, updated_at = ? WHERE id = ?",
            (lower_bound, now, friend_id)
        )
        conn.commit()
    
    def log_interaction(self, friend_id, message, point_value, actual_change, 
                        previous_bound, new_bound, previous_rank, new_rank):
        """Log an interaction with a friend."""
        conn, cursor = self._get_connection()
        now = datetime.datetime.now().isoformat()
        cursor.execute(
            """INSERT INTO interactions 
               (friend_id, message, point_value, actual_change, previous_bound, new_bound, 
                previous_rank, new_rank, timestamp) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (friend_id, message, point_value, actual_change, previous_bound, new_bound, 
             previous_rank, new_rank, now)
        )
        conn.commit()
    
    def get_all_friends(self):
        """Get all friends sorted by lower bound."""
        _, cursor = self._get_connection()
        cursor.execute(
            "SELECT id, name, lower_bound, fuzziness FROM friends ORDER BY lower_bound DESC"
        )
        return cursor.fetchall()
    
    def get_friend_interactions(self, friend_id, limit=10):
        """Get recent interactions with a friend."""
        _, cursor = self._get_connection()
        cursor.execute(
            """SELECT message, point_value, actual_change, previous_bound, new_bound, 
                     previous_rank, new_rank, timestamp 
               FROM interactions 
               WHERE friend_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (friend_id, limit)
        )
        return cursor.fetchall()
    
    def delete_friend(self, friend_id):
        """Delete a friend and all their interactions from the database."""
        conn, cursor = self._get_connection()
        try:
            # First delete all interactions for this friend
            cursor.execute("DELETE FROM interactions WHERE friend_id = ?", (friend_id,))
            # Then delete the friend
            cursor.execute("DELETE FROM friends WHERE id = ?", (friend_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Database error when deleting friend {friend_id}: {e}")
            conn.rollback()
            return False
    
    def close(self):
        """Close the database connection."""
        if hasattr(self._local, 'conn') and self._local.conn is not None:
            self._local.conn.close()
            self._local.conn = None
