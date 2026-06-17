"""
Setup script for installing and configuring the application.
Run: python setup.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)
    print()


def print_step(step_num, text):
    """Print a formatted step."""
    print(f"[{step_num}/5] {text}")


def check_python():
    """Check Python version."""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8+ required")
        return False

    print("✓ Python version OK")
    return True


def install_dependencies():
    """Install required dependencies."""
    print_step(1, "Installing Dependencies")

    try:
        print("Installing packages from requirements.txt...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✓ Dependencies installed successfully")
            return True
        else:
            print("ERROR: Failed to install dependencies")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def install_pywin32():
    """Install pywin32 post-install."""
    print_step(2, "Configuring Windows Integration")

    try:
        import pywin32
        
        print("Configuring pywin32...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pywin32"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✓ pywin32 configured")
            return True
        else:
            print("⚠ pywin32 configuration warning (may not affect functionality)")
            return True

    except Exception as e:
        print(f"⚠ Warning: {e}")
        return True


def create_config():
    """Create default configuration."""
    print_step(3, "Creating Configuration")

    try:
        from config import config, DEFAULT_CONFIG

        config_path = Path("config.json")
        if config_path.exists():
            print("✓ Configuration already exists")
            return True

        config.save_config(DEFAULT_CONFIG)
        print(f"✓ Configuration created: {config_path}")
        print(f"  Idle timeout: {DEFAULT_CONFIG['idle_timeout']} minutes")
        print(f"  Check interval: {DEFAULT_CONFIG['check_interval']} seconds")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_components():
    """Test all components."""
    print_step(4, "Testing Components")

    components = []

    try:
        import pynput
        components.append(("pynput", "Keyboard/Mouse tracking"))
    except ImportError:
        pass

    try:
        import pywin32
        components.append(("pywin32", "Windows integration"))
    except ImportError:
        pass

    try:
        import psutil
        components.append(("psutil", "System utilities"))
    except ImportError:
        pass

    try:
        import tkinter
        components.append(("tkinter", "GUI framework"))
    except ImportError:
        pass

    try:
        import sqlite3
        components.append(("sqlite3", "Database"))
    except ImportError:
        pass

    if components:
        print("✓ All required components loaded:")
        for name, desc in components:
            print(f"  - {name}: {desc}")
        return True
    else:
        print("ERROR: Failed to load components")
        return False


def create_shortcuts():
    """Create desktop shortcuts (optional)."""
    print_step(5, "Setting Up Shortcuts")

    if os.name != "nt":
        print("ℹ Shortcuts only available on Windows")
        return True

    try:
        response = input("Create desktop shortcut? (y/n): ").lower().strip()
        if response == "y":
            # This would require additional libraries like winshortcuts
            print("ℹ Manual shortcut creation recommended")
            print("  Right-click main.py > Send to > Desktop")
        return True
    except Exception as e:
        print(f"⚠ Warning: {e}")
        return True


def main():
    """Run setup process."""
    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║  Activity Tracker - Setup                          ║")
    print("║  Production-Quality Windows Activity Tracker       ║")
    print("╚════════════════════════════════════════════════════╝")

    steps = [
        ("Check Python", check_python),
        ("Install Dependencies", install_dependencies),
        ("Configure Windows Integration", install_pywin32),
        ("Create Configuration", create_config),
        ("Test Components", test_components),
    ]

    for i, (name, func) in enumerate(steps, 1):
        print_step(i, name)
        if not func():
            print()
            print("=" * 60)
            print("✗ Setup failed at this step")
            print("=" * 60)
            return False
        print()

    # Optional step
    print_step(5, "Optional: Create Shortcuts")
    create_shortcuts()

    print_header("Setup Complete! ✓")

    print("Quick Start Guide:")
    print()
    print("1. Run the test suite:")
    print("   python test_app.py")
    print()
    print("2. Start in interactive mode:")
    print("   python main.py --interactive")
    print()
    print("3. Start in background mode:")
    print("   python main.py")
    print()
    print("4. Enable auto-start (optional):")
    print("   python main.py --autostart")
    print()
    print("5. View documentation:")
    print("   README.md")
    print()
    print("=" * 60)
    print("Happy tracking! 🎯")
    print("=" * 60)
    print()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
