import json
import os

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "temp_unit": "°C",
    "check_updates": True
}

class ConfigManager:
    @staticmethod
    def load_config():
        if not os.path.exists(CONFIG_FILE):
            return ConfigManager.create_default_config()

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            is_valid = True
            for key in DEFAULT_CONFIG:
                if key not in config:
                    config[key] = DEFAULT_CONFIG[key]
                    is_valid = True

            if is_valid:
                ConfigManager.save_config(config)

            return config

        except (json.JSONDecodeError, TypeError, PermissionError):
            return ConfigManager.create_default_config()

    @staticmethod
    def save_config(config):
        try:
            if not os.path.exists(CONFIG_DIR):
                os.makedirs(CONFIG_DIR)

            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    @staticmethod
    def create_default_config():
        ConfigManager.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()