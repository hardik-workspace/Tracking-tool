"""
Activity tracker module.
Handles keyboard/mouse activity detection, idle tracking, and system events.
"""

import threading
import time
import platform
from datetime import datetime, timedelta
from typing import Callable, Optional
import utils
from config import config
from logger import ActivityLogger

# Try to import pynput, with fallback for non-supported platforms
try:
    from pynput import mouse, keyboard
    from pynput.mouse import Listener as MouseListener
    from pynput.keyboard import Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    utils.log_warning("pynput not available - activity tracking disabled")


class ActivityTracker:
    """Tracks user activity and idle time."""

    def __init__(self, callback: Callable = None):
        self.last_activity = datetime.now()
        self.idle_threshold = config.get("idle_timeout", 5) * 60  # Convert to seconds
        self.check_interval = config.get("check_interval", 2)
        self.is_idle = False
        self.is_running = False
        self.activity_callback = callback
        self.mouse_listener = None
        self.keyboard_listener = None
        self.activity_thread = None
        self.logger = ActivityLogger()
        self.idle_start_time = None
        self.current_activity_start = None

    def start(self) -> bool:
        """Start tracking activity."""
        try:
            if self.is_running:
                return True

            if not PYNPUT_AVAILABLE:
                utils.log_warning("Cannot start activity tracker - pynput not available")
                return False

            self.is_running = True
            self.last_activity = datetime.now()
            utils.log_info("Activity tracker started")

            # Start mouse listener
            self.mouse_listener = MouseListener(on_move=self._on_activity)
            self.mouse_listener.start()

            # Start keyboard listener
            self.keyboard_listener = KeyboardListener(on_press=self._on_activity)
            self.keyboard_listener.start()

            # Start activity checking thread
            self.activity_thread = threading.Thread(
                target=self._check_activity_loop, daemon=True
            )
            self.activity_thread.start()

            return True

        except Exception as e:
            utils.log_error(f"Error starting tracker: {e}", exc_info=True)
            return False

    def stop(self) -> bool:
        """Stop tracking activity."""
        try:
            self.is_running = False

            if self.mouse_listener:
                self.mouse_listener.stop()

            if self.keyboard_listener:
                self.keyboard_listener.stop()

            utils.log_info("Activity tracker stopped")
            return True

        except Exception as e:
            utils.log_error(f"Error stopping tracker: {e}", exc_info=True)
            return False

    def _on_activity(self, *args, **kwargs):
        """Called when mouse or keyboard activity is detected."""
        try:
            current_time = datetime.now()

            # Check if we were idle and now active
            if self.is_idle:
                idle_duration = (current_time - self.idle_start_time).total_seconds()
                self.is_idle = False

                # Log idle session
                self.logger.log_idle_session(
                    idle_start=self.idle_start_time.isoformat(),
                    idle_end=current_time.isoformat(),
                )

                # Trigger callback for idle end
                if self.activity_callback:
                    self.activity_callback(
                        {
                            "type": "ACTIVITY_RESUMED",
                            "idle_duration": idle_duration,
                            "timestamp": current_time.isoformat(),
                        }
                    )

                utils.log_info(
                    f"User activity resumed after {idle_duration} seconds of idle"
                )

            self.last_activity = current_time

        except Exception as e:
            utils.log_debug(f"Error in activity callback: {e}")

    def _check_activity_loop(self):
        """Periodically check if user is idle."""
        try:
            while self.is_running:
                try:
                    current_time = datetime.now()
                    time_since_last_activity = (
                        current_time - self.last_activity
                    ).total_seconds()

                    # Check if idle
                    if (
                        time_since_last_activity >= self.idle_threshold
                        and not self.is_idle
                    ):
                        self.is_idle = True
                        self.idle_start_time = current_time - timedelta(
                            seconds=time_since_last_activity
                        )

                        utils.log_info("User is now idle")

                        # Trigger idle callback
                        if self.activity_callback:
                            self.activity_callback(
                                {
                                    "type": "IDLE_START",
                                    "idle_start": self.idle_start_time.isoformat(),
                                    "timestamp": current_time.isoformat(),
                                }
                            )

                    time.sleep(self.check_interval)

                except Exception as e:
                    utils.log_debug(f"Error in activity loop: {e}")
                    time.sleep(self.check_interval)

        except Exception as e:
            utils.log_error(f"Activity loop error: {e}", exc_info=True)

    def get_idle_duration(self) -> int:
        """Get current idle duration in seconds."""
        try:
            if self.is_idle:
                return int((datetime.now() - self.idle_start_time).total_seconds())
            return 0
        except Exception:
            return 0

    def get_status(self) -> dict:
        """Get current tracker status."""
        return {
            "is_running": self.is_running,
            "is_idle": self.is_idle,
            "last_activity": self.last_activity.isoformat(),
            "idle_duration": self.get_idle_duration(),
        }


