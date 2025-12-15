#!/usr/bin/env python3
"""Voice to Code - GUI mode entry point."""

import os
import tkinter as tk
from tkinter import messagebox

from src.gui.models.main_view_model import MainViewModel
from src.gui.views.main_form import MainForm
from src.utils.config_manager import ConfigManager
from src.utils.os_detection import get_os_type, OSType
from src.utils.deps_detection import check_dependencies


def main():
    """Main entry point for GUI mode."""
    # Add Homebrew paths for bundled .app (safe for source mode too)
    os.environ['PATH'] = '/opt/homebrew/bin:/usr/local/bin:' + os.environ.get('PATH', '')
    
    # Check for required dependencies before starting the GUI
    missing_deps_msg = check_dependencies()
    if missing_deps_msg:
        # Create a minimal root window for the error dialog
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Missing Dependencies", missing_deps_msg)
        root.destroy()
        return

    # Initialize config manager
    ConfigManager.initialize()
    
    root = tk.Tk()
    vm = MainViewModel()
    _app = MainForm(root, vm)  # Keep reference to prevent garbage collection
    root.mainloop()


if __name__ == "__main__":
    if get_os_type() == OSType.MACOS:
        # Fix for PyInstaller on macOS: prevent multiple GUI windows during transcription.
        # Whisper/torch uses multiprocessing internally. Default 'spawn' method re-imports
        # the frozen executable, re-executing main.py and creating duplicate windows.
        # 'fork' clones the process instead, avoiding re-import.
        # See: https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html
        import multiprocessing
        multiprocessing.set_start_method('fork', force=True)

    main()
