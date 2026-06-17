"""
Configuration module for the tracking application.
Handles all configuration settings and defaults.
"""

import json
import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "idle_timeout": 5,  # minutes
    "check_interval": 2,  # seconds
    "auto_start": False,
    "system_tray": True,
    "db_path": "tracking_data.db",
    "log_path": "app_logs.txt",
    "show_notifications": True,
}

CONFIG_FILE = "config.json"


class Config:
    """Configuration manager for the application."""

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file or use defaults."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**DEFAULT_CONFIG, **config}
            else:
                self.save_config(DEFAULT_CONFIG)
                return DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()

    def save_config(self, config: dict = None) -> bool:
        """Save configuration to file."""
        try:
            config_to_save = config or self.config
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_to_save, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value):
        """Set a configuration value."""
        self.config[key] = value
        self.save_config()

    def get_all(self) -> dict:
        """Get all configuration."""
        return self.config.copy()


# Global config instance
config = Config()
