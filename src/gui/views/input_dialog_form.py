"""Input dialog form."""

import tkinter as tk


class InputDialogForm:
    """Simple input dialog."""
    
    def __init__(self, parent: tk.Tk | tk.Toplevel, title: str, prompt: str):
        """
        Create and show input dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            prompt: Input prompt text
        """
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x120")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        # Input field
        tk.Label(self.dialog, text=prompt).pack(pady=(10, 5))
        self.entry = tk.Entry(self.dialog, width=30)
        self.entry.pack(pady=5)
        self.entry.focus()
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", command=self._on_ok, width=10).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self._on_cancel, width=10).pack(side="left", padx=5)
        
        self.entry.bind('<Return>', lambda e: self._on_ok())
        
        self.dialog.wait_window()
    
    def _on_ok(self) -> None:
        """OK button handler."""
        self.result = self.entry.get()
        self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """Cancel button handler."""
        self.dialog.destroy()
    
    def get_result(self) -> str | None:
        """Get user input result.
        
        Returns:
            User input or None if cancelled
        """
        return self.result
