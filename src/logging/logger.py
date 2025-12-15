"""Logger with configurable handlers for voice-to-code."""

from src.logging.log_handler_protocol import LogHandlerProtocol


class Logger:
    """Logger that delegates to configured handlers."""
    
    def __init__(self, handlers: LogHandlerProtocol | list[LogHandlerProtocol]) -> None:
        """
        Initialize logger with handlers.
        
        Args:
            handlers: Single handler or list of handlers.
                     Each handler is callable(level: str, message: str)
        """
        self.handlers = handlers if isinstance(handlers, list) else [handlers]
    
    def debug(self, message: str) -> None:
        """Log debug message to all handlers."""
        for handler in self.handlers:
            handler('DEBUG', message)
    
    def info(self, message: str) -> None:
        """Log info message to all handlers."""
        for handler in self.handlers:
            handler('INFO', message)
    
    def warning(self, message: str) -> None:
        """Log warning message to all handlers."""
        for handler in self.handlers:
            handler('WARNING', message)
    
    def error(self, message: str) -> None:
        """Log error message to all handlers."""
        for handler in self.handlers:
            handler('ERROR', message)
