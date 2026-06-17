"""
Database logger module for storing activity data.
Handles SQLite database operations for tracking records.
"""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from config import config

# Lock for thread-safe database operations
db_lock = threading.Lock()


class ActivityLogger:
    """Manages database operations for activity logging."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get("db_path", "tracking_data.db")
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Create activity_logs table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration_minutes INTEGER,
                        activity_type TEXT NOT NULL,
                        reason TEXT,
                        application_name TEXT,
                        date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                # Create idle_sessions table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS idle_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        idle_start TEXT NOT NULL,
                        idle_end TEXT,
                        duration_minutes INTEGER,
                        reason TEXT,
                        date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                # Create system_events table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        details TEXT,
                        date TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                conn.commit()
                conn.close()

        except Exception as e:
            print(f"Error initializing database: {e}")

    def log_activity(
        self,
        start_time: str,
        end_time: str,
        activity_type: str,
        reason: str = None,
        application_name: str = None,
    ) -> bool:
        """Log an activity session."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Calculate duration
                try:
                    start = datetime.fromisoformat(start_time)
                    end = datetime.fromisoformat(end_time)
                    duration = int((end - start).total_seconds() / 60)
                except Exception:
                    duration = 0

                cursor.execute(
                    """
                    INSERT INTO activity_logs 
                    (start_time, end_time, duration_minutes, activity_type, reason, application_name, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        start_time,
                        end_time,
                        duration,
                        activity_type,
                        reason,
                        application_name,
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )

                conn.commit()
                conn.close()
                return True

        except Exception as e:
            print(f"Error logging activity: {e}")
            return False

    def log_idle_session(
        self,
        idle_start: str,
        idle_end: str,
        reason: str = None,
    ) -> bool:
        """Log an idle session."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                # Calculate duration
                try:
                    start = datetime.fromisoformat(idle_start)
                    end = datetime.fromisoformat(idle_end)
                    duration = int((end - start).total_seconds() / 60)
                except Exception:
                    duration = 0

                cursor.execute(
                    """
                    INSERT INTO idle_sessions 
                    (idle_start, idle_end, duration_minutes, reason, date)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        idle_start,
                        idle_end,
                        duration,
                        reason,
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )

                conn.commit()
                conn.close()
                return True

        except Exception as e:
            print(f"Error logging idle session: {e}")
            return False

    def log_system_event(
        self,
        event_type: str,
        details: str = None,
    ) -> bool:
        """Log a system event (lock/unlock)."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO system_events 
                    (event_type, timestamp, details, date)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        event_type,
                        datetime.now().isoformat(),
                        details,
                        datetime.now().strftime("%Y-%m-%d"),
                    ),
                )

                conn.commit()
                conn.close()
                return True

        except Exception as e:
            print(f"Error logging system event: {e}")
            return False

    def get_today_stats(self) -> dict:
        """Get today's activity statistics."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                today = datetime.now().strftime("%Y-%m-%d")

                # Get total active time
                cursor.execute(
                    """
                    SELECT SUM(duration_minutes) FROM activity_logs 
                    WHERE activity_type='ACTIVE' AND date=?
                    """,
                    (today,),
                )
                active_time = cursor.fetchone()[0] or 0

                # Get total idle time
                cursor.execute(
                    """
                    SELECT SUM(duration_minutes) FROM idle_sessions 
                    WHERE date=?
                    """,
                    (today,),
                )
                idle_time = cursor.fetchone()[0] or 0

                # Get number of sessions
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM idle_sessions WHERE date=?
                    """,
                    (today,),
                )
                sessions = cursor.fetchone()[0] or 0

                conn.close()

                return {
                    "active_time": active_time,
                    "idle_time": idle_time,
                    "sessions": sessions,
                }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"active_time": 0, "idle_time": 0, "sessions": 0}

    def get_activities(
        self, date: str = None, limit: int = 50
    ) -> List[Tuple]:
        """Get activities for a specific date."""
        try:
            with db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                if date is None:
                    date = datetime.now().strftime("%Y-%m-%d")

                cursor.execute(
                    """
                    SELECT start_time, end_time, duration_minutes, activity_type, 
                           reason, application_name 
                    FROM activity_logs 
                    WHERE date=? 
                    ORDER BY start_time DESC 
                    LIMIT ?
                    """,
                    (date, limit),
                )

                results = cursor.fetchall()
                conn.close()
                return results

        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []
