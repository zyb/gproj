import json
import os
import appdirs # For platform-independent config directory

APP_NAME = "ScreenshotTool"
APP_AUTHOR = "ScreenshotToolDev" # Or your specific author name

# Determine configuration directory using appdirs
CONFIG_DIR = appdirs.user_config_dir(APP_NAME, APP_AUTHOR)
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "general": {
        "default_save_path": os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots"),
        "screenshot_filename_format": "screenshot_{datetime}.png",
        "auto_copy_to_clipboard": False,
        "auto_start_on_boot": False, # Placeholder
    },
    "output": {
        "image_format": "PNG", # Options: PNG, JPG, BMP
        "image_quality_jpg": 90, # 1-100
        "video_format": "MP4", # Options: MP4, AVI
        "video_fps": 15.0,
    },
    "interface": {
        "theme": "Light", # Options: Light, Dark (Placeholder)
        "language": "en", # Default UI language
    }
}

# Global variable to hold the current configuration
_current_config = None

def load_config():
    """
    Loads configuration from the config file.
    If the file doesn't exist or is invalid, returns default settings
    and attempts to create/fix the config file with defaults.
    """
    global _current_config
    if _current_config is not None: # Already loaded
        return _current_config

    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                loaded_settings = json.load(f)
                # Basic validation: check if top-level keys exist
                if all(key in loaded_settings for key in DEFAULT_CONFIG.keys()):
                    # Further merge loaded settings with defaults to ensure all keys are present
                    # and new default settings are introduced if config file is from older version
                    config_to_use = {}
                    for section_key, section_defaults in DEFAULT_CONFIG.items():
                        loaded_section = loaded_settings.get(section_key, {})
                        config_to_use[section_key] = {**section_defaults, **loaded_section}
                    
                    _current_config = config_to_use
                    return _current_config
                else:
                    print(f"Warning: Config file {CONFIG_FILE_PATH} seems corrupted or outdated. Using defaults.")
                    _current_config = DEFAULT_CONFIG.copy() # Use a copy
                    save_config(_current_config) # Try to save defaults back
                    return _current_config
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {CONFIG_FILE_PATH}. Using default settings.")
            _current_config = DEFAULT_CONFIG.copy()
            save_config(_current_config) # Try to save defaults back
            return _current_config
        except Exception as e:
            print(f"An unexpected error occurred while loading config: {e}. Using default settings.")
            _current_config = DEFAULT_CONFIG.copy()
            # Optionally save defaults back, or handle more gracefully
            # save_config(_current_config) 
            return _current_config
    else:
        print(f"Config file not found at {CONFIG_FILE_PATH}. Creating with default settings.")
        _current_config = DEFAULT_CONFIG.copy()
        save_config(_current_config)
        return _current_config

def save_config(config_data):
    """
    Saves the current configuration data to the config file.
    """
    global _current_config
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        _current_config = config_data # Update the global cache
        print(f"Configuration saved to {CONFIG_FILE_PATH}")
        return True
    except Exception as e:
        print(f"Error saving configuration to {CONFIG_FILE_PATH}: {e}")
        return False

def get_setting(section_key, value_key, default_value=None):
    """
    Helper function to get a single configuration value.
    Loads config if not already loaded.
    """
    config = load_config() # Ensure config is loaded
    # Use section_key and value_key to navigate the config dictionary
    default_from_structure = DEFAULT_CONFIG.get(section_key, {}).get(value_key, default_value)
    return config.get(section_key, {}).get(value_key, default_from_structure)

def update_setting(section_key, value_key, new_value):
    """
    Updates a single configuration value in the global config cache.
    Does NOT automatically save to file; save_config must be called.
    """
    global _current_config
    config = load_config() # Ensure config is loaded and up-to-date
    
    if section_key not in config:
        config[section_key] = {}
    config[section_key][value_key] = new_value
    _current_config = config # Update the global cache

if __name__ == '__main__':
    print(f"Config file path: {CONFIG_FILE_PATH}")
    
    # Test loading (or creating default)
    current_settings = load_config()
    print("\nInitial or Loaded Config:")
    print(json.dumps(current_settings, indent=4))

    # Test getting a specific setting
    save_path = get_setting("general", "default_save_path")
    print(f"\nDefault save path from get_setting: {save_path}")

    # Test updating a setting (in memory) then saving
    # Simulate changing default_save_path
    new_save_path = "/tmp/my_screenshots"
    update_setting("general", "default_save_path", new_save_path)
    
    # This change is only in _current_config until save_config is called
    print(f"\nSave path after update_setting (in memory): {get_setting('general', 'default_save_path')}")

    # Save the modified config
    if save_config(_current_config): # _current_config should have the update
        print("\nConfig saved successfully after update.")
        
        # Verify by reloading
        _current_config = None # Reset cache to force reload
        reloaded_settings = load_config()
        print("\nReloaded Config:")
        print(json.dumps(reloaded_settings, indent=4))
        reloaded_save_path = get_setting("general", "default_save_path")
        print(f"\nDefault save path from reloaded config: {reloaded_save_path}")
        if reloaded_save_path == new_save_path:
            print("Setting update and save successful!")
        else:
            print("Error: Setting update not reflected after reload.")
            
        # Restore original default for next test run (optional)
        # update_setting("general", "default_save_path", DEFAULT_CONFIG["general"]["default_save_path"])
        # save_config(_current_config)
        # print("\nRestored default save path for next run.")

    else:
        print("\nFailed to save config after update.")

    # Test getting a non-existent key with default
    non_existent = get_setting("general", "non_existent_key", "fallback_value")
    print(f"\nTest non_existent_key: {non_existent}")

    # Test loading language from config
    lang = get_setting("interface", "language", "en")
    print(f"\nLanguage from config: {lang}")
    if lang != DEFAULT_CONFIG["interface"]["language"]:
         update_setting("interface", "language", DEFAULT_CONFIG["interface"]["language"])
         save_config(load_config())
         print(f"Restored language to default: {DEFAULT_CONFIG['interface']['language']}")
