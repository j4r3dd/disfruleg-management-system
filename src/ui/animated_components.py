import customtkinter as ctk
import math

class LoadingSpinner(ctk.CTkFrame):
    """Spinner de carga ultra-robusto para CustomTkinter."""
    
    def __init__(self, master, size=50, fg_color="transparent",
                 progress_color=None, bg_overlay_color=None,
                 bar_width=6, speed=0.1, direction="right"):
        
        # Inicializar todos los atributos ANTES de super().__init__
        self._destroyed = False
        self._running = False
        self._after_id = None
        self._angle = 0
        self._canvas = None
        
        # Validar master
        if master is None:
            raise ValueError("Master widget es None")
        
        try:
            if not master.winfo_exists():
                raise ValueError("Master widget no existe")
        except Exception as e:
            raise ValueError(f"Master inválido: {e}")
        
        # Inicializar todos los atributos que usa _draw() ANTES de super().__init__
        self._spinner_size = int(size)
        self.bar_width = int(bar_width)
        self.speed = float(speed)
        self.direction = str(direction).lower()
        
        # Guardar colores originales
        self._progress_color_tuple = progress_color 
        self._bg_overlay_color_tuple = bg_overlay_color
        
        # Inicializar colores basados en tema actual
        self._update_colors()
        
        # Llamar a super().__init__
        super().__init__(master, width=size, height=size, fg_color=fg_color, corner_radius=int(size/2))

        # Crear canvas
        try:
            self._canvas = ctk.CTkCanvas(
                self, 
                width=self._spinner_size, 
                height=self._spinner_size,
                highlightthickness=0, 
                bg=self.bg_color
            )
            self._canvas.pack(fill="both", expand=True)
        except Exception as e:
            self._destroyed = True
            raise Exception(f"No se pudo crear canvas: {e}")

        # Dibujar estado inicial
        self._draw()

    def _update_colors(self):
        """Actualiza los colores según el tema actual"""
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        if isinstance(self._progress_color_tuple, tuple):
            self.progress_color = self._progress_color_tuple[1 if is_dark else 0]
        else:
            self.progress_color = self._progress_color_tuple or ("#1f6aa5" if not is_dark else "#3b8ed0")
        
        if isinstance(self._bg_overlay_color_tuple, tuple):
            self.bg_color = self._bg_overlay_color_tuple[1 if is_dark else 0]
        else:
            self.bg_color = self._bg_overlay_color_tuple or ("#dbe0e5" if not is_dark else "#2b2b2b")
    
    def _safe_exists(self):
        """Verifica si el widget aún existe de forma segura"""
        try:
            return not self._destroyed and self.winfo_exists()
        except:
            return False
    
    def _draw(self, **kwargs):
        """Dibuja el spinner con verificaciones de seguridad"""
        # Verificar que tenemos todos los atributos necesarios
        if not hasattr(self, 'bar_width'):
            self.bar_width = 6
        
        if not hasattr(self, '_spinner_size'):
            self._spinner_size = 50
        
        if not self._safe_exists() or self._canvas is None:
            return
        
        try:
            self._canvas.delete("all")
            
            cx = self._spinner_size / 2
            cy = self._spinner_size / 2
            radius = self._spinner_size / 2 - self.bar_width / 2
            cap_radius = self.bar_width / 2

            # Círculo de fondo
            self._canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                outline=self.bg_color,
                width=self.bar_width
            )
            
            # Arco animado
            self._canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=self._angle, 
                extent=120,
                style=ctk.ARC,
                outline=self.progress_color,
                width=self.bar_width
            )
            
            # Caps redondeados en los extremos
            start_rad = math.radians(self._angle)
            end_rad = math.radians(self._angle + 120)

            start_x = cx + radius * math.cos(start_rad)
            start_y = cy - radius * math.sin(start_rad)
            end_x = cx + radius * math.cos(end_rad)
            end_y = cy - radius * math.sin(end_rad)

            for x, y in [(start_x, start_y), (end_x, end_y)]:
                self._canvas.create_oval(
                    x - cap_radius, y - cap_radius,
                    x + cap_radius, y + cap_radius,
                    fill=self.progress_color,
                    outline=""
                )
        except:
            pass

    def _animate(self):
        """Animación del spinner con protección contra callbacks huérfanos"""
        # Triple verificación antes de continuar
        if not self._safe_exists() or not self._running or self._destroyed:
            self._after_id = None
            self._running = False
            return
        
        try:
            # Actualizar ángulo
            step = 10 if self.direction == "right" else -10
            self._angle = (self._angle + step) % 360
            
            # Redibujar
            self._draw()
            
            # Verificar nuevamente antes de programar siguiente iteración
            if self._safe_exists() and self._running and not self._destroyed:
                delay_ms = int(self.speed * 1000)
                self._after_id = self.after(delay_ms, self._animate)
            else:
                self._after_id = None
                self._running = False
                
        except:
            self._after_id = None
            self._running = False

    def start(self):
        """Inicia la animación del spinner"""
        if self._safe_exists() and not self._running:
            self._running = True
            self._animate()

    def stop(self):
        """Detiene la animación con cancelación garantizada"""
        self._running = False
        
        if self._after_id is not None:
            try:
                if self._safe_exists():
                    self.after_cancel(self._after_id)
            except:
                pass
            finally:
                self._after_id = None

    def update_theme(self):
        """Actualiza los colores del tema"""
        if self._safe_exists():
            self._update_colors()
            try:
                if self._canvas is not None:
                    self._canvas.config(bg=self.bg_color)
            except:
                pass
            self._draw()

    def destroy(self):
        """Destruye el spinner con limpieza total garantizada"""
        # Prevenir múltiples llamadas
        if hasattr(self, '_destroyed') and self._destroyed:
            return
        
        # Marcar como destruido PRIMERO
        self._destroyed = True
        
        # Detener animación
        self.stop()
        
        # Procesar eventos pendientes
        try:
            if self.winfo_exists():
                self.update_idletasks()
        except:
            pass
        
        # Destruir canvas
        if self._canvas is not None:
            try:
                self._canvas.destroy()
            except:
                pass
            self._canvas = None
        
        # Destruir el frame
        try:
            super().destroy()
        except:
            pass


def create_spinner_safe(master, **kwargs):
    """Factory function para crear spinners de forma segura"""
    try:
        spinner = LoadingSpinner(master, **kwargs)
        return spinner
    except Exception as e:
        print(f"Error al crear spinner: {e}")
        return None


class SpinnerContext:
    """Context manager para uso con 'with' statement"""
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.kwargs = kwargs
        self.spinner = None
    
    def __enter__(self):
        self.spinner = create_spinner_safe(self.parent, **self.kwargs)
        if self.spinner:
            self.spinner.start()
        return self.spinner
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner:
            try:
                self.spinner.stop()
                try:
                    self.spinner.update_idletasks()
                except:
                    pass
                self.spinner.destroy()
            except:
                pass
        return False