"""Tests for GUI log handler."""

from src.logging.gui_log_handler import create_gui_handler


class MockWidget:
    """Mock tkinter widget for testing."""
    
    def __init__(self):
        self.text = []
        self.seen_positions = []
    
    def insert(self, pos, text):
        self.text.append(text)
    
    def see(self, pos):
        self.seen_positions.append(pos)


def test_gui_handler_inserts_text():
    """GUI handler should insert text into widget."""
    widget = MockWidget()
    handler = create_gui_handler(widget, debug_mode=True)
    
    handler('INFO', 'test message')
    
    assert len(widget.text) == 1
    assert 'test message' in widget.text[0]


def test_gui_handler_auto_scrolls():
    """GUI handler should call see() to auto-scroll."""
    widget = MockWidget()
    handler = create_gui_handler(widget, debug_mode=True)
    
    handler('INFO', 'test')
    
    assert len(widget.seen_positions) == 1


def test_gui_handler_filters_debug_when_disabled():
    """GUI handler should not log DEBUG messages when debug_mode=False."""
    widget = MockWidget()
    handler = create_gui_handler(widget, debug_mode=False)
    
    handler('DEBUG', 'should not appear')
    handler('INFO', 'should appear')
    handler('ERROR', 'error message')
    
    assert len(widget.text) == 2
    assert 'INFO: should appear' in widget.text[0]
    assert 'ERROR: error message' in widget.text[1]
    assert 'should not appear' not in ''.join(widget.text)


def test_gui_handler_logs_debug_when_enabled():
    """GUI handler should log DEBUG messages when debug_mode=True."""
    widget = MockWidget()
    handler = create_gui_handler(widget, debug_mode=True)
    
    handler('DEBUG', 'debug message')
    handler('INFO', 'info message')
    handler('WARNING', 'warning message')
    
    assert len(widget.text) == 3
    assert 'DEBUG: debug message' in widget.text[0]
    assert 'INFO: info message' in widget.text[1]
    assert 'WARNING: warning message' in widget.text[2]


def test_gui_handler_includes_timestamp():
    """GUI handler should include timestamp in log entries."""
    widget = MockWidget()
    handler = create_gui_handler(widget, debug_mode=True)
    
    handler('INFO', 'test')
    
    # Check for timestamp pattern [HH:MM:SS]
    assert widget.text[0].startswith('[')
    assert ']' in widget.text[0]
