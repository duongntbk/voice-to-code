"""Main window form."""

import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Any

from src.constants import DEFAULT_LOG_FILE, DEFAULT_OUTPUT_DIR, DEFAULT_AI_AGENT_SESSION
from src.factories import create_log_handler, create_processor, create_transcriber
from src.gui.models.main_view_model import MainViewModel
from src.gui.models.settings_view_model import SettingsViewModel
from src.gui.views.input_dialog_form import InputDialogForm
from src.gui.views.help_form import HelpForm
from src.gui.views.settings_form import SettingsForm
from src.logging.logger import Logger
from src.utils.config_manager import ConfigManager
from src.utils.feedback import speak


class MainForm:
    """Main application window."""
    
    def __init__(self, root: tk.Tk, vm: MainViewModel) -> None:
        """
        Initialize main window.
        
        Args:
            root: Tk root window
            vm: MainViewModel instance
        """
        self.root = root
        self.vm = vm
        
        # Window setup
        root.title("Voice to Code")
        root.configure(bg="#f0f0f0")
        
        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences...", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_help)
        
        # Main content frame
        main_frame = tk.Frame(root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status bar (bound to ViewModel)
        self.status = tk.Label(main_frame, textvariable=self.vm.status_text, 
                              bg="red", fg="white",
                              font=("Arial", 11), 
                              anchor="w", padx=10, pady=5)
        self.status.pack(fill="x", pady=(0, 10))
        
        # Bind status color changes
        self.vm.status_color.trace_add("write", self.update_status_color)
        
        # Logging text area with scrollbar
        log_frame = tk.Frame(main_frame, bg="#f0f0f0")
        log_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Courier", 10),
            bg="white",
            fg="black",
            relief="solid",
            borderwidth=1
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Session selector frame
        session_frame = tk.Frame(main_frame, bg="#f0f0f0")
        session_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(session_frame, text="AI Agent Session:", bg="#f0f0f0", font=("Arial", 10)).pack(side="left")
        
        self.sessions = [DEFAULT_AI_AGENT_SESSION]  # Default session list
        self.session_combo = ttk.Combobox(session_frame, values=self.sessions, width=20, state="readonly")
        self.session_combo.set(self.sessions[0])
        self.session_combo.pack(side="left", padx=(5, 5))
        
        # Add session button
        add_btn = tk.Button(session_frame, text="+", command=self._add_session, width=3, bg="#e0e0e0")
        add_btn.pack(side="left", padx=(0, 2))
        
        # Remove session button
        remove_btn = tk.Button(session_frame, text="-", command=self._remove_session, width=3, bg="#e0e0e0")
        remove_btn.pack(side="left")
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill="x")
        
        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text="Start",
            command=self.start,
            font=("Arial", 12),
            width=12,
            height=2,
            bg="#e0e0e0",
            relief="raised",
            bd=2
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="Stop",
            command=self.stop,
            font=("Arial", 12),
            width=12,
            height=2,
            bg="#e0e0e0",
            relief="raised",
            bd=2,
            state="disabled"
        )
        self.stop_btn.pack(side="left")
        
        # Bind button states to ViewModel
        self.vm.is_running.trace_add("write", self.update_button_states)
        self.update_button_states()  # Initialize button states
        
        # Set window size and position after all widgets created
        root.update_idletasks()
        root.geometry("600x500+200+150")
        
        # Initialize components
        self.transcriber = None
        self.processor = None
        self.worker_thread = None
        self.stop_event = threading.Event()
        config = ConfigManager.get()
        self.logger = self._initialize_logger(config)

    def start(self) -> None:
        """Start button handler."""
        self.log_text.delete("1.0", tk.END)
        self.vm.is_running.set(True)
        self.vm.status_text.set("Loading the model...")
        self.vm.status_color.set("darkorange")
        self.stop_event.clear()

        # Get fresh config on each start
        config = ConfigManager.get()
        
        # Reset logger just in case user changed logging destination
        self.logger = self._initialize_logger(config)
        
        # Start loading indicator animation
        self.loading_dots = 0
        self._display_load_indicator()
        
        # Init in background thread (model loading, GUI stays responsive)
        self.worker_thread = threading.Thread(
            target=self._run_voice_session,
            args=(config,),
            daemon=False,
        )
        self.worker_thread.start()
    
    def stop(self) -> None:
        """Stop button handler."""
        self.vm.is_running.set(False)
        self.vm.status_text.set("Stopping...")
        self.vm.status_color.set("darkorange")
        self.logger.info("Stopping Voice to Code...")
        self.stop_event.set()
        
        # Start stopping indicator animation
        self.loading_dots = 0
        self._display_load_indicator()
    
    def update_button_states(self, *args: Any) -> None:
        """Called automatically when is_running changes."""
        if self.vm.is_running.get():
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
        else:
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
    
    def update_status_color(self, *args: Any) -> None:
        """Called automatically when status_color changes."""
        self.status.config(bg=self.vm.status_color.get())
    
    def _display_load_indicator(self) -> None:
        """Animate status text with rotating dots. Stop when status is not one of these three values:
            - Loading the model
            - Stopping
            - Listening
        """
        current_text = self.vm.status_text.get()
        base_text = current_text.rstrip('.')
        
        if base_text in ["Loading the model", "Stopping", "Listening"]:
            dots = "." * (self.loading_dots % 4)
            self.vm.status_text.set(f"{base_text}{dots}")
            self.loading_dots += 1
            self.root.after(500, self._display_load_indicator)
    
    def _initialize_logger(self, config) -> Logger:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        log_file = DEFAULT_OUTPUT_DIR / DEFAULT_LOG_FILE
        
        # Use factory to respect log_handler_type from config
        handler = create_log_handler(config, log_file_path=log_file, log_widget=self.log_text)
        return Logger([handler])

    def _run_voice_session(self, config) -> None:
        try:
            # Init processor
            self.logger.debug("Initializing processor...")
            self.logger.info("=== Voice to Code Starting ===")
            self.processor = create_processor(
                config=config,
                get_session_name=self.session_combo.get,
                logger=self.logger
            )

            # Toggle vocalization (only works on macOS)
            self.processor.toggle_vocalization(config['vocalize_response'])
            
            # Init transcriber (SLOW - GUI will freeze)
            self.logger.info(f"Initializing transcriber with '{config['model']}' model...")
            
            self.transcriber = create_transcriber(config, self.logger, self.processor)
            if not self.transcriber.initialize():
                self._show_error("Failed to initialize transcriber")
                self._reset_to_stopped()
                return
            
            # Start streaming
            self.vm.status_text.set("Listening...")
            self.vm.status_color.set("green")
            self.logger.info("Ready. Listening for speech...")
            speak("Voice to Code starting")
            
            # Start listening indicator animation
            self.loading_dots = 0
            self._display_load_indicator()
            
            self._run_streaming()
            
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            self._reset_to_stopped()
    
    def _run_streaming(self) -> None:
        """Run streaming loop in background thread."""
        try:
            self.transcriber.do_streaming(lambda: not self.stop_event.is_set())
            
            self.logger.info("=== Voice to Code Stopped ===")
            self._reset_to_stopped()
            speak("Voice to Code ending")
            
        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            self._reset_to_stopped()
    
    def _reset_to_stopped(self) -> None:
        """Reset UI to stopped state."""
        self.vm.is_running.set(False)
        self.vm.status_text.set("Stopped")
        self.vm.status_color.set("red")
    
    
    def open_settings(self) -> None:
        """Open settings dialog."""
        settings_vm = SettingsViewModel()
        settings_vm.load_from_config(ConfigManager.get())
        SettingsForm(self.root, settings_vm, on_save_callback=self._on_settings_saved)
    
    def _on_settings_saved(self, config: dict[str, Any]) -> None:
        """Called when settings are saved."""
        self.logger.info("=== Settings Saved ===")
        for key, value in config.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("Settings will take effect on next Start.")
    
    def show_help(self) -> None:
        """Display help dialog."""
        HelpForm(self.root)
    
    def _add_session(self) -> None:
        """Add new AI Agent session to dropdown."""
        dialog = InputDialogForm(self.root, "Add Session", "Enter AI Agent session name:")
        name = dialog.get_result()
        if name and name.strip():
            name = name.strip()
            if name not in self.sessions:
                self.sessions.append(name)
                self.session_combo['values'] = self.sessions
                self.session_combo.set(name)
                self.logger.info(f"Added session: {name}")
    
    def _remove_session(self) -> None:
        """Remove current session from dropdown."""
        if len(self.sessions) <= 1:
            self.logger.warning("Cannot remove the last session")
            return
        
        current = self.session_combo.get()
        if current in self.sessions:
            self.sessions.remove(current)
            self.session_combo['values'] = self.sessions
            self.session_combo.set(self.sessions[0])
            self.logger.info(f"Removed session: {current}")
