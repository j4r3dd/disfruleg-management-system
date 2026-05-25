# -*- coding: utf-8 -*-
"""
Premium Loading Indicator Component
Modern, animated loading dialog with custom spinner
"""

import customtkinter as ctk
import threading
import time
import math
from typing import Optional, Callable


class LoadingIndicator:
    """
    Premium loading indicator with custom animated spinner
    
    Features:
    - Custom circular spinner animation
    - Pulsing glow effect
    - Floating dots animation
    - Glassmorphism design
    - Smooth fade in/out
    """
    
    # Color themes
    THEMES = {
        'purple': {
            'primary': '#9C27B0',
            'secondary': '#E040FB',
            'glow': '#CE93D8',
            'bg': '#1a1a2e',
            'card': '#16213e',
            'border': '#0f3460'
        },
        'blue': {
            'primary': '#2196F3',
            'secondary': '#03DAC6',
            'glow': '#64B5F6',
            'bg': '#0a1628',
            'card': '#102840',
            'border': '#1a4a6e'
        },
        'green': {
            'primary': '#00E676',
            'secondary': '#69F0AE',
            'glow': '#B9F6CA',
            'bg': '#0a1a14',
            'card': '#0d2818',
            'border': '#1b5e20'
        },
        'orange': {
            'primary': '#FF9800',
            'secondary': '#FFAB40',
            'glow': '#FFE0B2',
            'bg': '#1a1408',
            'card': '#2d2010',
            'border': '#e65100'
        }
    }

    def __init__(
        self, 
        parent, 
        message: str = "Cargando...",
        subtitle: str = "Por favor espere...",
        timeout: int = 30,
        theme: str = 'purple',
        show_dots: bool = True
    ):
        """
        Initialize premium loading indicator
        
        Args:
            parent: Parent window
            message: Main message to display
            subtitle: Secondary message
            timeout: Auto-close timeout in seconds
            theme: Color theme ('purple', 'blue', 'green', 'orange')
            show_dots: Show floating dots animation
        """
        self.parent = parent
        self.message = message
        self.subtitle = subtitle
        self.timeout = timeout
        self.theme = self.THEMES.get(theme, self.THEMES['purple'])
        self.show_dots = show_dots
        
        self.is_closed = False
        self.start_time = time.time()
        self._animation_running = True
        
        # Animation state
        self._spinner_angle = 0
        self._pulse_phase = 0
        self._dots_phase = 0
        
        # Create dialog
        self._create_dialog()
        self._create_ui()
        self._start_animations()
        self._start_timeout_monitor()
    
    def _create_dialog(self):
        """Create the dialog window"""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("")
        self.dialog.geometry("420x280")
        self.dialog.resizable(False, False)
        self.dialog.overrideredirect(True)
        
        # Make transparent for rounded corners effect
        self.dialog.configure(fg_color=self.theme['bg'])
        
        # Center on parent or screen
        self._center_window()
        
        # Modal behavior
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        
        # Fade in effect
        self.dialog.attributes('-alpha', 0.0)
        self._fade_in()
    
    def _center_window(self):
        """Center dialog on parent window or screen"""
        self.dialog.update_idletasks()
        
        width, height = 420, 280
        
        if self.parent:
            try:
                parent_x = self.parent.winfo_x()
                parent_y = self.parent.winfo_y()
                parent_w = self.parent.winfo_width()
                parent_h = self.parent.winfo_height()
                
                x = parent_x + (parent_w - width) // 2
                y = parent_y + (parent_h - height) // 2
                
                self.dialog.geometry(f"{width}x{height}+{x}+{y}")
                return
            except:
                pass
        
        # Fallback: center on screen
        screen_w = self.dialog.winfo_screenwidth()
        screen_h = self.dialog.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _fade_in(self):
        """Smooth fade in animation"""
        def fade():
            alpha = 0.0
            while alpha < 1.0 and not self.is_closed:
                try:
                    if not self._safe_widget_exists(self.dialog):
                        break
                    alpha += 0.08
                    self.dialog.attributes('-alpha', min(alpha, 1.0))
                    time.sleep(0.02)
                except Exception:
                    break
        
        threading.Thread(target=fade, daemon=True).start()
    
    def _fade_out(self, callback=None):
        """Smooth fade out animation"""
        def fade():
            alpha = 1.0
            while alpha > 0.0:
                try:
                    if not self._safe_widget_exists(self.dialog):
                        break
                    alpha -= 0.1
                    self.dialog.attributes('-alpha', max(alpha, 0.0))
                    time.sleep(0.02)
                except Exception:
                    break
            if callback:
                try:
                    callback()
                except Exception:
                    pass
        
        threading.Thread(target=fade, daemon=True).start()
    
    def _create_ui(self):
        """Create the premium UI"""
        # Main card with glassmorphism effect
        self.main_card = ctk.CTkFrame(
            self.dialog,
            fg_color=self.theme['card'],
            corner_radius=25,
            border_width=2,
            border_color=self.theme['border']
        )
        self.main_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Content container
        content = ctk.CTkFrame(self.main_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=25)
        
        # === SPINNER CANVAS ===
        self.canvas_size = 90
        self.canvas = ctk.CTkCanvas(
            content,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.theme['card'],
            highlightthickness=0
        )
        self.canvas.pack(pady=(0, 20))
        
        # Draw initial spinner
        self._draw_spinner()
        
        # === FLOATING DOTS ===
        if self.show_dots:
            self.dots_canvas = ctk.CTkCanvas(
                content,
                width=100,
                height=20,
                bg=self.theme['card'],
                highlightthickness=0
            )
            self.dots_canvas.pack(pady=(0, 15))
            self._draw_dots()
        
        # === MESSAGE ===
        self.message_label = ctk.CTkLabel(
            content,
            text=self.message,
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        )
        self.message_label.pack(pady=(0, 8))
        
        # === SUBTITLE ===
        self.subtitle_label = ctk.CTkLabel(
            content,
            text=self.subtitle,
            font=("Segoe UI", 12),
            text_color="#888888"
        )
        self.subtitle_label.pack()
        
        # === PROGRESS BAR (subtle) ===
        self.progress_frame = ctk.CTkFrame(
            content,
            fg_color=self.theme['border'],
            corner_radius=3,
            height=4
        )
        self.progress_frame.pack(fill="x", pady=(20, 0))
        
        self.progress_bar = ctk.CTkFrame(
            self.progress_frame,
            fg_color=self.theme['primary'],
            corner_radius=3,
            height=4
        )
        self.progress_bar.place(relx=0, rely=0, relwidth=0.3, relheight=1)
    
    def _draw_spinner(self):
        """Draw the custom circular spinner"""
        # Safety check before drawing
        if self.is_closed or not self._safe_widget_exists(self.canvas):
            return
            
        try:
            self.canvas.delete("all")
            
            cx, cy = self.canvas_size // 2, self.canvas_size // 2
            radius = 35
            line_width = 4
            
            # Background circle (subtle)
            self.canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                outline=self.theme['border'],
                width=line_width
            )
            
            # Spinning arc with gradient effect
            arc_length = 90  # degrees
            start_angle = self._spinner_angle
            
            # Main arc
            self.canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=start_angle,
                extent=arc_length,
                outline=self.theme['primary'],
                width=line_width,
                style='arc'
            )
            
            # Glow effect (secondary arc)
            self.canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=start_angle + arc_length - 20,
                extent=30,
                outline=self.theme['secondary'],
                width=line_width,
                style='arc'
            )
            
            # Center pulsing dot
            pulse_size = 8 + math.sin(self._pulse_phase) * 3
            pulse_color = self.theme['glow'] if int(self._pulse_phase * 2) % 2 == 0 else self.theme['primary']
            
            self.canvas.create_oval(
                cx - pulse_size, cy - pulse_size,
                cx + pulse_size, cy + pulse_size,
                fill=pulse_color,
                outline=""
            )
        except Exception:
            pass  # Suppress any drawing errors during close
    
    def _draw_dots(self):
        """Draw floating dots animation"""
        if not hasattr(self, 'dots_canvas') or self.is_closed:
            return
        
        if not self._safe_widget_exists(self.dots_canvas):
            return
        
        try:
            self.dots_canvas.delete("all")
            
            dot_count = 3
            base_y = 10
            spacing = 30
            start_x = 20
            
            for i in range(dot_count):
                # Calculate position with wave effect
                phase_offset = i * (math.pi / 3)
                y_offset = math.sin(self._dots_phase + phase_offset) * 5
                
                # Calculate size with pulse effect
                size = 6 + math.sin(self._dots_phase + phase_offset) * 2
                
                x = start_x + i * spacing
                y = base_y + y_offset
                
                # Draw dot with gradient-like effect
                self.dots_canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
                    fill=self.theme['secondary'] if i == int(self._dots_phase / 0.5) % dot_count else self.theme['primary'],
                    outline=""
                )
        except Exception:
            pass  # Suppress any drawing errors during close
    
    def _animate_progress(self):
        """Animate the progress bar back and forth"""
        if self.is_closed:
            return
            
        try:
            if self._safe_widget_exists(self.progress_bar):
                # Calculate position (oscillate between 0 and 0.7)
                progress = (math.sin(time.time() * 2) + 1) / 2 * 0.7
                self.progress_bar.place(relx=progress, rely=0, relwidth=0.3, relheight=1)
        except Exception:
            pass
    
    def _start_animations(self):
        """Start all animations"""
        def animate():
            while self._animation_running and not self.is_closed:
                try:
                    # Check if we should stop BEFORE doing any work
                    if self.is_closed or not self._animation_running:
                        break
                    
                    # Update spinner
                    self._spinner_angle = (self._spinner_angle + 8) % 360
                    self._pulse_phase += 0.15
                    self._dots_phase += 0.12
                    
                    # Safely check widget existence before drawing
                    if self._safe_widget_exists(self.dialog) and self._safe_widget_exists(self.canvas):
                        self._draw_spinner()
                        if self.show_dots and hasattr(self, 'dots_canvas') and self._safe_widget_exists(self.dots_canvas):
                            self._draw_dots()
                        self._animate_progress()
                        self._safe_dialog_update()
                    else:
                        break  # Widget destroyed, stop animation
                    
                    time.sleep(0.03)  # ~33 FPS
                except Exception:
                    break  # Any error means we should stop
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()
    
    def _start_timeout_monitor(self):
        """Monitor timeout and auto-close"""
        def monitor():
            while not self.is_closed:
                if time.time() - self.start_time > self.timeout:
                    self.close()
                    break
                time.sleep(0.5)
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def update_message(self, message: str, subtitle: str = None):
        """Update displayed messages"""
        try:
            if not self.is_closed and self.dialog.winfo_exists():
                self.message_label.configure(text=message)
                if subtitle:
                    self.subtitle_label.configure(text=subtitle)
                self.dialog.update()
        except:
            pass
    
    def _safe_widget_exists(self, widget) -> bool:
        """Safely check if a widget exists and is valid"""
        try:
            return widget is not None and widget.winfo_exists()
        except Exception:
            return False
    
    def _safe_dialog_update(self):
        """Safely update dialog without raising exceptions"""
        try:
            if self._safe_widget_exists(self.dialog):
                self.dialog.update()
        except Exception:
            pass
    
    def close(self):
        """Close with fade out animation"""
        if self.is_closed:
            return
        
        # Mark as closed FIRST to stop all animations immediately
        self.is_closed = True
        self._animation_running = False
        
        # Small delay to let animations stop
        time.sleep(0.05)
        
        def destroy():
            try:
                if self._safe_widget_exists(self.dialog):
                    try:
                        self.dialog.grab_release()
                    except Exception:
                        pass
                    try:
                        self.dialog.destroy()
                    except Exception:
                        pass
            except Exception:
                pass
        
        # Fade out then destroy
        self._fade_out(destroy)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    
    @classmethod
    def show(
        cls, 
        parent, 
        message: str = "Cargando...",
        subtitle: str = "Por favor espere...",
        timeout: int = 30,
        theme: str = 'purple'
    ) -> 'LoadingIndicator':
        """
        Show a loading indicator
        
        Args:
            parent: Parent window
            message: Main message
            subtitle: Secondary message
            timeout: Auto-close timeout
            theme: Color theme
            
        Returns:
            LoadingIndicator instance
        """
        return cls(parent, message, subtitle, timeout, theme)
    
    @classmethod
    def run_with_loading(
        cls,
        parent,
        message: str,
        task: Callable,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        timeout: int = 30,
        theme: str = 'purple'
    ):
        """
        Run a task with loading indicator
        
        Args:
            parent: Parent window
            message: Loading message
            task: Function to execute
            on_complete: Success callback
            on_error: Error callback
            timeout: Timeout in seconds
            theme: Color theme
        """
        loading = cls.show(parent, message, timeout=timeout, theme=theme)
        
        def run_task():
            try:
                result = task()
                loading.close()
                time.sleep(0.3)  # Wait for fade out
                if on_complete:
                    on_complete(result)
            except Exception as e:
                loading.close()
                time.sleep(0.3)
                if on_error:
                    on_error(e)
                else:
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"Error durante la operación:\n{str(e)}")
        
        threading.Thread(target=run_task, daemon=True).start()
        return loading
    
    @classmethod
    def show_briefly(cls, parent, message: str, duration: float = 2.0, theme: str = 'purple'):
        """Show loading indicator briefly"""
        loading = cls.show(parent, message, timeout=int(duration) + 2, theme=theme)
        
        def auto_close():
            time.sleep(duration)
            loading.close()
        
        threading.Thread(target=auto_close, daemon=True).start()
        return loading


