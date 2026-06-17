"""
Main application entry point.
Orchestrates the activity tracker, system monitor, and UI components.
"""

import threading
import time
from datetime import datetime
from tracker import ActivityTracker, SystemEventMonitor
from ui import InactivityPopup, StatusWindow
from logger import ActivityLogger
from config import config
import utils


class TrackingApplication:
    """Main application class that orchestrates all tracking components."""

    def __init__(self):
        self.is_running = False
        self.activity_tracker = None
        self.system_monitor = None
        self.activity_logger = ActivityLogger()
        self.popup = InactivityPopup()
        self.status_window = None
        self.current_activity_start = None
        self.pending_reason = False
        self.last_popup_time = None

    def initialize(self) -> bool:
        """Initialize the application."""
        try:
            utils.log_info("Initializing tracking application")
            utils.ensure_database_path()

            # Initialize tracker and monitor
            self.activity_tracker = ActivityTracker(
                callback=self._on_tracker_event
            )
            self.system_monitor = SystemEventMonitor(
                callback=self._on_system_event
            )

            return True

        except Exception as e:
            utils.log_error(f"Error initializing application: {e}", exc_info=True)
            return False

    def start(self) -> bool:
        """Start the application."""
        try:
            utils.log_info("Starting tracking application")

            if not self.initialize():
                return False

            self.is_running = True

            # Start trackers
            if not self.activity_tracker.start():
                utils.log_error("Failed to start activity tracker")
                return False

            if not self.system_monitor.start():
                utils.log_warning("Failed to start system monitor")
                # Don't fail if system monitor fails

            self.current_activity_start = datetime.now()

            utils.log_info("Tracking application started successfully")
            return True

        except Exception as e:
            utils.log_error(f"Error starting application: {e}", exc_info=True)
            return False

    def stop(self) -> bool:
        """Stop the application."""
        try:
            utils.log_info("Stopping tracking application")
            self.is_running = False

            if self.activity_tracker:
                self.activity_tracker.stop()

            if self.system_monitor:
                self.system_monitor.stop()

            if self.status_window:
                self.status_window.close()

            utils.log_info("Tracking application stopped")
            return True

        except Exception as e:
            utils.log_error(f"Error stopping application: {e}", exc_info=True)
            return False

    def _on_tracker_event(self, event: dict):
        """Handle events from activity tracker."""
        try:
            event_type = event.get("type")

            if event_type == "IDLE_START":
                utils.log_info("User is now idle - showing popup")
                self.pending_reason = True
                self._show_inactivity_popup("Idle Detected")

            elif event_type == "ACTIVITY_RESUMED":
                utils.log_info("User activity resumed")
                idle_duration = event.get("idle_duration", 0)

                # Store idle session with reason if available
                if self.pending_reason:
                    self.pending_reason = False
                    # Wait for popup response

        except Exception as e:
            utils.log_error(f"Error handling tracker event: {e}", exc_info=True)

    def _on_system_event(self, event: dict):
        """Handle events from system monitor."""
        try:
            event_type = event.get("type")

            if event_type == "SYSTEM_UNLOCKED":
                utils.log_info("System unlocked - showing popup")
                lock_duration = event.get("lock_duration", 0)
                self._show_inactivity_popup(
                    f"System Unlocked (Locked for {int(lock_duration/60)} min)"
                )

        except Exception as e:
            utils.log_error(f"Error handling system event: {e}", exc_info=True)

    def _show_inactivity_popup(self, title: str = "Activity Tracker"):
        """Show inactivity popup."""
        try:
            # Prevent multiple popups in short succession
            current_time = time.time()
            if (
                self.last_popup_time
                and (current_time - self.last_popup_time) < 30
            ):
                utils.log_debug("Skipping popup - too soon after last one")
                return

            self.last_popup_time = current_time

            def on_popup_response(response: dict):
                """Handle popup response."""
                try:
                    reason = response.get("reason", "Unknown")
                    details = response.get("details", "")

                    utils.log_info(f"Popup response: {reason}")

                    # Log the idle session with reason
                    idle_duration = self.activity_tracker.get_idle_duration()
                    current_time_str = datetime.now().isoformat()
                    idle_start_time = (
                        datetime.now().isoformat()
                        if not hasattr(self, "_idle_start")
                        else self._idle_start
                    )

                    self.activity_logger.log_idle_session(
                        idle_start=idle_start_time,
                        idle_end=current_time_str,
                        reason=f"{reason}: {details}" if details else reason,
                    )

                except Exception as e:
                    utils.log_error(f"Error processing popup response: {e}")

            self.popup.show(
                title=title,
                message="Please select reason for inactivity:",
                callback=on_popup_response,
                timeout=600,  # 10 minutes timeout
            )

        except Exception as e:
            utils.log_error(f"Error showing popup: {e}", exc_info=True)

    def run_interactive(self):
        """Run the application in interactive mode with a status window."""
        try:
            if not self.start():
                print("Failed to start application")
                return

            # Create and show status window
            self.status_window = StatusWindow()
            if self.status_window.create():
                self.status_window.show()

            # Update status periodically
            def update_loop():
                while self.is_running:
                    try:
                        if self.status_window:
                            activity_status = (
                                "Idle"
                                if self.activity_tracker.is_idle
                                else "Active"
                            )
                            self.status_window.update_activity(activity_status)

                            stats = self.activity_logger.get_today_stats()
                            self.status_window.update_stats(
                                stats.get("idle_time", 0),
                                stats.get("active_time", 0),
                            )

                        time.sleep(5)
                    except Exception as e:
                        utils.log_debug(f"Error in update loop: {e}")
                        time.sleep(5)

            update_thread = threading.Thread(target=update_loop, daemon=True)
            update_thread.start()

            # Keep running
            if self.status_window.window:
                self.status_window.window.mainloop()

        except KeyboardInterrupt:
            utils.log_info("Interrupted by user")
        except Exception as e:
            utils.log_error(f"Error in interactive mode: {e}", exc_info=True)
        finally:
            self.stop()

    def run_background(self):
        """Run the application in background mode (no UI)."""
        try:
            if not self.start():
                print("Failed to start application")
                return

            utils.log_info("Running in background mode")

            # Keep the main thread alive
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                utils.log_info("Interrupted by user")

        except Exception as e:
            utils.log_error(f"Error in background mode: {e}", exc_info=True)
        finally:
            self.stop()


def main():
    """Main entry point."""
    try:
        import sys

        app = TrackingApplication()

        # Check command line arguments
        interactive_mode = "--interactive" in sys.argv or "-i" in sys.argv
        enable_autostart = "--autostart" in sys.argv
        disable_autostart = "--no-autostart" in sys.argv

        # Handle autostart options
        if enable_autostart:
            if utils.enable_autostart():
                print("Autostart enabled")
            sys.exit(0)

        if disable_autostart:
            if utils.disable_autostart():
                print("Autostart disabled")
            sys.exit(0)

        # Run application
        if interactive_mode:
            print("Starting in interactive mode...")
            app.run_interactive()
        else:
            print("Starting in background mode...")
            app.run_background()

    except Exception as e:
        utils.log_error(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
