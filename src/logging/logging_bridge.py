"""Bridge Python's logging module to our Logger."""

import logging


class LoggingBridge(logging.Handler):
    """Handler that bridges stdlib logging to our Logger instance."""
    
    def __init__(self, our_logger):
        """
        Initialize bridge.
        
        Args:
            our_logger: Our Logger instance
        """
        super().__init__()
        self.our_logger = our_logger
    
    def emit(self, record):
        """Handle a log record from stdlib logging."""
        try:
            msg = self.format(record)
            
            # Map logging levels to our logger methods
            if record.levelno >= logging.ERROR:
                self.our_logger.info(f"[{record.name}] {msg}")
            elif record.levelno >= logging.WARNING:
                self.our_logger.info(f"[{record.name}] {msg}")
            elif record.levelno >= logging.INFO:
                self.our_logger.info(f"[{record.name}] {msg}")
            else:
                self.our_logger.debug(f"[{record.name}] {msg}")
        except Exception as e:
            import sys
            print(f"WARNING: Logging bridge failed: {e}", file=sys.stderr)


def setup_stdlib_logging_bridge(handler_func):
    """
    Set up stdlib logging bridge using a handler function.
    
    Note: Clears any existing handlers on whisper/whisper_mic loggers first.
    
    Args:
        handler_func: Handler function(level, message) to receive logs
    """
    # Create a dummy logger that forwards to handler function
    class BridgeLogger:
        def debug(self, msg):
            handler_func('DEBUG', msg)
        def info(self, msg):
            handler_func('INFO', msg)
        def warning(self, msg):
            handler_func('WARNING', msg)
        def error(self, msg):
            handler_func('ERROR', msg)
    
    bridge = LoggingBridge(BridgeLogger())
    
    # Capture whisper_mic logs (clear old handlers first)
    whisper_mic_logger = logging.getLogger('whisper_mic')
    whisper_mic_logger.handlers = [bridge]
    whisper_mic_logger.setLevel(logging.INFO)
    whisper_mic_logger.propagate = False
    
    # Capture whisper logs (clear old handlers first)
    whisper_logger = logging.getLogger('whisper')
    whisper_logger.handlers = [bridge]
    whisper_logger.setLevel(logging.WARNING)
    whisper_logger.propagate = False
    
    # Capture Python warnings (like FP16 warning)
    logging.captureWarnings(True)
    warnings_logger = logging.getLogger('py.warnings')
    warnings_logger.handlers = [bridge]
    warnings_logger.setLevel(logging.WARNING)
    warnings_logger.propagate = False


def clear_stdlib_logging_bridge():
    """Restore default logging behavior (remove bridges, restore propagation)."""
    # Restore whisper_mic to default behavior
    whisper_mic_logger = logging.getLogger('whisper_mic')
    whisper_mic_logger.handlers = []
    whisper_mic_logger.propagate = True  # Let it use default console output
    
    # Restore whisper to default behavior
    whisper_logger = logging.getLogger('whisper')
    whisper_logger.handlers = []
    whisper_logger.propagate = True
    
    # Restore warnings to default
    warnings_logger = logging.getLogger('py.warnings')
    warnings_logger.handlers = []
    warnings_logger.propagate = True
    logging.captureWarnings(False)
