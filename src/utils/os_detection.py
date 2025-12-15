"""Operating system detection utilities."""

import platform
from enum import Enum


class OSType(Enum):
    """Enumeration of supported operating systems."""
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


def get_os_type() -> OSType:
    """Detect the current operating system.
    
    Returns:
        OSType enum value representing the current OS
    """
    system = platform.system()
    if system == "Darwin":
        return OSType.MACOS
    elif system == "Linux":
        return OSType.LINUX
    else:
        return OSType.UNKNOWN
