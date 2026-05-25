# -*- coding: utf-8 -*-
"""
Reusable Loading Indicator Component
Clean, modern loading dialog with spinner animation
"""

import customtkinter as ctk
import threading
import time
from typing import Optional, Callable


class LoadingIndicator:
    """
    Reusable loading indicator with spinner animation

    Usage:
        # Simple usage
        loading = LoadingIndicator.show(parent, "Loading module...")
        # ... do work ...
        loading.close()

        # Context manager (auto-close)
        with LoadingIndicator.show(parent, "Processing...") as loading:
            # ... do work ...
            pass

        # With task execution
        def my_task():
            time.sleep(2)
            return "Done!"

        result = LoadingIndicator.run_with_loading(
            parent,
            "Loading...",
            my_task
        )
    """

    def __init__(self, parent, message: str = "Cargando...", timeout: int = 30):
        """
        Initialize loading indicator

        Args:
            parent: Parent window (CTk or Tk)
            message: Message to display
            timeout: Maximum time to show loading (seconds)
        """
        self.parent = parent
        self.message = message
        self.timeout = timeout
        self.is_closed = False
        self.start_time = time.time()

        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("")
        self.dialog.geometry("350x180")
        self.dialog.resizable(False, False)

        # Remove window decorations for modern look
        self.dialog.overrideredirect(True)

        # Center on screen
        self._center_window()

        # Make it modal-like
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)

        # Create UI
        self._create_ui()

        # Start spinner animation
        self._spinner_running = True
        self._spinner_angle = 0
        self._start_spinner_animation()

        # Auto-close timeout
        self._start_timeout_monitor()

    def _center_window(self):
        """Center the dialog on parent window or screen"""
        self.dialog.update_idletasks()

        # Get parent position and size
        if self.parent:
            try:
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_width = self.parent.winfo_width()
                parent_height = self.parent.winfo_height()

                # Calculate center position
                x = parent_x + (parent_width - 350) // 2
                y = parent_y + (parent_height - 180) // 2

                self.dialog.geometry(f"+{x}+{y}")
                return
            except:
                pass

        # Fallback: center on screen
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - 350) // 2
        y = (screen_height - 180) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _create_ui(self):
        """Create the loading indicator UI"""
        # Main container with rounded corners effect
        main_frame = ctk.CTkFrame(
            self.dialog,
            fg_color=("#2a2a2a", "#2a2a2a"),
            corner_radius=20,
            border_width=2,
            border_color=("#3a3a3a", "#3a3a3a")
        )
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Content container
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Spinner (using progressbar in indeterminate mode)
        self.progress = ctk.CTkProgressBar(
            content_frame,
            mode="indeterminate",
            height=8,
            progress_color=("#9C27B0", "#9C27B0"),
            fg_color=("#404040", "#404040")
        )
        self.progress.pack(pady=(0, 20))
        self.progress.start()

        # Icon/Emoji
        icon_label = ctk.CTkLabel(
            content_frame,
            text="⏳",
            font=("Arial", 36)
        )
        icon_label.pack(pady=(0, 15))

        # Message
        self.message_label = ctk.CTkLabel(
            content_frame,
            text=self.message,
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.message_label.pack(pady=(0, 5))

        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            content_frame,
            text="Por favor espere...",
            font=("Arial", 11),
            text_color="gray60"
        )
        self.subtitle_label.pack()

    def _start_spinner_animation(self):
        """Start the spinner animation in background thread"""
        def animate():
            while self._spinner_running and not self.is_closed:
                try:
                    if self.dialog.winfo_exists():
                        self.dialog.update()
                    time.sleep(0.05)
                except:
                    break

        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()

    def _start_timeout_monitor(self):
        """Monitor timeout and auto-close if exceeded"""
        def monitor():
            while not self.is_closed:
                elapsed = time.time() - self.start_time
                if elapsed > self.timeout:
                    self.close()
                    break
                time.sleep(0.5)

        timeout_thread = threading.Thread(target=monitor, daemon=True)
        timeout_thread.start()

    def update_message(self, message: str):
        """Update the loading message"""
        try:
            if not self.is_closed and self.dialog.winfo_exists():
                self.message_label.configure(text=message)
                self.dialog.update()
        except:
            pass

    def close(self):
        """Close the loading indicator"""
        if self.is_closed:
            return

        self.is_closed = True
        self._spinner_running = False

        try:
            if self.dialog.winfo_exists():
                self.progress.stop()
                self.dialog.grab_release()
                self.dialog.destroy()
        except:
            pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False

    @classmethod
    def show(cls, parent, message: str = "Cargando...", timeout: int = 30) -> 'LoadingIndicator':
        """
        Show a loading indicator

        Args:
            parent: Parent window
            message: Message to display
            timeout: Auto-close timeout in seconds

        Returns:
            LoadingIndicator instance (call .close() when done)
        """
        return cls(parent, message, timeout)

    @classmethod
    def run_with_loading(
        cls,
        parent,
        message: str,
        task: Callable,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        timeout: int = 30
    ):
        """
        Run a task with loading indicator in background thread

        Args:
            parent: Parent window
            message: Loading message
            task: Function to execute (should return result)
            on_complete: Callback when task completes (receives result)
            on_error: Callback when task fails (receives exception)
            timeout: Timeout in seconds

        Returns:
            LoadingIndicator instance
        """
        loading = cls.show(parent, message, timeout)

        def run_task():
            try:
                result = task()
                loading.close()
                if on_complete:
                    on_complete(result)
            except Exception as e:
                loading.close()
                if on_error:
                    on_error(e)
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"Error durante la operación:\n{str(e)}")

        task_thread = threading.Thread(target=run_task, daemon=True)
        task_thread.start()

        return loading

    @classmethod
    def show_briefly(cls, parent, message: str, duration: float = 2.0):
        """
        Show a loading indicator for a brief moment (non-blocking)

        Args:
            parent: Parent window
            message: Message to display
            duration: How long to show (seconds)
        """
        loading = cls.show(parent, message, timeout=int(duration) + 1)

        def auto_close():
            time.sleep(duration)
            loading.close()

        close_thread = threading.Thread(target=auto_close, daemon=True)
        close_thread.start()

        return loading


