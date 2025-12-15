"""Protocol for logger implementations."""

from typing import Protocol


class LoggerProtocol(Protocol):
    """Protocol for logger implementations."""
    
    def debug(self, message: str) -> None:
        """Log debug message.
        
        Args:
            message: Message to log
        """
        ...
    
    def info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Message to log
        """
        ...
    
    def warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Message to log
        """
        ...
    
    def error(self, message: str) -> None:
        """Log error message.
        
        Args:
            message: Message to log
        """
        ...
