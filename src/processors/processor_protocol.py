"""Protocol for processor implementations."""

from typing import Protocol


class ProcessorProtocol(Protocol):
    """Protocol for processor implementations."""
    
    def accept(self, text: str) -> None:
        """Process transcribed text.
        
        Args:
            text: Transcribed text to process
            
        Raises:
            Exception if processing fails (e.g., session not found)
        """
        ...

    def toggle_vocalization(self, is_on: bool) -> None:
        """Toggle vocalization settings on AI Agent side
        Note: This is a noop on non-macOS system

        Args:
           is_on: Flag to indicate whether response vocalization should be turn on or not.
        """
        ...
