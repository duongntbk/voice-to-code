"""Utility to write configuration to config.py file."""



def write_config_to_file(config_dict, config_file_path):
    """
    Write configuration dictionary to config.py file.
    
    Args:
        config_dict: Dictionary of configuration values
        config_file_path: Path to config.py file
    """
    # Format the config dictionary
    lines = ["# Voice-to-Code Configuration\n\n", "CONFIG = {\n"]
    
    for key, value in config_dict.items():
        # Format the comment
        comment = _get_config_comment(key)
        if comment:
            lines.append(f"    {comment}\n")
        
        # Format the value
        formatted_value = _format_value(value)
        lines.append(f"    '{key}': {formatted_value},\n")
        lines.append("\n")
    
    # Remove last newline and close dict
    if lines[-1] == "\n":
        lines.pop()
    lines.append("}\n")
    
    # Write to file
    with open(config_file_path, 'w') as f:
        f.writelines(lines)


def _format_value(value):
    """Format a Python value for writing to config file."""
    if isinstance(value, bool):
        return str(value)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        # Check if it's a path-like string
        if value.startswith('/') or value.startswith('~'):
            return f'Path("{value}")'
        return f"'{value}'"
    else:
        return repr(value)


def _get_config_comment(key):
    """Get comment for a config key."""
    comments = {
        'transcriber_type': '# Transcriber type: which speech-to-text implementation to use',
        'processor_type': '# Processor type: where to send transcribed text',
        'vocalize_response': '# Vocalize AI agent responses using text-to-speech',
        'model': '# Whisper model: tiny, base, small, medium, large\n    # Trade-off: larger = more accurate but slower',
        'pause_threshold': '# Pause threshold: seconds of silence before ending a phrase',
        'listen_timeout': '# Listen timeout: max seconds to wait for speech to start before checking stop flag',
        'energy_threshold': '# Energy threshold: minimum audio energy to detect speech (higher = less sensitive)\n    # Default 300 works for most environments',
        'dynamic_energy': '# Dynamic energy: auto-adjust energy threshold based on ambient noise',
        'log_handler_type': '# Log handler type: where to send log messages',
        'debug': '# Debug mode: log detailed operation info\n    # False = only log start/stop/errors/transcriptions\n    # True = log all operational details',
    }
    return comments.get(key, '')
