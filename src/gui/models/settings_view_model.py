"""ViewModel for settings dialog."""

import tkinter as tk
from typing import Any


class SettingsViewModel:
    """ViewModel holding state for the settings dialog."""
    
    def __init__(self) -> None:
        # Transcriber and processor types
        self.transcriber_options = ['whisper_mic']
        self.transcriber_type = tk.StringVar(value='whisper_mic')
        
        self.processor_options = ['tmux']
        self.processor_type = tk.StringVar(value='tmux')
        
        # Whisper model options
        self.model_options = ['tiny', 'base', 'small', 'medium', 'large']
        self.model = tk.StringVar(value='large')
        
        # Audio thresholds
        self.pause_threshold = tk.DoubleVar(value=2.0)
        self.listen_timeout = tk.DoubleVar(value=2.0)
        self.energy_threshold = tk.IntVar(value=100)
        self.dynamic_energy = tk.BooleanVar(value=True)
        
        # General settings
        self.vocalize_response = tk.BooleanVar(value=False)
        
        # Logging settings
        self.log_handler_options = ['ui', 'file']
        self.log_handler_type = tk.StringVar(value='ui')
        self.debug = tk.BooleanVar(value=False)
    
    def load_from_config(self, config: dict[str, Any]) -> None:
        """Load values from config into form fields."""
        self.transcriber_type.set(config.get('transcriber_type', 'whisper_mic'))
        self.processor_type.set(config.get('processor_type', 'tmux'))
        self.model.set(config.get('model', 'large'))
        self.pause_threshold.set(config.get('pause_threshold', 2.0))
        self.listen_timeout.set(config.get('listen_timeout', 2.0))
        self.energy_threshold.set(config.get('energy_threshold', 100))
        self.dynamic_energy.set(config.get('dynamic_energy', True))
        self.vocalize_response.set(config.get('vocalize_response', False))
        self.log_handler_type.set(config.get('log_handler_type', 'ui'))
        self.debug.set(config.get('debug', False))
    
    def get_config_dict(self) -> dict[str, Any]:
        """Get current settings as a dictionary."""
        return {
            'transcriber_type': self.transcriber_type.get(),
            'processor_type': self.processor_type.get(),
            'model': self.model.get(),
            'pause_threshold': self.pause_threshold.get(),
            'listen_timeout': self.listen_timeout.get(),
            'energy_threshold': self.energy_threshold.get(),
            'dynamic_energy': self.dynamic_energy.get(),
            'vocalize_response': self.vocalize_response.get(),
            'log_handler_type': self.log_handler_type.get(),
            'debug': self.debug.get(),
        }