class SimpleLoadingDialog:
    """
    Simpler, lighter-weight loading indicator (no animation)
    Useful for very quick operations where full LoadingIndicator is overkill
    """

    def __init__(self, parent, message: str = "Cargando..."):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("")
        self.dialog.geometry("300x120")
        self.dialog.resizable(False, False)
        self.dialog.overrideredirect(True)

        # Center
        self.dialog.update_idletasks()
        if parent:
            try:
                x = parent.winfo_x() + (parent.winfo_width() - 300) // 2
                y = parent.winfo_y() + (parent.winfo_height() - 120) // 2
                self.dialog.geometry(f"+{x}+{y}")
            except:
                pass

        # Make modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)

        # Simple UI
        frame = ctk.CTkFrame(self.dialog, fg_color=("#2a2a2a", "#2a2a2a"))
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text="⏳",
            font=("Arial", 32)
        ).pack(pady=(10, 10))

        ctk.CTkLabel(
            frame,
            text=message,
            font=("Arial", 12)
        ).pack()

        self.dialog.update()

    def close(self):
        try:
            if self.dialog.winfo_exists():
                self.dialog.grab_release()
                self.dialog.destroy()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# Example usage
if __name__ == "__main__":
    import customtkinter as ctk

    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.geometry("600x400")
    root.title("Loading Indicator Demo")

    def test_basic():
        loading = LoadingIndicator.show(root, "Cargando módulo...")
        time.sleep(3)
        loading.close()

    def test_context_manager():
        with LoadingIndicator.show(root, "Procesando datos..."):
            time.sleep(2)

    def test_with_task():
        def long_task():
            time.sleep(3)
            return "¡Completado!"

        def on_done(result):
            from tkinter import messagebox
            messagebox.showinfo("Éxito", result)

        LoadingIndicator.run_with_loading(
            root,
            "Ejecutando tarea...",
            long_task,
            on_complete=on_done
        )

    def test_simple():
        with SimpleLoadingDialog(root, "Espere un momento..."):
            time.sleep(2)

    # UI
    ctk.CTkLabel(
        root,
        text="Loading Indicator Examples",
        font=("Arial", 20, "bold")
    ).pack(pady=30)

    ctk.CTkButton(
        root,
        text="Test Basic Loading",
        command=lambda: threading.Thread(target=test_basic, daemon=True).start()
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Test Context Manager",
        command=lambda: threading.Thread(target=test_context_manager, daemon=True).start()
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Test With Task",
        command=test_with_task
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Test Simple Dialog",
        command=lambda: threading.Thread(target=test_simple, daemon=True).start()
    ).pack(pady=10)

    root.mainloop()
