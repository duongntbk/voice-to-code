"""ViewModel for main window."""

import tkinter as tk


class MainViewModel:
    """ViewModel holding state for the main window."""
    
    def __init__(self) -> None:
        self.is_running = tk.BooleanVar(value=False)
        self.status_text = tk.StringVar(value="Stopped")
        self.status_color = tk.StringVar(value="red")