class SimpleLoadingDialog:
    """Lightweight loading dialog for quick operations"""
    
    def __init__(self, parent, message: str = "Cargando..."):
        self.is_closed = False
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("")
        self.dialog.geometry("320x140")
        self.dialog.resizable(False, False)
        self.dialog.overrideredirect(True)
        self.dialog.configure(fg_color="#1a1a2e")
        
        # Center
        self.dialog.update_idletasks()
        if parent:
            try:
                x = parent.winfo_x() + (parent.winfo_width() - 320) // 2
                y = parent.winfo_y() + (parent.winfo_height() - 140) // 2
                self.dialog.geometry(f"+{x}+{y}")
            except:
                pass
        
        # Modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.lift()
        self.dialog.attributes('-topmost', True)
        
        # UI
        frame = ctk.CTkFrame(
            self.dialog, 
            fg_color="#16213e",
            corner_radius=20,
            border_width=2,
            border_color="#0f3460"
        )
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)
        
        # Spinner emoji with animation
        self.spinner_label = ctk.CTkLabel(
            content,
            text="⏳",
            font=("Segoe UI", 36)
        )
        self.spinner_label.pack(pady=(0, 12))
        
        ctk.CTkLabel(
            content,
            text=message,
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        ).pack()
        
        self.dialog.update()
        
        # Simple spinner animation
        self._animate = True
        self._start_animation()
    
    def _start_animation(self):
        """Animate spinner emoji"""
        spinners = ["⏳", "⌛"]
        idx = [0]
        
        def animate():
            while self._animate and not self.is_closed:
                try:
                    if self.dialog.winfo_exists():
                        self.spinner_label.configure(text=spinners[idx[0] % 2])
                        idx[0] += 1
                        self.dialog.update()
                    time.sleep(0.5)
                except:
                    break
        
        threading.Thread(target=animate, daemon=True).start()
    
    def close(self):
        if self.is_closed:
            return
        self.is_closed = True
        self._animate = False
        
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


