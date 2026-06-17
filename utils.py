"""
Utility functions for the tracking application.
Provides helper functions for Windows interaction, logging, etc.
"""

import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from config import config

# Setup logging
LOG_FILE = config.get("log_path", "app_logs.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("TrackingApp")


def get_active_window_name() -> str:
    """Get the name of the currently active window (Windows only)."""
    try:
        import win32gui

        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        return window_title if window_title else "Unknown"
    except Exception as e:
        logger.debug(f"Error getting active window: {e}")
        return "Unknown"


def get_active_application() -> str:
    """Get the active application name."""
    try:
        import psutil

        for proc in psutil.process_iter(["pid", "name"]):
            try:
                if proc.info["pid"] == os.getpid():
                    continue
                # Try to get the foreground process
                return proc.info["name"]
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return "Unknown"
    except Exception as e:
        logger.debug(f"Error getting application: {e}")
        return "Unknown"


def enable_autostart() -> bool:
    """Enable application to run on system startup (Windows)."""
    try:
        import winreg

        # Get the path to the current script
        app_path = os.path.abspath("main.py")

        # Open the Run registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        # Set the value
        winreg.SetValueEx(key, "ActivityTracker", 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)

        logger.info("Autostart enabled")
        return True
    except Exception as e:
        logger.error(f"Error enabling autostart: {e}")
        return False


def disable_autostart() -> bool:
    """Disable application autostart."""
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        winreg.DeleteValue(key, "ActivityTracker")
        winreg.CloseKey(key)

        logger.info("Autostart disabled")
        return True
    except Exception as e:
        logger.error(f"Error disabling autostart: {e}")
        return False


def get_system_info() -> dict:
    """Get basic system information."""
    try:
        import psutil
        import platform

        return {
            "platform": platform.system(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.debug(f"Error getting system info: {e}")
        return {
            "platform": "Windows",
            "cpu_percent": 0,
            "memory_percent": 0,
            "timestamp": datetime.now().isoformat(),
        }


def log_info(message: str):
    """Log an info message."""
    logger.info(message)


def log_error(message: str, exc_info=False):
    """Log an error message."""
    logger.error(message, exc_info=exc_info)


def log_warning(message: str):
    """Log a warning message."""
    logger.warning(message)


def log_debug(message: str):
    """Log a debug message."""
    logger.debug(message)


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def is_admin() -> bool:
    """Check if the application is running as admin."""
    try:
        import ctypes

        return ctypes.windll.shell.IsUserAnAdmin()
    except Exception:
        return False


def ensure_database_path():
    """Ensure database directory exists."""
    try:
        db_path = config.get("db_path")
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    except Exception as e:
        logger.error(f"Error ensuring database path: {e}")