class SystemEventMonitor:
    """Monitors system events like lock/unlock."""

    def __init__(self, callback: Callable = None):
        self.callback = callback
        self.is_running = False
        self.monitor_thread = None
        self.logger = ActivityLogger()
        self.is_locked = False
        self.lock_time = None

    def start(self) -> bool:
        """Start monitoring system events."""
        try:
            if self.is_running:
                return True

            self.is_running = True
            utils.log_info("System event monitor started")

            # Start monitoring thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True
            )
            self.monitor_thread.start()

            return True

        except Exception as e:
            utils.log_error(f"Error starting system monitor: {e}", exc_info=True)
            return False

    def stop(self) -> bool:
        """Stop monitoring system events."""
        try:
            self.is_running = False
            utils.log_info("System event monitor stopped")
            return True
        except Exception as e:
            utils.log_error(f"Error stopping system monitor: {e}", exc_info=True)
            return False

    def _monitor_loop(self):
        """Monitor system lock/unlock events."""
        try:
            # Windows-only system monitoring
            if platform.system() != "Windows":
                utils.log_debug("System monitoring not supported on non-Windows platforms")
                while self.is_running:
                    time.sleep(2)
                return

            try:
                import win32api
                import win32con
                import win32event
                import win32security
            except ImportError:
                utils.log_warning("pywin32 not available - system monitoring disabled")
                while self.is_running:
                    time.sleep(2)
                return

            while self.is_running:
                try:
                    # Check if screen is locked by attempting to get session state
                    # This is a simplified check
                    current_locked = self._is_system_locked()

                    # Trigger event if lock state changed
                    if current_locked and not self.is_locked:
                        self.is_locked = True
                        self.lock_time = datetime.now()
                        utils.log_info("System locked")

                        self.logger.log_system_event(
                            event_type="SYSTEM_LOCKED",
                            details=None,
                        )

                        if self.callback:
                            self.callback(
                                {
                                    "type": "SYSTEM_LOCKED",
                                    "timestamp": self.lock_time.isoformat(),
                                }
                            )

                    elif not current_locked and self.is_locked:
                        self.is_locked = False
                        unlock_time = datetime.now()
                        lock_duration = (unlock_time - self.lock_time).total_seconds()

                        utils.log_info(
                            f"System unlocked after {lock_duration} seconds"
                        )

                        self.logger.log_system_event(
                            event_type="SYSTEM_UNLOCKED",
                            details=f"Locked for {lock_duration} seconds",
                        )

                        if self.callback:
                            self.callback(
                                {
                                    "type": "SYSTEM_UNLOCKED",
                                    "lock_duration": lock_duration,
                                    "timestamp": unlock_time.isoformat(),
                                }
                            )

                    time.sleep(2)

                except Exception as e:
                    utils.log_debug(f"Error monitoring system: {e}")
                    time.sleep(2)

        except Exception as e:
            utils.log_error(f"System monitoring error: {e}", exc_info=True)

    def _is_system_locked(self) -> bool:
        """Check if Windows system is locked."""
        try:
            if platform.system() != "Windows":
                return False

            import win32gui

            desktop = win32gui.GetDesktopWindow()
            shell_window = win32gui.FindWindow("Shell_TrayWnd", None)

            # Simple check: if we can find the lock screen window
            lock_screen = win32gui.FindWindow(
                "LockScreenControlPanel", None
            ) or win32gui.FindWindow("Windows.UI.Core.CoreWindow", "Windows Shell Experience Host")

            return lock_screen is not None

        except Exception:
            return False

    def get_status(self) -> dict:
        """Get current system status."""
        return {
            "is_running": self.is_running,
            "is_locked": self.is_locked,
            "lock_time": self.lock_time.isoformat()
            if self.lock_time
            else None,
        }
