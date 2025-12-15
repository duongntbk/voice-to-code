"""GUI logging handler for voice-to-code."""

import tkinter as tk
from datetime import datetime
from typing import Any

from src.logging.log_handler_protocol import LogHandlerProtocol


def create_gui_handler(log_widget: Any, debug_mode: bool = False, capture_stdlib_logs: bool = False) -> LogHandlerProtocol:
    """
    Create a GUI logging handler.
    
    Args:
        log_widget: tkinter widget with insert() and see() methods (e.g., ScrolledText)
        debug_mode: If True, log DEBUG messages; if False, only INFO
        capture_stdlib_logs: If True, capture WhisperMic stdlib logging (requires debug_mode)
    
    Returns:
        Handler function(level, message)
    """
    
    def handler(level: str, message: str) -> None:
        # Skip DEBUG messages if not in debug mode
        if level == 'DEBUG' and not debug_mode:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        try:
            log_widget.insert(tk.END, log_entry)
            log_widget.see(tk.END)  # Auto-scroll to bottom
        except Exception as e:
            import sys
            print(f"WARNING: GUI log handler failed: {e}", file=sys.stderr)
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
