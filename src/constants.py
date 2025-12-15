"""Constants for voice-to-code application."""

from pathlib import Path

# Default AI Agent session name
DEFAULT_AI_AGENT_SESSION = 'ai-voice-input'

# Default log file name
DEFAULT_LOG_FILE = 'voice_input.log'

# Default output directory
DEFAULT_OUTPUT_DIR = Path.home() / '.voice-to-code'

# User config file path
USER_CONFIG_PATH = DEFAULT_OUTPUT_DIR / 'config.py'
