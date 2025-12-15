"""Settings dialog form."""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from src.gui.models.settings_view_model import SettingsViewModel
from src.utils.config_manager import ConfigManager


class SettingsForm:
    """Settings/Preferences dialog."""
    
    def __init__(self, parent: tk.Tk | tk.Toplevel, vm: SettingsViewModel, on_save_callback: Callable[[dict[str, Any]], None] | None = None) -> None:
        """
        Create and show settings dialog.
        
        Args:
            parent: Parent window
            vm: SettingsViewModel instance
            on_save_callback: Optional callback(config_dict) when Save is clicked
        """
        self.vm = vm
        self.on_save = on_save_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")
        self.window.geometry("480x540")
        self.window.configure(bg="#f0f0f0")
        self.window.resizable(False, False)
        
        # Center and make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Main container with minimal padding
        container = tk.Frame(self.window, bg="#f0f0f0", padx=15, pady=15)
        container.pack(fill="both", expand=True)
        
        # Component Selection Section
        self._create_section_header(container, "Component Selection")
        
        # Transcriber and Processor on same row
        row = tk.Frame(container, bg="#f0f0f0")
        row.pack(fill="x", pady=(3, 5))
        
        tk.Label(row, text="Transcriber:", font=("Arial", 9), bg="#f0f0f0").pack(side="left")
        ttk.Combobox(row, textvariable=self.vm.transcriber_type,
                    values=self.vm.transcriber_options, state="readonly", width=12).pack(side="left", padx=(5, 20))
        
        tk.Label(row, text="Processor:", font=("Arial", 9), bg="#f0f0f0").pack(side="left")
        ttk.Combobox(row, textvariable=self.vm.processor_type,
                    values=self.vm.processor_options, state="readonly", width=12).pack(side="left", padx=(5, 0))
        
        # Audio Settings Section
        self._create_section_header(container, "Audio Settings")
        
        # Whisper Model
        self._create_labeled_widget(
            container,
            "Whisper Model:",
            ttk.Combobox(container, textvariable=self.vm.model, 
                        values=self.vm.model_options, state="readonly", width=15)
        )
        
        # Pause Threshold
        self._create_slider(
            container,
            "Pause Threshold (seconds):",
            self.vm.pause_threshold,
            from_=0.5, to=5.0, resolution=0.1
        )
        
        # Listen Timeout
        self._create_slider(
            container,
            "Listen Timeout (seconds):",
            self.vm.listen_timeout,
            from_=0.5, to=5.0, resolution=0.1
        )
        
        # Energy Threshold
        self._create_slider(
            container,
            "Energy Threshold:",
            self.vm.energy_threshold,
            from_=50, to=500, resolution=10
        )
        
        # Dynamic Energy
        self._create_checkbox(
            container,
            "Dynamic Energy (auto-adjust for ambient noise)",
            self.vm.dynamic_energy
        )
        
        # General Settings Section
        self._create_section_header(container, "General Settings")
        
        # Vocalize Response
        self._create_checkbox(
            container,
            "Vocalize Response",
            self.vm.vocalize_response
        )
        
        # Log handler and Debug mode on same row
        log_row = tk.Frame(container, bg="#f0f0f0")
        log_row.pack(fill="x", pady=(3, 5))
        
        tk.Label(log_row, text="Log Output:", font=("Arial", 9), bg="#f0f0f0").pack(side="left")
        ttk.Combobox(log_row, textvariable=self.vm.log_handler_type,
                    values=self.vm.log_handler_options, state="readonly", width=8).pack(side="left", padx=(5, 20))
        
        tk.Checkbutton(log_row, text="Debug Mode", variable=self.vm.debug,
                      font=("Arial", 9), bg="#f0f0f0", activebackground="#f0f0f0").pack(side="left")
        
        # Buttons at bottom
        button_frame = tk.Frame(container, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=(12, 0))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            font=("Arial", 12),
            width=10,
            bg="#e0e0e0",
            relief="raised",
            bd=2
        )
        cancel_btn.pack(side="right", padx=(5, 0))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self._save,
            font=("Arial", 12),
            width=10,
            bg="#e0e0e0",
            relief="raised",
            bd=2
        )
        save_btn.pack(side="right")
    
    def _create_section_header(self, parent: tk.Frame, text: str) -> None:
        """Create a section header label."""
        header = tk.Label(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#333333",
            anchor="w"
        )
        header.pack(fill="x", pady=(8, 3))
        
        # Separator line
        sep = tk.Frame(parent, height=1, bg="#cccccc")
        sep.pack(fill="x", pady=(0, 5))
    
    def _create_labeled_frame(self, parent: tk.Frame, label_text: str) -> tk.Frame:
        """Create a frame with a label above it."""
        label = tk.Label(
            parent,
            text=label_text,
            font=("Arial", 9),
            bg="#f0f0f0",
            anchor="w"
        )
        label.pack(fill="x", pady=(3, 1))
        
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill="x", pady=(0, 5))
        return frame
    
    def _create_labeled_widget(self, parent: tk.Frame, label_text: str, widget: Any) -> None:
        """Create a label and widget pair."""
        _frame = self._create_labeled_frame(parent, label_text)
        widget.pack(anchor="w")
    
    def _create_slider(self, parent: tk.Frame, label_text: str, variable: tk.DoubleVar | tk.IntVar, from_: float, to: float, resolution: float) -> None:
        """Create a slider with label and value display."""
        frame = self._create_labeled_frame(parent, label_text)
        
        # Slider and value label on same row
        slider = tk.Scale(
            frame,
            from_=from_,
            to=to,
            resolution=resolution,
            variable=variable,
            orient="horizontal",
            length=220,
            bg="#f0f0f0",
            showvalue=0
        )
        slider.pack(side="left", padx=(0, 8))
        
        value_label = tk.Label(
            frame,
            textvariable=variable,
            font=("Arial", 9),
            bg="#f0f0f0",
            width=6,
            anchor="w"
        )
        value_label.pack(side="left")
    
    def _create_checkbox(self, parent: tk.Frame, label_text: str, variable: tk.BooleanVar) -> None:
        """Create a checkbox."""
        checkbox = tk.Checkbutton(
            parent,
            text=label_text,
            variable=variable,
            font=("Arial", 9),
            bg="#f0f0f0",
            activebackground="#f0f0f0"
        )
        checkbox.pack(anchor="w", pady=(3, 5))
    
    def _create_text_field(self, parent: tk.Frame, label_text: str, variable: tk.StringVar) -> None:
        """Create a text entry field."""
        frame = self._create_labeled_frame(parent, label_text)
        entry = tk.Entry(frame, textvariable=variable, width=40)
        entry.pack(anchor="w")
    
    def _save(self) -> None:
        """Save button handler."""
        config = self.vm.get_config_dict()
        
        # Save via ConfigManager (writes to file and updates in-memory)
        ConfigManager.save(config)
        
        # Call callback if provided
        if self.on_save:
            self.on_save(config)
        
        # Close dialog
        self.window.destroy()
