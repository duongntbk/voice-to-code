"""tmux-specific feedback utilities for voice-to-code."""

import subprocess


def update_status(status, session_name):
    """Update tmux status bar with current state."""
    try:
        subprocess.run([
            "tmux", "set-option", "-t", session_name,
            "status-right", f"[{status}]"
        ], capture_output=True)
    except Exception:
        pass  # Silently fail if tmux status update doesn't work
