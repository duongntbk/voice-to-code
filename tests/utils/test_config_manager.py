"""Tests for ConfigManager."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.config_manager import ConfigManager


@pytest.fixture(autouse=True)
def reset_config_manager():
    """Reset ConfigManager state before each test."""
    ConfigManager.reset()
    yield


@pytest.fixture
def test_config_file(tmp_path):
    """Create a test config.py file."""
    config_file = tmp_path / "config.py"
    config_file.write_text("CONFIG = {'model': 'tiny', 'debug': True, 'session_name': 'test-session'}")
    return config_file


@patch('src.utils.config_manager.ConfigManager.load')
def test_initialize_sets_config_file_path_from_source(mock_load):
    """Test initialize finds repo config.py when running from source."""
    ConfigManager.initialize()
    
    # Should point to repo config.py
    assert ConfigManager._config_file_path.name == 'config.py'
    mock_load.assert_called_once()


@patch('src.utils.config_manager.shutil.copy')
@patch('src.utils.config_manager.Path')
@patch('sys.frozen', True, create=True)
@patch('sys._MEIPASS', '/tmp/bundle', create=True)
def test_initialize_copies_bundled_config_on_first_run(mock_path, mock_copy):
    """Test initialize copies bundled config to user location on first run."""
    
    # Mock Path.home() and user_config.exists()
    mock_path.home.return_value = Path('/tmp/test_home')
    
    # Mock that user config doesn't exist
    with patch.object(Path, 'exists', return_value=False):
        with patch.object(Path, 'mkdir'):
            with patch('src.utils.config_manager.ConfigManager.load'):
                ConfigManager.initialize()
                
                # Should have called copy
                mock_copy.assert_called_once()
                # Should point to user config
                assert str(ConfigManager._config_file_path).endswith('.voice-to-code/config.py')


def test_load_reads_config_from_file(test_config_file):
    """Test load reads CONFIG from file."""
    ConfigManager._config_file_path = test_config_file
    config = ConfigManager.load()
    
    assert config['model'] == 'tiny'
    assert config['debug'] is True
    assert config['session_name'] == 'test-session'


def test_load_without_initialize_raises_error():
    """Test load raises error if not initialized."""
    with pytest.raises(RuntimeError, match="ConfigManager not initialized"):
        ConfigManager.load()


@patch('pathlib.Path.exists')
def test_load_missing_file_raises_error(mock_exists):
    """Test load raises error if config file doesn't exist."""
    mock_exists.return_value = False
    
    with pytest.raises(FileNotFoundError):
        ConfigManager.initialize()


def test_get_returns_copy_of_config():
    """Test get returns a copy (mutations don't affect internal state)."""
    ConfigManager.initialize()
    config1 = ConfigManager.get()
    original_model = config1['model']
    config1['model'] = 'modified'
    
    config2 = ConfigManager.get()
    
    # Original unchanged
    assert config2['model'] == original_model


@patch('src.utils.config_writer.write_config_to_file')
def test_save_writes_to_file_and_updates_memory(mock_write):
    """Test save writes to file and updates in-memory config."""
    ConfigManager.initialize()
    
    new_config = {'new': 'value'}
    ConfigManager.save(new_config)
    
    # Verify write_config_to_file called
    mock_write.assert_called_once()
    
    # Verify in-memory updated
    assert ConfigManager.get()['new'] == 'value'


def test_save_without_initialize_raises_error():
    """Test save raises error if not initialized."""
    with pytest.raises(RuntimeError, match="ConfigManager not initialized"):
        ConfigManager.save({'test': 'value'})


def test_get_value_returns_specific_key():
    """Test get_value retrieves specific config value."""
    ConfigManager.initialize()

    assert ConfigManager.get_value('model') is not None


def test_get_value_returns_default_for_missing_key():
    """Test get_value returns default if key doesn't exist."""
    ConfigManager.initialize()
    
    assert ConfigManager.get_value('nonexistent_key', 'default') == 'default'
    assert ConfigManager.get_value('nonexistent_key') is None


@patch('src.utils.config_writer.write_config_to_file')
def test_update_merges_and_saves(mock_write):
    """Test update merges new values with existing config."""
    ConfigManager.initialize()
    original_model = ConfigManager.get()['model']
    
    ConfigManager.update({'debug': True, 'new_key': 'new_value'})
    
    # Verify merged config saved
    saved_config = mock_write.call_args[0][0]
    assert saved_config['model'] == original_model  # Original kept
    assert saved_config['debug'] is True            # Updated
    assert saved_config['new_key'] == 'new_value'   # Added


def test_reset_clears_state():
    """Test reset clears config manager state."""
    ConfigManager._config = {'test': 'value'}
    ConfigManager._config_file_path = Path('/test')
    
    ConfigManager.reset()
    
    assert ConfigManager._config is None
    assert ConfigManager._config_file_path is None


@patch('src.utils.config_writer.write_config_to_file')
def test_save_creates_copy(mock_write):
    """Test save stores a copy (external mutations don't affect manager)."""
    ConfigManager.initialize()
    
    new_config = {'model': 'base'}
    ConfigManager.save(new_config)
    
    # Mutate the dict we passed in
    new_config['model'] = 'mutated'
    
    # Manager should have copy, not reference
    assert ConfigManager.get()['model'] == 'base'
