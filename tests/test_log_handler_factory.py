"""Tests for log handler factory."""

import sys
from unittest.mock import Mock, patch

import pytest

# Mock whisper_mic before importing our code (CI server doesn't have it)
sys.modules['whisper_mic'] = Mock()

from src.factories import create_log_handler  # noqa: E402


@patch('src.factories.create_file_handler')
def test_create_log_handler_file(mock_file_handler):
    """Test creating file log handler."""
    config = {'log_handler_type': 'file', 'debug': True}
    log_path = '/tmp/test.log'
    
    handler = create_log_handler(config, log_file_path=log_path)
    
    mock_file_handler.assert_called_once_with(log_path, True, capture_stdlib_logs=True)
    assert handler == mock_file_handler.return_value


@patch('src.factories.create_gui_handler')
def test_create_log_handler_ui(mock_gui_handler):
    """Test creating UI log handler."""
    config = {'log_handler_type': 'ui', 'debug': False}
    widget = Mock()
    
    handler = create_log_handler(config, log_widget=widget)
    
    mock_gui_handler.assert_called_once_with(widget, False, capture_stdlib_logs=False)
    assert handler == mock_gui_handler.return_value


@patch('src.factories.create_gui_handler')
def test_create_log_handler_default_type(mock_gui_handler):
    """Test default log handler type is ui."""
    config = {}
    widget = Mock()
    
    _handler = create_log_handler(config, log_widget=widget)
    
    mock_gui_handler.assert_called_once()


def test_create_log_handler_file_missing_path():
    """Test file handler without path raises ValueError."""
    config = {'log_handler_type': 'file'}
    
    with pytest.raises(ValueError, match="log_file_path required"):
        create_log_handler(config)


def test_create_log_handler_ui_missing_widget():
    """Test UI handler without widget raises ValueError."""
    config = {'log_handler_type': 'ui'}
    
    with pytest.raises(ValueError, match="log_widget required"):
        create_log_handler(config)


def test_create_log_handler_unknown_type():
    """Test unknown handler type raises ValueError."""
    config = {'log_handler_type': 'unknown'}
    
    with pytest.raises(ValueError, match="Unknown log handler type"):
        create_log_handler(config)


@patch('src.factories.create_file_handler')
def test_create_log_handler_passes_debug_mode(mock_file_handler):
    """Test debug mode is passed to handler."""
    config = {'log_handler_type': 'file', 'debug': True}
    
    create_log_handler(config, log_file_path='/tmp/test.log')
    
    # Verify debug=True and capture_stdlib_logs=True were passed
    call_args = mock_file_handler.call_args
    assert call_args[0][1] is True
    assert call_args[1]['capture_stdlib_logs'] is True
