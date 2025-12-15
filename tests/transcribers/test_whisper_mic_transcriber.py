"""Tests for WhisperMicTranscriber class."""

import sys
from unittest.mock import Mock, patch

# Mock whisper_mic before importing our code (CI server doesn't have it)
sys.modules['whisper_mic'] = Mock()

# We need to mock whisper_mic BEFORE importing our code,
# so we can't move the import to the top.
# We need to add a # noqa: E402 comment to suppress this specific linting error.
from src.transcribers.whisper_mic_transcriber import (  # noqa: E402
    WhisperMicTranscriber,
)


def test_initialization_reads_config():
    """Test that transcriber reads config values on initialization."""
    config = {'listen_timeout': 3.0, 'model': 'base'}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    
    assert transcriber.listen_timeout == 3.0
    assert transcriber.config == config
    assert transcriber.logger == logger
    assert transcriber.processor == processor
    assert transcriber.mic is None


def test_initialization_uses_default_timeout():
    """Test that transcriber uses default timeout if not in config."""
    config = {'model': 'base'}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    
    assert transcriber.listen_timeout == 2.0


@patch('src.transcribers.whisper_mic_transcriber.WhisperMic')
def test_initialize_creates_whisper_mic(MockWhisperMic):
    """Test that initialize calls WhisperMic with correct config."""
    config = {
        'model': 'tiny',
        'pause_threshold': 2.5,
        'energy_threshold': 150,
        'dynamic_energy': False,
        'debug': True
    }
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    result = transcriber.initialize()
    
    # Verify WhisperMic was called with correct params
    MockWhisperMic.assert_called_once_with(
        model='tiny',
        english=True,
        pause=2.5,
        energy=150,
        dynamic_energy=False,
        verbose=True,
        no_keyboard=True
    )
    assert result is True
    assert transcriber.mic is not None


@patch('src.transcribers.whisper_mic_transcriber.WhisperMic')
def test_initialize_with_default_values(MockWhisperMic):
    """Test initialize uses default values for missing config keys."""
    config = {'model': 'base'}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    transcriber.initialize()
    
    MockWhisperMic.assert_called_once_with(
        model='base',
        english=True,
        pause=2.0,
        energy=100,
        dynamic_energy=True,
        verbose=False,
        no_keyboard=True
    )


@patch('src.transcribers.whisper_mic_transcriber.WhisperMic')
def test_initialize_handles_exception(MockWhisperMic):
    """Test that initialize returns False and logs error on exception."""
    config = {'model': 'tiny'}
    logger = Mock()
    processor = Mock()
    
    MockWhisperMic.side_effect = Exception("Model not found")
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    result = transcriber.initialize()
    
    assert result is False
    logger.error.assert_called()
    assert "Failed to initialize" in logger.error.call_args[0][0]


def test_do_streaming_fails_without_initialization():
    """Test do_streaming returns False if mic not initialized."""
    config = {}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    result = transcriber.do_streaming(lambda: True)
    
    assert result is False
    logger.error.assert_called()


def test_do_streaming_processes_transcriptions():
    """Test do_streaming calls processor.accept for each transcription."""
    config = {'listen_timeout': 1.0}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    transcriber.mic = Mock()
    
    # Simulate 3 transcriptions then stop
    call_count = [0]
    def should_continue():
        call_count[0] += 1
        return call_count[0] <= 3
    
    transcriptions = ["First text", "Second text", "Third text"]
    transcriber.mic.listen.side_effect = transcriptions
    
    transcriber.do_streaming(should_continue)
    
    # Verify processor.accept was called for each transcription
    assert processor.accept.call_count == 3
    processor.accept.assert_any_call("First text")
    processor.accept.assert_any_call("Second text")
    processor.accept.assert_any_call("Third text")


def test_do_streaming_skips_none_results():
    """Test do_streaming doesn't call processor for None results."""
    config = {'listen_timeout': 1.0}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    transcriber.mic = Mock()
    
    call_count = [0]
    def should_continue():
        call_count[0] += 1
        return call_count[0] <= 3
    
    # Mix of successful and None results
    transcriber.mic.listen.side_effect = ["Hello", None, "World"]
    
    transcriber.do_streaming(should_continue)
    
    # Only 2 calls to processor (None is skipped)
    assert processor.accept.call_count == 2
    processor.accept.assert_any_call("Hello")
    processor.accept.assert_any_call("World")


def test_do_streaming_stops_on_should_continue_false():
    """Test do_streaming stops when should_continue returns False."""
    config = {'listen_timeout': 1.0}
    logger = Mock()
    processor = Mock()
    
    transcriber = WhisperMicTranscriber(config, logger, processor)
    transcriber.mic = Mock()
    transcriber.mic.listen.return_value = "Some text"
    
    call_count = [0]
    def should_continue():
        call_count[0] += 1
        return call_count[0] <= 2
    
    result = transcriber.do_streaming(should_continue)
    
    assert result is True
    assert processor.accept.call_count == 2
