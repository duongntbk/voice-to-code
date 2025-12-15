"""Protocol for log handler callables."""

from typing import Protocol


class LogHandlerProtocol(Protocol):
    """Protocol for log handler callables."""
    
    def __call__(self, level: str, message: str) -> None:
        """Handle a log message.
        
        Args:
            level: Log level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR')
            message: Log message to handle
        """
        ...
