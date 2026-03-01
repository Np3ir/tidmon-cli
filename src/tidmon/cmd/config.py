import logging
from tidmon.core.config import Config

log = logging.getLogger(__name__)


class ConfigCommand:
    def __init__(self, config: Config = None):
        self.config = config or Config()

    def show(self):
        """Display all configuration values."""
        self.config.show_config()

    def get_all(self):
        """Print all config key-value pairs."""
        try:
            all_config = self.config.get_all()
            print("\n  CURRENT CONFIGURATION\n")
            for key, value in sorted(all_config.items()):
                sensitive = key in ('access_token', 'refresh_token', 'email_password')
                display = "***" if (sensitive and value) else value
                print(f"  {key:30} = {display}")
            print()
        except Exception as e:
            log.error(f"Could not display configuration: {e}")

    def get_key(self, key: str):
        """Print the value of a specific key."""
        value = self.config.get_value(key)
        if value is None:
            print(f"  Key '{key}' not found.")
        else:
            print(f"  {key} = {value}")

    def set_key(self, key: str, value: str):
        """Set a configuration key."""
        if self.config.set_value(key, value):
            print(f"  ✓ Set '{key}' = '{self.config.get_value(key)}'")
        else:
            print(f"  ✗ Failed to set '{key}'")

    def path(self):
        """Print the configuration file path."""
        print(f"\n  Config file: {self.config.get_config_file_path()}\n")