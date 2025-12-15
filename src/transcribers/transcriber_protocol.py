"""Protocol for transcriber implementations."""

from typing import Callable, Protocol


class TranscriberProtocol(Protocol):
    """Protocol for transcriber implementations."""
    
    def initialize(self) -> bool:
        """Initialize the transcriber (load models, setup audio).
        
        Returns:
            True if initialization successful, False otherwise
        """
        ...
    
    def do_streaming(self, should_continue: Callable[[], bool]) -> bool:
        """Run continuous voice input loop.
        
        Args:
            should_continue: Callable returning bool - continue loop while True
            
        Returns:
            True if streaming completed successfully, False otherwise
        """
        ...
