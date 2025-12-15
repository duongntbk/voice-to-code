"""WhisperMic-based audio transcriber for voice-to-code.

Duck-typed interface expected by this class:
    processor: Any object with accept(text: str) -> bool method
    logger: Logger instance with info() and debug() methods
"""

from typing import Any, Callable

from whisper_mic import WhisperMic

from src.logging.logger_protocol import LoggerProtocol
from src.processors.processor_protocol import ProcessorProtocol

# WhisperMic returns this prefix on timeout instead of raising exception
TIMEOUT_PREFIX = "Timeout:"


class WhisperMicTranscriber:
    """Transcriber using WhisperMic for audio capture and transcription."""
    
    def __init__(self, config: dict[str, Any], logger: LoggerProtocol, processor: ProcessorProtocol) -> None:
        """
        Initialize transcriber with configuration.
        
        Args:
            config: Configuration dict with whisper settings
            logger: Logger instance for logging
            processor: Object with accept(text: str) method to receive transcribed text
        """
        self.config = config
        self.logger = logger
        self.processor = processor
        self.mic = None
        
        # Read listen timeout values once
        self.listen_timeout = config.get('listen_timeout', 2.0)
    
    def is_timeout(self, text: str | None) -> bool:
        """
        Check if text indicates a timeout response from WhisperMic.
        
        Args:
            text: Text to check
            
        Returns:
            True if text is a timeout message, False otherwise
        """
        return text is not None and text.startswith(TIMEOUT_PREFIX)
    
    def initialize(self) -> bool:
        """Initialize WhisperMic with configured parameters."""
        try:
            self.logger.debug(f"Initializing WhisperMic with '{self.config['model']}' model...")
            
            self.mic = WhisperMic(
                model=self.config['model'],
                english=True,
                pause=self.config.get('pause_threshold', 2.0),
                energy=self.config.get('energy_threshold', 100),
                dynamic_energy=self.config.get('dynamic_energy', True),
                verbose=self.config.get('debug', False),
                no_keyboard=True,
            )
            
            self.logger.debug("WhisperMic initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize WhisperMic: {e}")
            return False
    
    def do_streaming(self, should_continue: Callable[[], bool]) -> bool:
        """
        Run continuous voice input loop.
        
        Args:
            should_continue: Callable returning bool - continue loop while True
        
        Note: Loop checks should_continue every config['listen_timeout'] seconds when idle.
              Once speech starts, full phrase is captured regardless of duration.
        """
        if not self.mic:
            self.logger.error("Transcriber not initialized. Call initialize() first.")
            return False
        
        chunk_num = 0
        
        try:
            while should_continue():
                self.logger.debug(f"Waiting for speech (chunk {chunk_num})...")
                
                text = self._listen_and_transcribe()
                
                if text:
                    self.logger.info(f"Transcribed: {text}")
                    self.processor.accept(text)
                
                chunk_num += 1
        finally:
            self.mic = None
            self.logger = None
            self.processor = None
        
        return True

    def _listen_and_transcribe(self) -> str | None:
        """
        Listen for speech, auto-detect pause, and transcribe.
        
        Returns:
            Transcribed text or None if timeout/interrupted/failed.
        """
        try:
            self.logger.debug("Listening for speech...")
            result = self.mic.listen(timeout=self.listen_timeout)
            
            # Handle verbose mode (returns dict) vs normal mode (returns string)
            if isinstance(result, dict):
                text = result.get('text', '')
            else:
                text = result if result else ''
            
            # Check for timeout message
            if self.is_timeout(text):
                self.logger.debug(f"No speech detected within {self.listen_timeout}s timeout")
                return None
            
            if text and text.strip():
                return text.strip()
            else:
                self.logger.debug("No speech detected or empty result")
                return None
                
        except Exception as e:
            self.logger.error(f"Listen/transcription failed: {e}")
            return None
