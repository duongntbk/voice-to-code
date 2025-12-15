"""Tests for logging bridge."""

import logging
from unittest.mock import Mock, patch

from src.logging.logging_bridge import (
    LoggingBridge,
    clear_stdlib_logging_bridge,
    setup_stdlib_logging_bridge,
)


def test_logging_bridge_forwards_info():
    """Test LoggingBridge forwards INFO logs."""
    messages = []
    
    class MockLogger:
        def info(self, msg):
            messages.append(('INFO', msg))
        def debug(self, msg):
            messages.append(('DEBUG', msg))
    
    bridge = LoggingBridge(MockLogger())
    
    # Create a log record and emit
    record = logging.LogRecord(
        name='test', level=logging.INFO, pathname='', lineno=0,
        msg='test message', args=(), exc_info=None
    )
    bridge.emit(record)
    
    assert len(messages) == 1
    assert 'test message' in messages[0][1]


def test_logging_bridge_forwards_debug():
    """Test LoggingBridge forwards DEBUG logs."""
    messages = []
    
    class MockLogger:
        def info(self, msg):
            messages.append(('INFO', msg))
        def debug(self, msg):
            messages.append(('DEBUG', msg))
    
    bridge = LoggingBridge(MockLogger())
    
    record = logging.LogRecord(
        name='test', level=logging.DEBUG, pathname='', lineno=0,
        msg='debug message', args=(), exc_info=None
    )
    bridge.emit(record)
    
    assert len(messages) == 1
    assert messages[0][0] == 'DEBUG'


@patch('logging.getLogger')
@patch('logging.captureWarnings')
def test_setup_stdlib_logging_bridge(mock_capture_warnings, mock_get_logger):
    """Test setup configures stdlib loggers."""
    mock_whisper_mic = Mock()
    mock_whisper = Mock()
    mock_warnings = Mock()
    
    def get_logger_side_effect(name):
        if name == 'whisper_mic':
            return mock_whisper_mic
        elif name == 'whisper':
            return mock_whisper
        elif name == 'py.warnings':
            return mock_warnings
        return Mock()
    
    mock_get_logger.side_effect = get_logger_side_effect
    handler_func = Mock()
    
    setup_stdlib_logging_bridge(handler_func)
    
    # Verify whisper_mic logger configured
    assert len(mock_whisper_mic.handlers) == 1
    mock_whisper_mic.setLevel.assert_called_once_with(logging.INFO)
    assert mock_whisper_mic.propagate is False
    
    # Verify whisper logger configured
    assert len(mock_whisper.handlers) == 1
    mock_whisper.setLevel.assert_called_once_with(logging.WARNING)
    assert mock_whisper.propagate is False
    
    # Verify warnings captured
    mock_capture_warnings.assert_called_once_with(True)
    assert len(mock_warnings.handlers) == 1


@patch('logging.getLogger')
@patch('logging.captureWarnings')
def test_clear_stdlib_logging_bridge(mock_capture_warnings, mock_get_logger):
    """Test clear removes handlers and restores defaults."""
    mock_whisper_mic = Mock()
    mock_whisper = Mock()
    mock_warnings = Mock()
    
    def get_logger_side_effect(name):
        if name == 'whisper_mic':
            return mock_whisper_mic
        elif name == 'whisper':
            return mock_whisper
        elif name == 'py.warnings':
            return mock_warnings
        return Mock()
    
    mock_get_logger.side_effect = get_logger_side_effect
    
    clear_stdlib_logging_bridge()
    
    # Verify handlers cleared
    assert mock_whisper_mic.handlers == []
    assert mock_whisper.handlers == []
    assert mock_warnings.handlers == []
    
    # Verify propagate restored
    assert mock_whisper_mic.propagate is True
    assert mock_whisper.propagate is True
    assert mock_warnings.propagate is True
    
    # Verify warnings disabled
    mock_capture_warnings.assert_called_once_with(False)
