"""Tests for factory functions."""

import sys
from unittest.mock import Mock, patch

import pytest

# Mock whisper_mic before importing our code (CI server doesn't have it)
sys.modules['whisper_mic'] = Mock()

from src.factories import create_processor, create_transcriber  # noqa: E402


@patch('src.factories.TmuxProcessor')
def test_create_processor_tmux(mock_tmux):
    """Test creating tmux processor."""
    config = {'processor_type': 'tmux'}
    get_session = Mock()
    logger = Mock()
    
    processor = create_processor(config, get_session, logger)
    
    mock_tmux.assert_called_once_with(get_session, logger)
    assert processor == mock_tmux.return_value


@patch('src.factories.TmuxProcessor')
def test_create_processor_default_type(mock_tmux):
    """Test default processor type when not in config."""
    config = {}
    get_session = Mock()
    logger = Mock()
    
    _processor = create_processor(config, get_session, logger)
    
    mock_tmux.assert_called_once_with(get_session, logger)


def test_create_processor_unknown_type():
    """Test unknown processor type raises ValueError."""
    config = {'processor_type': 'unknown'}
    get_session = Mock()
    logger = Mock()
    
    with pytest.raises(ValueError, match="Unknown processor"):
        create_processor(config, get_session, logger)


@patch('src.factories.WhisperMicTranscriber')
def test_create_transcriber_whisper_mic(mock_whisper):
    """Test creating whisper_mic transcriber."""
    config = {'transcriber_type': 'whisper_mic'}
    logger = Mock()
    processor = Mock()
    
    transcriber = create_transcriber(config, logger, processor)
    
    mock_whisper.assert_called_once_with(config, logger, processor)
    assert transcriber == mock_whisper.return_value


@patch('src.factories.WhisperMicTranscriber')
def test_create_transcriber_default_type(mock_whisper):
    """Test default transcriber type when not in config."""
    config = {}
    logger = Mock()
    processor = Mock()
    
    _transcriber = create_transcriber(config, logger, processor)
    
    mock_whisper.assert_called_once_with(config, logger, processor)


def test_create_transcriber_unknown_type():
    """Test unknown transcriber type raises ValueError."""
    config = {'transcriber_type': 'unknown'}
    logger = Mock()
    processor = Mock()
    
    with pytest.raises(ValueError, match="Unknown transcriber"):
        create_transcriber(config, logger, processor)
