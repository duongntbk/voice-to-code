"""Factory functions for creating transcribers, processors, and log handlers."""

from pathlib import Path
from typing import Any

from src.logging.file_log_handler import create_file_handler
from src.logging.gui_log_handler import create_gui_handler
from src.logging.log_handler_protocol import LogHandlerProtocol
from src.logging.logger_protocol import LoggerProtocol
from src.processors.processor_protocol import ProcessorProtocol
from src.processors.tmux_processor import TmuxProcessor
from src.transcribers.transcriber_protocol import TranscriberProtocol
from src.transcribers.whisper_mic_transcriber import WhisperMicTranscriber


def create_processor(config: dict[str, Any], get_session_name, logger: LoggerProtocol) -> ProcessorProtocol:
    """
    Create processor based on config.
    
    Args:
        config: Configuration dict with 'processor_type' key
        get_session_name: Callable returning current session name
        logger: Logger instance
    
    Returns:
        Processor instance
    
    Raises:
        ValueError: If processor_type is unknown
    """
    proc_type = config.get('processor_type', 'tmux')
    
    if proc_type == 'tmux':
        return TmuxProcessor(get_session_name, logger)
    else:
        raise ValueError(f"Unknown processor type: {proc_type}")


def create_transcriber(config: dict[str, Any], logger: LoggerProtocol, processor: ProcessorProtocol) -> TranscriberProtocol:
    """
    Create transcriber based on config.
    
    Args:
        config: Configuration dict with 'transcriber_type' key
        logger: Logger instance
        processor: Processor instance to receive transcribed text
    
    Returns:
        Transcriber instance
    
    Raises:
        ValueError: If transcriber_type is unknown
    """
    trans_type = config.get('transcriber_type', 'whisper_mic')
    
    if trans_type == 'whisper_mic':
        return WhisperMicTranscriber(config, logger, processor)
    else:
        raise ValueError(f"Unknown transcriber type: {trans_type}")


def create_log_handler(config: dict[str, Any], log_file_path: Path | str | None = None, log_widget: Any = None) -> LogHandlerProtocol:
    """
    Create log handler based on config.
    
    Args:
        config: Configuration dict with 'log_handler_type' key
        log_file_path: Path to log file (required for 'file' type)
        log_widget: GUI widget (required for 'ui' type)
    
    Returns:
        Log handler function
    
    Raises:
        ValueError: If handler_type is unknown or required param is missing
    """
    handler_type = config.get('log_handler_type', 'ui')
    debug_mode = config.get('debug', False)
    
    if handler_type == 'file':
        if not log_file_path:
            raise ValueError("log_file_path required for 'file' handler type")
        return create_file_handler(log_file_path, debug_mode, capture_stdlib_logs=debug_mode)
    elif handler_type == 'ui':
        if not log_widget:
            raise ValueError("log_widget required for 'ui' handler type")
        return create_gui_handler(log_widget, debug_mode, capture_stdlib_logs=debug_mode)
    else:
        raise ValueError(f"Unknown log handler type: {handler_type}")
