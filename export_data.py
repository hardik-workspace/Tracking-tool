"""
Data export and analytics script.
View and export tracked activity data.
Run: python export_data.py
"""

import sqlite3
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from tabulate import tabulate


class DataAnalyzer:
    """Analyze and export activity data."""

    def __init__(self, db_path="tracking_data.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def get_today_summary(self):
        """Get today's activity summary."""
        if not self.conn:
            return None

        cursor = self.conn.cursor()

        # Total idle time
        cursor.execute(
            """
            SELECT SUM(duration_minutes) as total 
            FROM idle_sessions 
            WHERE date = date('now')
            """
        )
        idle_time = cursor.fetchone()["total"] or 0

        # Total active time
        cursor.execute(
            """
            SELECT SUM(duration_minutes) as total 
            FROM activity_logs 
            WHERE activity_type = 'ACTIVE' AND date = date('now')
            """
        )
        active_time = cursor.fetchone()["total"] or 0

        # Number of sessions
        cursor.execute(
            """
            SELECT COUNT(*) as count 
            FROM idle_sessions 
            WHERE date = date('now')
            """
        )
        sessions = cursor.fetchone()["count"]

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "idle_time_minutes": idle_time,
            "active_time_minutes": active_time,
            "sessions": sessions,
            "total_time_minutes": idle_time + active_time,
        }

    def get_weekly_summary(self):
        """Get weekly activity summary."""
        if not self.conn:
            return None

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT 
                date,
                SUM(CASE WHEN duration_minutes > 0 THEN 1 ELSE 0 END) as session_count,
                SUM(CASE WHEN activity_type = 'IDLE' THEN duration_minutes ELSE 0 END) as idle_minutes,
                SUM(CASE WHEN activity_type = 'ACTIVE' THEN duration_minutes ELSE 0 END) as active_minutes
            FROM activity_logs
            WHERE date >= date('now', '-7 days')
            GROUP BY date
            ORDER BY date DESC
            """
        )

        return cursor.fetchall()

    def get_idle_reasons(self, days=7):
        """Get idle reasons summary."""
        if not self.conn:
            return None

        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT 
                reason,
                COUNT(*) as count,
                SUM(duration_minutes) as total_minutes,
                AVG(duration_minutes) as avg_minutes
            FROM idle_sessions
            WHERE date >= date('now', ? || ' days')
            GROUP BY reason
            ORDER BY count DESC
            """,
            (f"-{days}",),
        )

        return cursor.fetchall()

    def get_idle_sessions(self, date=None, limit=50):
        """Get idle sessions for a specific date."""
        if not self.conn:
            return None

        cursor = self.conn.cursor()

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT 
                idle_start,
                idle_end,
                duration_minutes,
                reason
            FROM idle_sessions
            WHERE date = ?
            ORDER BY idle_start DESC
            LIMIT ?
            """,
            (date, limit),
        )

        return cursor.fetchall()

    def export_to_csv(self, output_path="export.csv", date=None):
        """Export idle sessions to CSV."""
        if not self.conn:
            return False

        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")

            sessions = self.get_idle_sessions(date)

            with open(output_path, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Start Time", "End Time", "Duration (min)", "Reason"])

                for session in sessions:
                    writer.writerow(
                        [
                            session["idle_start"],
                            session["idle_end"],
                            session["duration_minutes"],
                            session["reason"],
                        ]
                    )

            print(f"✓ Data exported to {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_json(self, output_path="export.json"):
        """Export all data to JSON."""
        if not self.conn:
            return False

        try:
            cursor = self.conn.cursor()

            # Get all idle sessions
            cursor.execute("SELECT * FROM idle_sessions ORDER BY idle_start DESC")
            idle_sessions = [dict(row) for row in cursor.fetchall()]

            # Get summary
            summary = self.get_today_summary()

            data = {
                "export_date": datetime.now().isoformat(),
                "summary": summary,
                "idle_sessions": idle_sessions,
            }

            with open(output_path, "w") as jsonfile:
                json.dump(data, jsonfile, indent=2, default=str)

            print(f"✓ Data exported to {output_path}")
            return True

        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False


def print_header(title):
    """Print formatted header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def print_today_summary(analyzer):
    """Print today's summary."""
    print_header("TODAY'S SUMMARY")

    summary = analyzer.get_today_summary()

    if summary:
        data = [
            ["Date", summary["date"]],
            ["Idle Time", f"{summary['idle_time_minutes']} minutes"],
            ["Active Time", f"{summary['active_time_minutes']} minutes"],
            ["Total Time", f"{summary['total_time_minutes']} minutes"],
            ["Sessions", summary["sessions"]],
        ]

        print(tabulate(data, tablefmt="simple"))
        print()


