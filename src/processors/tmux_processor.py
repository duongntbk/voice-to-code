"""Tmux-based text processor for voice-to-code.

Duck-typed interface:
    Implements accept(text: str) method expected by transcribers
"""

import subprocess

from typing import Callable
from src.logging.logger_protocol import LoggerProtocol
from src.utils.os_detection import get_os_type, OSType


class TmuxProcessor:
    """Processor that sends transcribed text to a tmux session."""

    __START_RESPONSE_VOCALIZATION_PROMPT = (
        "From the next prompt not include this one, "
        "after each response, use bash to run: say 'concise summary'. "
        "Max 2 sentences for the summary."
    )
    __STOP_RESPONSE_VOCALIZATION_PROMPT = (
        "Stop vocalizing responses if you were doing so. "
        "Do not use say commands anymore."
    )
    
    def __init__(self, get_session_name: Callable[[], str], logger: LoggerProtocol) -> None:
        """
        Initialize tmux processor.
        
        Args:
            get_session_name: Callable returning current session name
            logger: Logger instance for logging
        """
        self.get_session_name = get_session_name
        self.logger = logger
    
    def accept(self, text: str) -> None:
        """
        Send transcribed text to tmux session.
        
        Args:
            text: Transcribed text to send
            
        Raises:
            subprocess.CalledProcessError if tmux command fails
        """
        if not text:
            return
        
        session_name = self.get_session_name()
        
        # Sanitize: remove newlines to prevent command injection
        clean_text = text.replace('\n', ' ').replace('\r', ' ')
        
        try:
            self.logger.info(f"Sending to tmux session '{session_name}'")
            
            # Use -l flag for literal text (prevents control sequence interpretation)
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, "-l", clean_text
            ], check=True)
            
            # Send Enter separately
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, "Enter"
            ], check=True)
        except subprocess.CalledProcessError as e:
            # Swallow exception - user can fix by changing session dropdown dynamically
            # Transcription continues, no need to restart
            self.logger.error(f"Failed to send to tmux session '{session_name}': {e}")
            self.logger.info("Fix: Change session in dropdown or start tmux session")

    def toggle_vocalization(self, is_on: bool) -> None:
        """Toggle vocalization settings on AI Agent side
        Note: This is a noop on non-macOS system

        Args:
           is_on: Flag to indicate whether response vocalization should be turn on or not
        """

        if get_os_type() != OSType.MACOS:
            return
        
        session_name = self.get_session_name()
        prompt_to_send = self.__START_RESPONSE_VOCALIZATION_PROMPT if is_on else self.__STOP_RESPONSE_VOCALIZATION_PROMPT

        try:
            subprocess.run([
                "tmux", "send-keys", "-t", session_name, "-l", prompt_to_send
            ], check=True)

            subprocess.run([
                "tmux", "send-keys", "-t", session_name, "Enter"
            ], check=True)

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to set response vocalization to {is_on}: {e}")
