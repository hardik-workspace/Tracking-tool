"""
User interface module for the tracking application.
Provides popup dialogs for user input on idle/unlock events.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from typing import Callable, Optional


class InactivityPopup:
    """Popup window for asking reason for inactivity."""

    def __init__(self, parent=None):
        self.popup = None
        self.result = None
        self.callback = None
        self.is_destroyed = False

        # Reason options
        self.reasons = [
            "Break",
            "System Issue",
            "Internet Issue",
            "Meeting",
            "Personal Work",
            "Others",
        ]

    def show(
        self,
        title: str = "Activity Tracker",
        message: str = "Please select reason for inactivity",
        callback: Callable = None,
        timeout: int = 600,
    ) -> bool:
        """
        Show the popup dialog.

        Args:
            title: Window title
            message: Popup message
            callback: Callback function when user submits
            timeout: Auto-dismiss timeout in seconds

        Returns:
            True if popup was shown successfully
        """
        try:
            self.callback = callback
            self.result = None
            self.is_destroyed = False

            # Create popup window in a thread to avoid blocking
            def create_popup():
                try:
                    root = tk.Tk()
                    root.withdraw()  # Hide root window

                    self.popup = tk.Toplevel(root)
                    self.popup.title(title)
                    self.popup.geometry("400x250")
                    self.popup.resizable(False, False)

                    # Make it stay on top
                    self.popup.attributes("-topmost", True)
                    self.popup.focus_force()

                    # Add icon if possible
                    try:
                        self.popup.iconbitmap("default")
                    except Exception:
                        pass

                    # Message label
                    msg_label = ttk.Label(
                        self.popup,
                        text=message,
                        wraplength=350,
                        justify="center",
                    )
                    msg_label.pack(pady=15, padx=15)

                    # Reason dropdown
                    ttk.Label(self.popup, text="Reason for inactivity:").pack(pady=5)

                    self.reason_var = tk.StringVar(value=self.reasons[0])
                    reason_dropdown = ttk.Combobox(
                        self.popup,
                        textvariable=self.reason_var,
                        values=self.reasons,
                        state="readonly",
                        width=30,
                    )
                    reason_dropdown.pack(pady=5, padx=15)

                    # Text input for "Others" option
                    ttk.Label(self.popup, text="Additional details (if Others):").pack(
                        pady=5
                    )

                    self.text_input = tk.Text(
                        self.popup, height=4, width=40, wrap=tk.WORD
                    )
                    self.text_input.pack(pady=5, padx=15)

                    # Button frame
                    button_frame = ttk.Frame(self.popup)
                    button_frame.pack(pady=15)

                    submit_btn = ttk.Button(
                        button_frame,
                        text="Submit",
                        command=self._on_submit,
                    )
                    submit_btn.pack(side=tk.LEFT, padx=5)

                    cancel_btn = ttk.Button(
                        button_frame,
                        text="Cancel",
                        command=self._on_cancel,
                    )
                    cancel_btn.pack(side=tk.LEFT, padx=5)

                    # Set timeout for auto-dismiss
                    if timeout > 0:
                        self.popup.after(timeout * 1000, self._on_timeout)

                    # Center on screen
                    self.popup.update_idletasks()
                    width = self.popup.winfo_width()
                    height = self.popup.winfo_height()
                    x = (self.popup.winfo_screenwidth() // 2) - (width // 2)
                    y = (self.popup.winfo_screenheight() // 2) - (height // 2)
                    self.popup.geometry(f"+{x}+{y}")

                    # Handle window close
                    self.popup.protocol("WM_DELETE_WINDOW", self._on_cancel)

                    # Run event loop
                    root.withdraw()
                    self.popup.mainloop()

                except Exception as e:
                    print(f"Error creating popup: {e}")
                    self.is_destroyed = True

            thread = threading.Thread(target=create_popup, daemon=True)
            thread.start()

            return True

        except Exception as e:
            print(f"Error showing popup: {e}")
            return False

    def _on_submit(self):
        """Handle submit button."""
        try:
            reason = self.reason_var.get()
            additional_text = self.text_input.get("1.0", tk.END).strip()

            if reason == "Others" and not additional_text:
                messagebox.showwarning(
                    "Missing Information",
                    "Please provide details for 'Others' option.",
                )
                return

            self.result = {
                "reason": reason,
                "details": additional_text,
                "timestamp": datetime.now().isoformat(),
            }

            if self.callback:
                self.callback(self.result)

            self._close_popup()

        except Exception as e:
            print(f"Error submitting: {e}")
            messagebox.showerror("Error", f"Error submitting: {e}")

    def _on_cancel(self):
        """Handle cancel button."""
        self.result = {
            "reason": "Cancelled",
            "details": "",
            "timestamp": datetime.now().isoformat(),
        }

        if self.callback:
            self.callback(self.result)

        self._close_popup()

    def _on_timeout(self):
        """Handle timeout."""
        if not self.is_destroyed:
            self.result = {
                "reason": "Timeout",
                "details": "",
                "timestamp": datetime.now().isoformat(),
            }

            if self.callback:
                self.callback(self.result)

            self._close_popup()

    def _close_popup(self):
        """Close the popup window."""
        try:
            self.is_destroyed = True
            if self.popup:
                self.popup.quit()
                self.popup.destroy()
        except Exception:
            pass


class StatusWindow:
    """Minimal status window for showing application status."""

    def __init__(self):
        self.window = None

    def create(self, title: str = "Activity Tracker"):
        """Create the status window."""
        try:
            self.window = tk.Tk()
            self.window.title(title)
            self.window.geometry("300x150")
            self.window.resizable(False, False)

            # Status label
            self.status_label = ttk.Label(
                self.window,
                text="Status: Running",
                font=("Arial", 10),
            )
            self.status_label.pack(pady=10)

            # Activity label
            self.activity_label = ttk.Label(
                self.window,
                text="Activity: Active",
                font=("Arial", 9),
            )
            self.activity_label.pack(pady=5)

            # Stats label
            self.stats_label = ttk.Label(
                self.window,
                text="Idle Time: 0 min | Active Time: 0 min",
                font=("Arial", 8),
            )
            self.stats_label.pack(pady=5)

            # Button frame
            button_frame = ttk.Frame(self.window)
            button_frame.pack(pady=10)

            exit_btn = ttk.Button(
                button_frame,
                text="Exit",
                command=self.window.quit,
            )
            exit_btn.pack(side=tk.LEFT, padx=5)

            minimize_btn = ttk.Button(
                button_frame,
                text="Minimize",
                command=self.window.withdraw,
            )
            minimize_btn.pack(side=tk.LEFT, padx=5)

            return True

        except Exception as e:
            print(f"Error creating status window: {e}")
            return False

    def update_status(self, status: str):
        """Update status label."""
        try:
            if self.window:
                self.status_label.config(text=f"Status: {status}")
                self.window.update()
        except Exception:
            pass

    def update_activity(self, activity: str):
        """Update activity label."""
        try:
            if self.window:
                self.activity_label.config(text=f"Activity: {activity}")
                self.window.update()
        except Exception:
            pass

    def update_stats(self, idle_time: int, active_time: int):
        """Update statistics."""
        try:
            if self.window:
                self.stats_label.config(
                    text=f"Idle Time: {idle_time} min | Active Time: {active_time} min"
                )
                self.window.update()
        except Exception:
            pass

    def show(self):
        """Show the window."""
        try:
            if self.window:
                self.window.deiconify()
                self.window.lift()
                return True
        except Exception:
            pass
        return False

    def close(self):
        """Close the window."""
        try:
            if self.window:
                self.window.quit()
                self.window.destroy()
        except Exception:
            pass
