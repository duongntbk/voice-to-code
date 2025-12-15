# Voice-to-Code Configuration

CONFIG = {
    # Transcriber type: which speech-to-text implementation to use
    'transcriber_type': 'whisper_mic',

    # Processor type: where to send transcribed text
    'processor_type': 'tmux',

    # Whisper model: tiny, base, small, medium, large
    # Trade-off: larger = more accurate but slower
    'model': 'large',

    # Pause threshold: seconds of silence before ending a phrase
    'pause_threshold': 2.0,

    # Listen timeout: max seconds to wait for speech to start before checking stop flag
    'listen_timeout': 2.0,

    # Energy threshold: minimum audio energy to detect speech (higher = less sensitive)
    # Default 300 works for most environments
    'energy_threshold': 200,

    # Dynamic energy: auto-adjust energy threshold based on ambient noise
    'dynamic_energy': True,

    # Vocalize AI agent responses using text-to-speech
    'vocalize_response': False,

    # Log handler type: where to send log messages
    'log_handler_type': 'ui',

    # Debug mode: log detailed operation info
    # False = only log start/stop/errors/transcriptions
    # True = log all operational details
    'debug': True,
}
