"""File logging handler for voice-to-code."""

from datetime import datetime
from pathlib import Path

from src.logging.log_handler_protocol import LogHandlerProtocol


def create_file_handler(log_file_path: Path | str, debug_mode: bool = False, capture_stdlib_logs: bool = False) -> LogHandlerProtocol:
    """
    Create a file logging handler.
    
    Args:
        log_file_path: Path to log file
        debug_mode: If True, log DEBUG messages; if False, only INFO
        capture_stdlib_logs: If True, capture WhisperMic stdlib logging (requires debug_mode)
    
    Returns:
        Handler function(level, message)
    """
    log_file = Path(log_file_path)
    
    def handler(level: str, message: str) -> None:
        # Skip DEBUG messages if not in debug mode
        if level == 'DEBUG' and not debug_mode:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        try:
            with open(log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            import sys
            print(f"WARNING: File log handler failed: {e}", file=sys.stderr)
            print(f"  Message was: [{level}] {message}", file=sys.stderr)
    
    # Set up stdlib logging bridge if requested
    from src.logging.logging_bridge import (
        clear_stdlib_logging_bridge,
        setup_stdlib_logging_bridge,
    )
    
    if capture_stdlib_logs and debug_mode:
        setup_stdlib_logging_bridge(handler)
    else:
        clear_stdlib_logging_bridge()
    
    return handler