def print_idle_sessions(analyzer, date=None):
    """Print idle sessions."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
        date_str = "TODAY"
    else:
        date_str = date

    print_header(f"IDLE SESSIONS - {date_str}")

    sessions = analyzer.get_idle_sessions(date)

    if sessions:
        headers = ["Start Time", "End Time", "Duration (min)", "Reason"]
        data = [
            [
                s["idle_start"][-8:],  # Show only time
                s["idle_end"][-8:] if s["idle_end"] else "N/A",
                s["duration_minutes"],
                s["reason"][:30],  # Truncate long reasons
            ]
            for s in sessions
        ]

        print(tabulate(data, headers=headers, tablefmt="grid"))
        print()
    else:
        print("No idle sessions recorded for this date.")
        print()


def print_idle_reasons(analyzer, days=7):
    """Print idle reasons summary."""
    print_header(f"IDLE REASONS - Last {days} Days")

    reasons = analyzer.get_idle_reasons(days)

    if reasons:
        headers = ["Reason", "Count", "Total Minutes", "Avg Minutes"]
        data = [
            [
                r["reason"][:30],
                r["count"],
                r["total_minutes"],
                f"{r['avg_minutes']:.1f}",
            ]
            for r in reasons
        ]

        print(tabulate(data, headers=headers, tablefmt="grid"))
        print()
    else:
        print("No idle sessions recorded in the past", days, "days.")
        print()


def main():
    """Main menu."""
    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║  Activity Tracker - Data Analyzer & Exporter      ║")
    print("╚════════════════════════════════════════════════════╝")

    # Check if database exists
    if not Path("tracking_data.db").exists():
        print()
        print("✗ Database not found. Run the application first:")
        print("  python main.py --interactive")
        print()
        return

    analyzer = DataAnalyzer()

    if not analyzer.connect():
        print("Failed to connect to database")
        return

    while True:
        print()
        print("Select an option:")
        print("1. View today's summary")
        print("2. View today's idle sessions")
        print("3. View idle reasons (last 7 days)")
        print("4. View idle sessions from specific date")
        print("5. Export to CSV")
        print("6. Export to JSON")
        print("7. Exit")
        print()

        choice = input("Enter option (1-7): ").strip()

        if choice == "1":
            print_today_summary(analyzer)

        elif choice == "2":
            print_idle_sessions(analyzer)

        elif choice == "3":
            print_idle_reasons(analyzer, days=7)

        elif choice == "4":
            date = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(date, "%Y-%m-%d")
                print_idle_sessions(analyzer, date)
            except ValueError:
                print("Invalid date format")

        elif choice == "5":
            filename = input("Enter output filename (default: export.csv): ").strip()
            if not filename:
                filename = "export.csv"
            analyzer.export_to_csv(filename)

        elif choice == "6":
            filename = input("Enter output filename (default: export.json): ").strip()
            if not filename:
                filename = "export.json"
            analyzer.export_to_json(filename)

        elif choice == "7":
            break

        else:
            print("Invalid option")

    analyzer.close()
    print()
    print("Goodbye!")


if __name__ == "__main__":
    # Check if tabulate is installed
    try:
        import tabulate
    except ImportError:
        print("Installing required package...")
        import subprocess
        import sys

        subprocess.run([sys.executable, "-m", "pip", "install", "tabulate"])

    main()
