"""Tests for config_writer module."""

import importlib.util

from src.utils.config_writer import _format_value, write_config_to_file


def test_write_config_to_file_creates_file(tmp_path):
    """Test writing config dict creates a file."""
    config_file = tmp_path / "test_config.py"
    config = {
        'model': 'large',
        'pause_threshold': 2.0,
        'session_name': 'test-session',
        'debug': True
    }
    
    write_config_to_file(config, config_file)
    
    assert config_file.exists()


def test_write_config_contains_expected_keys(tmp_path):
    """Test written config contains all keys and values."""
    config_file = tmp_path / "test_config.py"
    config = {
        'model': 'large',
        'pause_threshold': 2.5,
        'energy_threshold': 150,
        'dynamic_energy': False,
        'session_name': 'my-session',
        'debug': True
    }
    
    write_config_to_file(config, config_file)
    
    content = config_file.read_text()
    assert "CONFIG = {" in content
    assert "'model': 'large'" in content
    assert "'pause_threshold': 2.5" in content
    assert "'energy_threshold': 150" in content
    assert "'dynamic_energy': False" in content
    assert "'session_name': 'my-session'" in content
    assert "'debug': True" in content


def test_config_file_is_valid_python(tmp_path):
    """Test generated config.py is valid Python that can be imported."""
    config_file = tmp_path / "config.py"
    config = {
        'model': 'tiny',
        'pause_threshold': 1.5,
        'debug': False
    }
    
    write_config_to_file(config, config_file)
    
    # Import and verify
    spec = importlib.util.spec_from_file_location("test_config", config_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    assert module.CONFIG['model'] == 'tiny'
    assert module.CONFIG['pause_threshold'] == 1.5
    assert module.CONFIG['debug'] is False


def test_format_string_value():
    """Test _format_value handles strings correctly."""
    assert _format_value('hello') == "'hello'"
    assert _format_value('ai-voice-input') == "'ai-voice-input'"


def test_format_boolean_value():
    """Test _format_value handles booleans correctly."""
    assert _format_value(True) == 'True'
    assert _format_value(False) == 'False'


def test_format_number_value():
    """Test _format_value handles numbers correctly."""
    assert _format_value(100) == '100'
    assert _format_value(2.5) == '2.5'


def test_format_path_value():
    """Test _format_value detects and formats paths."""
    assert _format_value('/tmp/logs') == 'Path("/tmp/logs")'
    assert _format_value('~/Documents') == 'Path("~/Documents")'


def test_write_includes_comments(tmp_path):
    """Test written config includes comments for known keys."""
    config_file = tmp_path / "config.py"
    config = {'model': 'base', 'processor_type': 'tmux'}
    
    write_config_to_file(config, config_file)
    
    content = config_file.read_text()
    # Should have comment for model
    assert "# Whisper model" in content
    # Should have comment for processor type
    assert "# Processor type" in content


def test_overwrites_existing_file(tmp_path):
    """Test writing to existing file overwrites it."""
    config_file = tmp_path / "config.py"
    config_file.write_text("OLD CONTENT")
    
    config = {'model': 'tiny'}
    write_config_to_file(config, config_file)
    
    content = config_file.read_text()
    assert "OLD CONTENT" not in content
    assert "CONFIG = {" in content
