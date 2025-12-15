"""Cross-platform feedback utilities for voice-to-code: notifications and speech."""

import shutil
import subprocess

from src.utils.os_detection import get_os_type, OSType


def notify(title, message):
    try:
        os_type = get_os_type()
        if os_type == OSType.MACOS:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], check=True, capture_output=True)
        elif os_type == OSType.LINUX:
            if not shutil.which("notify-send"):
                return
            subprocess.run([
                "notify-send", title, message
            ], check=True, capture_output=True)
    except Exception as e:
        import sys
        print(f"WARNING: notify failed: {e}", file=sys.stderr)


def speak(message):
    try:
        os_type = get_os_type()
        if os_type == OSType.MACOS:
            subprocess.Popen([
                "say", "-v", "Princess", message
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif os_type == OSType.LINUX:
            if not shutil.which("espeak-ng"):
                return
            subprocess.Popen([
                "espeak-ng", message
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        import sys
        print(f"WARNING: speak failed: {e}", file=sys.stderr)
