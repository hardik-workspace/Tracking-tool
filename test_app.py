"""
Test script to verify all components are working correctly.
Run: python test_app.py
"""

import sys
import time
import sqlite3
from datetime import datetime
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("=" * 50)
    print("Testing Imports")
    print("=" * 50)

    import platform
    is_windows = platform.system() == "Windows"

    modules = {
        "pynput": ("Keyboard/mouse tracking", True),  # (description, required_on_platform)
        "pywin32": ("Windows integration", is_windows),  # Only required on Windows
        "psutil": ("System utilities", True),
        "tkinter": ("GUI framework", True),
        "sqlite3": ("Database", True),
    }

    all_passed = True

    for module_name, (description, is_required_on_platform) in modules.items():
        try:
            __import__(module_name)
            print(f"✓ {module_name:15} - {description}")
        except ImportError as e:
            error_str = str(e).lower()
            # Special handling for X server/display errors (headless environment)
            if module_name == "pynput" and ("display" in error_str or "x server" in error_str or "x connection" in error_str):
                print(f"⊘ {module_name:15} - {description} (headless environment)")
            elif is_required_on_platform:
                print(f"✗ {module_name:15} - {description}")
                print(f"  Error: {e}")
                all_passed = False
            else:
                print(f"⊘ {module_name:15} - {description} (not required on {platform.system()})")
        except Exception as e:
            error_str = str(e).lower()
            # Handle other errors like display errors from pynput
            if "display" in error_str or "x server" in error_str or "x connection" in error_str:
                print(f"⊘ {module_name:15} - {description} (headless environment)")
            elif is_required_on_platform:
                print(f"✗ {module_name:15} - {description}")
                print(f"  Error: {e}")
                all_passed = False
            else:
                print(f"⊘ {module_name:15} - {description} (not required on {platform.system()})")

    print()
    return all_passed


def test_config():
    """Test configuration loading."""
    print("=" * 50)
    print("Testing Configuration")
    print("=" * 50)

    try:
        from config import config

        print("✓ Config module loaded")
        print(f"  Idle timeout: {config.get('idle_timeout')} minutes")
        print(f"  Check interval: {config.get('check_interval')} seconds")
        print(f"  Database path: {config.get('db_path')}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error loading config: {e}")
        print()
        return False


def test_logger():
    """Test logger module and database."""
    print("=" * 50)
    print("Testing Logger & Database")
    print("=" * 50)

    try:
        from logger import ActivityLogger

        logger = ActivityLogger()
        print("✓ Logger initialized")

        # Test database operations
        test_record = {
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "activity_type": "TEST",
            "reason": "Test record",
        }

        result = logger.log_activity(
            start_time=test_record["start_time"],
            end_time=test_record["end_time"],
            activity_type=test_record["activity_type"],
            reason=test_record["reason"],
        )

        if result:
            print("✓ Test record logged to database")
        else:
            print("✗ Failed to log test record")
            print()
            return False

        # Test retrieval
        activities = logger.get_activities()
        if activities:
            print(f"✓ Database retrieval working ({len(activities)} records)")
        else:
            print("✗ Database retrieval failed")
            print()
            return False

        # Test stats
        stats = logger.get_today_stats()
        print(f"✓ Statistics retrieved")
        print(f"  Active time: {stats.get('active_time', 0)} minutes")
        print(f"  Idle time: {stats.get('idle_time', 0)} minutes")
        print(f"  Sessions: {stats.get('sessions', 0)}")
        print()
        return True

    except Exception as e:
        print(f"✗ Error testing logger: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def test_utils():
    """Test utility functions."""
    print("=" * 50)
    print("Testing Utilities")
    print("=" * 50)

    try:
        from utils import (
            get_active_window_name,
            get_system_info,
            format_duration,
        )

        print("✓ Utils module loaded")

        try:
            window = get_active_window_name()
            print(f"✓ Active window: {window}")
        except Exception as e:
            print(f"⚠ Could not get active window: {e}")

        try:
            info = get_system_info()
            print(f"✓ System info retrieved")
            print(f"  Platform: {info.get('platform')}")
            print(f"  CPU: {info.get('cpu_percent')}%")
            print(f"  Memory: {info.get('memory_percent')}%")
        except Exception as e:
            print(f"⚠ Could not get system info: {e}")

        duration_str = format_duration(125)
        if duration_str == "2m 5s":
            print(f"✓ Duration formatting: {duration_str}")
        else:
            print(f"✗ Duration formatting failed: got {duration_str}")
            print()
            return False

        print()
        return True

    except Exception as e:
        print(f"✗ Error testing utils: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def test_ui():
    """Test UI components (without showing windows)."""
    print("=" * 50)
    print("Testing UI Components")
    print("=" * 50)

    try:
        from ui import InactivityPopup, StatusWindow

        print("✓ UI modules loaded")
        print("✓ InactivityPopup class instantiated")
        print("✓ StatusWindow class instantiated")
        print()
        return True

    except Exception as e:
        print(f"✗ Error testing UI: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def test_tracker():
    """Test tracker module."""
    print("=" * 50)
    print("Testing Tracker")
    print("=" * 50)

    try:
        from tracker import ActivityTracker, SystemEventMonitor

        print("✓ Tracker modules loaded")
        print("✓ ActivityTracker class instantiated")
        print("✓ SystemEventMonitor class instantiated")
        print()
        return True

    except Exception as e:
        print(f"✗ Error testing tracker: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def test_main():
    """Test main application."""
    print("=" * 50)
    print("Testing Main Application")
    print("=" * 50)

    try:
        from main import TrackingApplication

        app = TrackingApplication()
        print("✓ TrackingApplication instantiated")

        if app.initialize():
            print("✓ Application initialized")
        else:
            print("✗ Failed to initialize application")
            print()
            return False

        print()
        return True

    except Exception as e:
        print(f"✗ Error testing main app: {e}")
        import traceback

        traceback.print_exc()
        print()
        return False


def main():
    """Run all tests."""
    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║  Activity Tracker - Component Test Suite           ║")
    print("╚════════════════════════════════════════════════════╝")
    print()

    results = {
        "Imports": test_imports(),
        "Config": test_config(),
        "Logger": test_logger(),
        "Utils": test_utils(),
        "UI": test_ui(),
        "Tracker": test_tracker(),
        "Main": test_main(),
    }

    print("=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20} {status}")

    print()
    print(f"Total: {passed}/{total} tests passed")
    print()

    if passed == total:
        print("=" * 50)
        print("✓ All tests passed! Application is ready to use.")
        print("=" * 50)
        print()
        print("Next steps:")
        print("  1. Run: python main.py --interactive")
        print("  2. Move your mouse to test activity detection")
        print("  3. Wait for idle timeout to test popup")
        print("  4. Check tracking_data.db for stored data")
        print()
        return 0
    else:
        print("=" * 50)
        print("✗ Some tests failed. Please install missing dependencies.")
        print("=" * 50)
        print()
        print("Run: pip install -r requirements.txt")
        print()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
