#!/usr/bin/env python3
"""Dependency detection utilities for checking required binaries."""

import shutil
from typing import List, Dict, Optional

from .os_detection import get_os_type, OSType


# TODO: show appropriate install command per Linux distro
#       (currently defaulting to apt-get for Debian/Ubuntu)
class DependencyChecker:
    """Checks for required system dependencies."""

    REQUIRED_DEPS = ['tmux', 'ffmpeg']

    INSTALL_COMMANDS = {
        OSType.LINUX: 'sudo apt-get install',
        OSType.MACOS: 'brew install',
        OSType.UNKNOWN: 'sudo apt-get install'
    }

    def __init__(self):
        """Initialize dependency checker."""
        pass

    def is_binary_available(self, binary_name: str) -> bool:
        """Check if a binary is available in PATH."""
        return shutil.which(binary_name) is not None

    def check_all_dependencies(self) -> Dict[str, bool]:
        """Check all required dependencies and return their status."""
        results = {}
        for dep_name in self.REQUIRED_DEPS:
            results[dep_name] = self.is_binary_available(dep_name)
        return results

    def get_missing_dependencies(self) -> List[str]:
        """Get list of missing dependency names."""
        check_results = self.check_all_dependencies()
        return [dep for dep, available in check_results.items() if not available]

    def get_install_commands(self, missing_deps: List[str]) -> List[str]:
        """Get install commands for missing dependencies."""
        if not missing_deps:
            return []

        os_type = get_os_type()
        base_command = self.INSTALL_COMMANDS.get(os_type)
        if not base_command:
            return []

        # Filter to only include valid dependencies
        valid_deps = [dep for dep in missing_deps if dep in self.REQUIRED_DEPS]
        if not valid_deps:
            return []

        # Combine all packages into a single command
        return [f"{base_command} {' '.join(valid_deps)}"]

    def format_missing_message(self) -> Optional[str]:
        """Format a user-friendly message about missing dependencies."""
        missing = self.get_missing_dependencies()
        if not missing:
            return None

        install_commands = self.get_install_commands(missing)

        message = f"Missing required libraries: {', '.join(missing)}.\n"
        if install_commands:
            message += "Please install them with:\n"
            for cmd in install_commands:
                message += f"  {cmd}\n"

        return message.strip()


def check_dependencies() -> Optional[str]:
    """Convenience function to check all dependencies and return error message if any missing."""
    checker = DependencyChecker()
    return checker.format_missing_message()