# ==================== DEMO ====================
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.geometry("700x500")
    root.title("Premium Loading Indicator Demo")
    root.configure(fg_color="#0a0a0a")
    
    # Title
    ctk.CTkLabel(
        root,
        text="🎨 Premium Loading Indicator",
        font=("Segoe UI", 28, "bold"),
        text_color="white"
    ).pack(pady=40)
    
    # Theme buttons frame
    themes_frame = ctk.CTkFrame(root, fg_color="transparent")
    themes_frame.pack(pady=20)
    
    ctk.CTkLabel(
        themes_frame,
        text="Select Theme:",
        font=("Segoe UI", 14),
        text_color="#888"
    ).pack(side="left", padx=(0, 15))
    
    def show_loading(theme):
        def task():
            loading = LoadingIndicator.show(
                root, 
                f"Cargando {theme.title()}...",
                "Iniciando módulo...",
                theme=theme
            )
            time.sleep(4)
            loading.close()
        threading.Thread(target=task, daemon=True).start()
    
    for theme in ['purple', 'blue', 'green', 'orange']:
        color = LoadingIndicator.THEMES[theme]['primary']
        ctk.CTkButton(
            themes_frame,
            text=theme.title(),
            width=100,
            height=40,
            corner_radius=10,
            fg_color=color,
            hover_color=LoadingIndicator.THEMES[theme]['secondary'],
            command=lambda t=theme: show_loading(t)
        ).pack(side="left", padx=5)
    
    # Simple loading button
    ctk.CTkButton(
        root,
        text="Simple Loading Dialog",
        width=200,
        height=45,
        corner_radius=10,
        fg_color="#333",
        hover_color="#444",
        command=lambda: threading.Thread(
            target=lambda: (
                SimpleLoadingDialog(root, "Cargando datos...").__enter__(),
                time.sleep(3),
            ),
            daemon=True
        ).start()
    ).pack(pady=30)
    
    # Info
    ctk.CTkLabel(
        root,
        text="Click any theme button to see the premium loading animation",
        font=("Segoe UI", 11),
        text_color="#666"
    ).pack(pady=20)
    
    root.mainloop()