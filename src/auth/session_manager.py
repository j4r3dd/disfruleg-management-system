import tkinter as tk
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable
import threading

class SessionManager:
    def __init__(self, timeout_minutes: int = 30):
        self.timeout_minutes = timeout_minutes
        self.current_user = None
        self.login_time = None
        self.last_activity = None
        self.session_callbacks = []
        self.timeout_timer = None
        self.session_active = False
        
    def start_session(self, user_data: Dict[str, Any]):
        self.current_user = user_data
        self.login_time = datetime.now()
        self.last_activity = datetime.now()
        self.session_active = True
        self._start_timeout_timer()
        self._notify_callbacks('session_started', user_data)
    
    def end_session(self):
        if self.session_active:
            user_data = self.current_user
            self.current_user = None
            self.login_time = None
            self.last_activity = None
            self.session_active = False
            if self.timeout_timer:
                self.timeout_timer.cancel()
                self.timeout_timer = None
            self._notify_callbacks('session_ended', user_data)
    
    def update_activity(self):
        if self.session_active:
            self.last_activity = datetime.now()
            self._start_timeout_timer()
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        return self.current_user if self.session_active else None
    
    def is_active(self) -> bool:
        return self.session_active and self.current_user is not None
    
    def get_session_duration(self) -> Optional[timedelta]:
        if self.login_time:
            return datetime.now() - self.login_time
        return None
    
    def get_time_until_timeout(self) -> Optional[timedelta]:
        if not self.session_active or not self.last_activity:
            return None
        timeout_time = self.last_activity + timedelta(minutes=self.timeout_minutes)
        remaining = timeout_time - datetime.now()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)
    
    def add_callback(self, callback: Callable):
        self.session_callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        if callback in self.session_callbacks:
            self.session_callbacks.remove(callback)
    
    def _notify_callbacks(self, event_type: str, user_data: Dict[str, Any]):
        for callback in self.session_callbacks:
            try:
                callback(event_type, user_data)
            except Exception as e:
                print(f"Error in session callback: {e}")
    
    def _start_timeout_timer(self):
        if self.timeout_timer:
            self.timeout_timer.cancel()
        timeout_seconds = self.timeout_minutes * 60
        self.timeout_timer = threading.Timer(timeout_seconds, self._handle_timeout)
        self.timeout_timer.daemon = True
        self.timeout_timer.start()
    
    def _handle_timeout(self):
        if self.session_active:
            user_data = self.current_user
            self.end_session()
            self._notify_callbacks('session_timeout', user_data)

session_manager = SessionManager()

class SessionAwareWidget:
    def __init__(self):
        self.session_callback_registered = False
        
    def register_session_callback(self):
        if not self.session_callback_registered:
            session_manager.add_callback(self._handle_session_event)
            self.session_callback_registered = True
    
    def unregister_session_callback(self):
        if self.session_callback_registered:
            session_manager.remove_callback(self._handle_session_event)
            self.session_callback_registered = False
    
    def _handle_session_event(self, event_type: str, user_data: dict):
        pass
    
    def update_session_activity(self):
        session_manager.update_activity()

class SessionStatusBar(tk.Frame, SessionAwareWidget):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, relief=tk.SUNKEN, bd=1)
        SessionAwareWidget.__init__(self)
        
        self._destroyed = False
        self._update_after_id = None
        
        self.user_var = tk.StringVar()
        self.time_var = tk.StringVar()
        
        self.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.user_label = tk.Label(self, textvariable=self.user_var, anchor=tk.W)
        self.user_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = tk.Label(self, textvariable=self.time_var, anchor=tk.E)
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        self.register_session_callback()
        self._update_display()
        self._start_update_timer()
    
    def _handle_session_event(self, event_type: str, user_data: dict):
        if event_type in ['session_started', 'session_ended', 'session_timeout']:
            self._update_display()
    
    def _safe_exists(self):
        try:
            return not self._destroyed and self.winfo_exists()
        except:
            return False
    
    def _update_display(self):
        if not self._safe_exists():
            return
        
        try:
            user = session_manager.get_current_user()
            
            if user:
                self.user_var.set(f"Usuario: {user['nombre_completo']} ({user['rol']})")
                time_remaining = session_manager.get_time_until_timeout()
                if time_remaining:
                    minutes = int(time_remaining.total_seconds() / 60)
                    self.time_var.set(f"Sesión expira en {minutes} min")
                else:
                    self.time_var.set("Sesión expirada")
            else:
                self.user_var.set("No hay usuario autenticado")
                self.time_var.set("")
        except:
            pass
    
    def _start_update_timer(self):
        if self._update_after_id is not None:
            try:
                if self._safe_exists():
                    self.after_cancel(self._update_after_id)
            except:
                pass
            self._update_after_id = None
        
        if not self._safe_exists():
            return
        
        try:
            self._update_display()
            if self._safe_exists():
                self._update_after_id = self.after(60000, self._start_update_timer)
        except Exception as e:
            print(f"[SessionStatusBar] Error en update timer: {e}")
            self._update_after_id = None
    
    def destroy(self):
        if hasattr(self, '_destroyed') and self._destroyed:
            return
        
        self._destroyed = True
        
        if self._update_after_id is not None:
            try:
                if self.winfo_exists():
                    self.after_cancel(self._update_after_id)
            except:
                pass
            self._update_after_id = None
        
        try:
            self.unregister_session_callback()
        except:
            pass
        
        try:
            super().destroy()
        except:
            pass

def require_authentication(func):
    def wrapper(*args, **kwargs):
        if not session_manager.is_active():
            raise Exception("Función requiere autenticación. Por favor, inicie sesión.")
        session_manager.update_activity()
        return func(*args, **kwargs)
    return wrapper

def get_current_user():
    return session_manager.get_current_user()

def is_authenticated():
    return session_manager.is_active()

def logout():
    session_manager.end_session()
