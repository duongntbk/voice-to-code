"""Help dialog form."""

import tkinter as tk
import webbrowser


class HelpForm:
    """Help/About dialog."""
    
    def __init__(self, parent: tk.Tk | tk.Toplevel) -> None:
        """
        Create and show help dialog.
        
        Args:
            parent: Parent window
        """
        self.window = tk.Toplevel(parent)
        self.window.title("Help")
        self.window.geometry("400x200")
        self.window.configure(bg="#f0f0f0")
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        # Main frame
        frame = tk.Frame(self.window, bg="#f0f0f0", padx=30, pady=30)
        frame.pack(expand=True, fill="both")
        
        # Help text container
        text_frame = tk.Frame(frame, bg="#f0f0f0")
        text_frame.pack(pady=20)
        
        # Help text
        help_text = tk.Label(
            text_frame,
            text="Report issues on ",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#333333"
        )
        help_text.pack(side="left")
        
        # Clickable GitHub link
        github_link = tk.Label(
            text_frame,
            text="GitHub",
            font=("Arial", 14, "underline"),
            bg="#f0f0f0",
            fg="#0066cc",
            cursor="hand2"
        )
        github_link.pack(side="left")
        github_link.bind("<Button-1>", lambda e: self._open_issue_page())
        
        # OK button
        ok_button = tk.Button(
            frame,
            text="OK",
            command=self.window.destroy,
            font=("Arial", 12),
            width=10,
            bg="#e0e0e0",
            fg="black",
            relief="raised",
            bd=2
        )
        ok_button.pack(pady=10)
    
    def _open_issue_page(self) -> None:
        """Open issue page in browser."""
        webbrowser.open("https://example.com")
