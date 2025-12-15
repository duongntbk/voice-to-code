"""Configuration manager for voice-to-code."""

import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration with file persistence."""
    
    _instance = None
    _config = None
    _config_file_path = None
    
    @classmethod
    def initialize(cls) -> None:
        """
        Initialize the config manager.
        
        Auto-detects bundled vs source mode and sets appropriate config path.
        For bundled apps: copies bundled config.py to ~/.voice-to-code/ on first run.
        For source: uses repo config.py.
        """
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            bundled_config = Path(sys._MEIPASS) / 'config.py'
            user_config = Path.home() / '.voice-to-code' / 'config.py'
            
            # Copy bundled config to user location on first run
            if not user_config.exists():
                user_config.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(bundled_config, user_config)
            
            cls._config_file_path = user_config
        else:
            # Running from source - use repo config.py
            cls._config_file_path = Path(__file__).parent.parent.parent / 'config.py'
        
        cls.load()
    
    @classmethod
    def load(cls) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Config dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            Exception: If config file is invalid Python
        """
        if not cls._config_file_path:
            raise RuntimeError("ConfigManager not initialized. Call initialize() first.")
        
        if not cls._config_file_path.exists():
            raise FileNotFoundError(f"Config file not found: {cls._config_file_path}")
        
        # Import config module dynamically
        spec = importlib.util.spec_from_file_location("config", cls._config_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        cls._config = module.CONFIG.copy()  # Copy to avoid external mutations
        return cls._config
    
    @classmethod
    def get(cls) -> Dict[str, Any]:
        """
        Get current configuration.
        
        Returns:
            Config dictionary (copy to prevent mutation)
        """
        if cls._config is None:
            cls.load()
        
        return cls._config.copy()
    
    @classmethod
    def save(cls, new_config: Dict[str, Any]) -> None:
        """
        Save configuration to file and update in-memory config.
        
        Args:
            new_config: New configuration dictionary
        """
        if not cls._config_file_path:
            raise RuntimeError("ConfigManager not initialized. Call initialize() first.")
        
        # Write to file
        from src.utils.config_writer import write_config_to_file
        write_config_to_file(new_config, cls._config_file_path)
        
        # Update in-memory config
        cls._config = new_config.copy()
    
    @classmethod
    def get_value(cls, key: str, default=None) -> Any:
        """
        Get a specific config value.
        
        Args:
            key: Config key
            default: Default value if key not found
            
        Returns:
            Config value
        """
        config = cls.get()
        return config.get(key, default)
    
    @classmethod
    def update(cls, updates: Dict[str, Any]) -> None:
        """
        Update specific config values and save.
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        current = cls.get()
        current.update(updates)
        cls.save(current)
    
    @classmethod
    def reset(cls) -> None:
        """Reset config manager state (useful for testing)."""
        cls._config = None
        cls._config_file_path = None
