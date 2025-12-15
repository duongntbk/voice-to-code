"""Tests for OS detection utility."""

import pytest
from unittest.mock import patch

from src.utils.os_detection import OSType, get_os_type


@pytest.mark.parametrize("platform_system,expected_os", [
    ('Darwin', OSType.MACOS),
    ('Linux', OSType.LINUX),
    ('Windows', OSType.UNKNOWN),
    ('FreeBSD', OSType.UNKNOWN),
    ('', OSType.UNKNOWN),
])
@patch('platform.system')
def test_get_os_type(mock_system, platform_system, expected_os):
    """Test get_os_type returns correct OSType for each platform."""
    mock_system.return_value = platform_system
    
    result = get_os_type()
    
    assert result == expected_os
    mock_system.assert_called_once()
