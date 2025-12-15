"""Tests for TmuxProcessor class."""

import subprocess
from unittest.mock import Mock, patch

from src.processors.tmux_processor import TmuxProcessor


def test_initialization_stores_callable():
    """Test processor stores get_session_name callable."""
    get_session = Mock(return_value='my-session')
    logger = Mock()
    
    processor = TmuxProcessor(get_session, logger)
    
    assert processor.get_session_name == get_session
    assert processor.logger == logger
    assert processor.get_session_name() == 'my-session'


@patch('subprocess.run')
def test_accept_sends_to_tmux(mock_run):
    """Test accept sends text with correct tmux commands."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.accept("Hello world")
    
    # Should call tmux twice: send-keys with text, then Enter
    assert mock_run.call_count == 2
    get_session.assert_called()
    
    calls = mock_run.call_args_list
    assert calls[0][0][0] == ["tmux", "send-keys", "-t", "test-session", "-l", "Hello world"]
    assert calls[1][0][0] == ["tmux", "send-keys", "-t", "test-session", "Enter"]


@patch('subprocess.run')
def test_accept_sanitizes_newlines(mock_run):
    """Test accept removes newlines from text."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.accept("Line1\nLine2\rLine3")
    
    # Should send with newlines replaced by spaces
    calls = mock_run.call_args_list
    assert calls[0][0][0] == ["tmux", "send-keys", "-t", "test-session", "-l", "Line1 Line2 Line3"]


@patch('subprocess.run')
def test_accept_sanitizes_mixed_newlines(mock_run):
    """Test accept handles mixed newline characters."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.accept("First\n\rSecond\r\nThird")
    
    calls = mock_run.call_args_list
    # All newlines should be replaced with spaces
    assert calls[0][0][0] == ["tmux", "send-keys", "-t", "test-session", "-l", "First  Second  Third"]


@patch('subprocess.run')
def test_accept_returns_false_for_empty_text(mock_run):
    """Test accept returns None for empty text."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    result = processor.accept("")
    
    assert result is None
    mock_run.assert_not_called()


@patch('subprocess.run')
def test_accept_returns_false_for_none(mock_run):
    """Test accept returns None for None input."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    result = processor.accept(None)
    
    assert result is None
    mock_run.assert_not_called()


@patch('subprocess.run')
def test_accept_handles_subprocess_error(mock_run):
    """Test accept handles and logs subprocess errors."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')
    
    processor.accept("test")
    
    logger.error.assert_called()
    assert "Failed to send to tmux" in logger.error.call_args[0][0]


@patch('subprocess.run')
def test_accept_logs_session_name(mock_run):
    """Test accept logs the session name it's sending to."""
    get_session = Mock(return_value='my-special-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.accept("test message")
    
    logger.info.assert_called_with("Sending to tmux session 'my-special-session'")


@patch('subprocess.run')
def test_accept_uses_literal_flag(mock_run):
    """Test accept uses -l flag for literal text interpretation."""
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.accept("some $special chars")
    
    # Verify -l flag is used
    calls = mock_run.call_args_list
    assert "-l" in calls[0][0][0]


@patch('subprocess.run')
@patch('src.processors.tmux_processor.get_os_type')
def test_toggle_vocalization_on_macos_with_true(mock_get_os_type, mock_run):
    """Test toggle_vocalization sends start prompt on macOS when is_on=True."""
    from src.utils.os_detection import OSType
    mock_get_os_type.return_value = OSType.MACOS
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.toggle_vocalization(True)
    
    # Should send start prompt
    assert mock_run.call_count == 2
    first_call = mock_run.call_args_list[0][0][0]
    assert 'after each response' in ' '.join(first_call).lower()


@patch('subprocess.run')
@patch('src.processors.tmux_processor.get_os_type')
def test_toggle_vocalization_on_macos_with_false(mock_get_os_type, mock_run):
    """Test toggle_vocalization sends stop prompt on macOS when is_on=False."""
    from src.utils.os_detection import OSType
    mock_get_os_type.return_value = OSType.MACOS
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.toggle_vocalization(False)
    
    # Should send stop prompt
    assert mock_run.call_count == 2
    first_call = mock_run.call_args_list[0][0][0]
    assert 'Stop vocalizing' in ' '.join(first_call)


@patch('subprocess.run')
@patch('src.processors.tmux_processor.get_os_type')
def test_toggle_vocalization_noop_on_linux(mock_get_os_type, mock_run):
    """Test toggle_vocalization is noop on Linux."""
    from src.utils.os_detection import OSType
    mock_get_os_type.return_value = OSType.LINUX
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    processor.toggle_vocalization(True)
    
    # Should not call subprocess on non-macOS
    mock_run.assert_not_called()


@patch('subprocess.run')
@patch('src.processors.tmux_processor.get_os_type')
def test_toggle_vocalization_handles_error(mock_get_os_type, mock_run):
    """Test toggle_vocalization handles subprocess errors."""
    from src.utils.os_detection import OSType
    mock_get_os_type.return_value = OSType.MACOS
    get_session = Mock(return_value='test-session')
    logger = Mock()
    processor = TmuxProcessor(get_session, logger)
    
    mock_run.side_effect = subprocess.CalledProcessError(1, 'tmux')
    
    processor.toggle_vocalization(True)
    
    logger.error.assert_called()
    assert 'Failed to set response vocalization' in logger.error.call_args[0][0]
