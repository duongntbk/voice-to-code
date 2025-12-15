"""Tests for file log handler."""

from src.logging.file_log_handler import create_file_handler


def test_file_handler_writes_to_file(tmp_path):
    """File handler should write log messages to file."""
    log_file = tmp_path / "test.log"
    handler = create_file_handler(log_file, debug_mode=True)
    
    handler('INFO', 'test message')
    
    content = log_file.read_text()
    assert 'test message' in content
    assert log_file.exists()


def test_file_handler_appends_not_overwrites(tmp_path):
    """File handler should append to existing file, not overwrite."""
    log_file = tmp_path / "test.log"
    handler = create_file_handler(log_file, debug_mode=True)
    
    handler('INFO', 'first message')
    handler('INFO', 'second message')
    
    content = log_file.read_text()
    assert 'first message' in content
    assert 'second message' in content


def test_file_handler_filters_debug_when_disabled(tmp_path):
    """File handler should not log DEBUG messages when debug_mode=False."""
    log_file = tmp_path / "test.log"
    handler = create_file_handler(log_file, debug_mode=False)
    
    handler('DEBUG', 'should not appear')
    handler('INFO', 'should appear')
    handler('ERROR', 'error message')
    
    content = log_file.read_text()
    assert 'should not appear' not in content
    assert 'INFO: should appear' in content
    assert 'ERROR: error message' in content


def test_file_handler_logs_debug_when_enabled(tmp_path):
    """File handler should log DEBUG messages when debug_mode=True."""
    log_file = tmp_path / "test.log"
    handler = create_file_handler(log_file, debug_mode=True)
    
    handler('DEBUG', 'debug message')
    handler('INFO', 'info message')
    handler('WARNING', 'warning message')
    
    content = log_file.read_text()
    assert 'DEBUG: debug message' in content
    assert 'INFO: info message' in content
    assert 'WARNING: warning message' in content


def test_file_handler_includes_timestamp(tmp_path):
    """File handler should include timestamp in log entries."""
    log_file = tmp_path / "test.log"
    handler = create_file_handler(log_file, debug_mode=True)
    
    handler('INFO', 'test')
    
    content = log_file.read_text()
    # Check for timestamp pattern [YYYY-MM-DD HH:MM:SS]
    assert content.startswith('[')
    assert ']' in content
