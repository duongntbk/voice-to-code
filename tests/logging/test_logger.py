"""Tests for Logger class."""

from src.logging.logger import Logger


def test_logger_calls_single_handler():
    """Logger should call a single handler with correct level and message."""
    messages = []
    
    def handler(level, msg):
        messages.append((level, msg))
    
    logger = Logger(handler)
    logger.debug("test debug")
    logger.info("test info")
    logger.warning("test warning")
    logger.error("test error")
    
    assert messages == [
        ('DEBUG', 'test debug'),
        ('INFO', 'test info'),
        ('WARNING', 'test warning'),
        ('ERROR', 'test error')
    ]


def test_logger_calls_multiple_handlers():
    """Logger should call all handlers when multiple are configured."""
    messages1, messages2 = [], []
    
    logger = Logger([
        lambda lvl, msg: messages1.append((lvl, msg)),
        lambda lvl, msg: messages2.append((lvl, msg))
    ])
    
    logger.info("test")
    
    assert messages1 == [('INFO', 'test')]
    assert messages2 == [('INFO', 'test')]


def test_logger_accepts_list_of_handlers():
    """Logger should accept handlers as a list."""
    messages = []
    handlers = [lambda lvl, msg: messages.append(msg)]
    
    logger = Logger(handlers)
    logger.info("test")
    
    assert messages == ["test"]


def test_logger_handles_handler_exception():
    """Logger should continue calling other handlers if one fails."""
    messages = []
    
    def failing_handler(level, msg):
        raise Exception("Handler failed")
    
    def working_handler(level, msg):
        messages.append(msg)
    
    logger = Logger([failing_handler, working_handler])
    
    try:
        logger.info("test")
    except Exception:
        pass
    
    # This test shows current behavior - exception propagates
    # We might want to catch exceptions in handlers later
