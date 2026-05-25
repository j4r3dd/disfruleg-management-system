# -*- coding: utf-8 -*-
"""
help_button.py - BOTÓN RECTANGULAR SIMPLE Y LIMPIO
- Imagen pequeña al lado del texto
- Sin deformación
- Rápido sin freeze
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import os
import logging

logger = logging.getLogger(__name__)

class AnimatedHelpButton:
    """Botón rectangular elegante - versión simple"""
    
    def __init__(self, parent, image_path=None, bg_color='#FFA500', text_color='white'):
        """Inicializa el botón flotante"""
        self.parent = parent
        self.image_path = image_path
        self.bg_color = bg_color
        self.text_color = text_color
        self.click_callback = None
        self.popup_visible = False
        self.popup_frame = None
        self.animation_step = 0
        self.max_animation_steps = 4
        self.photo = None
        
        # ============================================================
        # BOTÓN RECTANGULAR SIMPLE CON IMAGEN
        # ============================================================
        
        # Botón rectangular redondeado - ESTILO FUTURISTA NEÓN
        self.button = ctk.CTkButton(
            parent,
            text='AYUDA',
            fg_color='#0A0E27',  # Fondo oscuro ciberpunk
            hover_color='#1a1f3a',
            text_color='#00FF41',  # Verde neón Matrix
            corner_radius=12,
            width=120,
            height=48,
            border_width=2,
            border_color='#00FF41',  # Borde verde neón
            font=('Courier New', 14, 'bold'),
            command=self._toggle_popup
        )
        self.button.place(
            relx=0.5,
            rely=0.012,
            anchor='n'
        )
        
        # Eventos
        self.button.bind('<Enter>', self._on_hover_enter)
        self.button.bind('<Leave>', self._on_hover_leave)
        
        # Detectar clicks fuera
        self.parent.bind('<Button-1>', self._on_canvas_click, add=True)
    
    def _on_hover_enter(self, event):
        """Mouse entra - mostrar popup"""
        if not self.popup_visible:
            self._show_popup()
    
    def _on_hover_leave(self, event):
        """Mouse sale"""
        pass
    
    def _toggle_popup(self):
        """Click en botón - abre el Centro de Ayuda directamente"""
        logger.info("[CHUMI] Click detectado, ejecutando callback...")
        
        if self.click_callback:
            logger.info("[CHUMI] Ejecutando callback...")
            self.click_callback()
        else:
            logger.warning("[CHUMI] No hay callback configurado")
    
    def _show_popup(self):
        """Muestra popup"""
        if self.popup_visible:
            return
        
        self.popup_visible = True
        self.animation_step = 0
        
        if self.popup_frame is None:
            self._create_popup()
        
        self._animate_in()
    
    def _hide_popup(self):
        """Oculta popup"""
        if not self.popup_visible:
            return
        
        self.popup_visible = False
        self._animate_out()
    
    def _create_popup(self):
        """Crea popup futurista neón"""
        self.popup_frame = ctk.CTkFrame(
            self.parent,
            fg_color='#0A0E27',
            corner_radius=12,
            border_width=2,
            border_color='#00FF41'
        )
        
        content = ctk.CTkFrame(self.popup_frame, fg_color='#0A0E27')
        content.pack(padx=18, pady=15)
        
        # Icono futurista
        ctk.CTkLabel(
            content,
            text='◆',
            font=('Helvetica', 32),
            text_color='#00FF41'
        ).pack(pady=(0, 8))
        
        # Título
        ctk.CTkLabel(
            content,
            text='AYUDA',
            text_color='#00FF41',
            font=('Courier New', 14, 'bold'),
            wraplength=200,
            justify='center'
        ).pack(pady=(0, 6))
        
        # Descripción futurista
        ctk.CTkLabel(
            content,
            text='Sistema de soporte\nintegrado',
            text_color='#00FFFF',
            font=('Courier New', 10),
            wraplength=200,
            justify='center'
        ).pack(pady=(0, 8))
        
        # Divisor neón
        ctk.CTkFrame(
            content,
            fg_color='#00FF41',
            height=1,
            width=160
        ).pack(pady=8, fill='x')
        
        # CTA futurista
        ctk.CTkLabel(
            content,
            text='> ACTIVAR SOPORTE',
            text_color='#00FF41',
            font=('Courier New', 9, 'bold'),
            wraplength=200,
            justify='center'
        ).pack(pady=(2, 0))
        
        # Posicionar popup
        self.popup_frame.place(
            relx=0.5,
            rely=0.025,
            anchor='w',
            x=85,
            y=3
        )
    
    def _animate_in(self):
        """Anima entrada"""
        if self.animation_step < self.max_animation_steps:
            self.animation_step += 1
            progress = self.animation_step / self.max_animation_steps
            
            if self.popup_frame and self.popup_frame.winfo_exists():
                self.popup_frame.place(
                    relx=0.5,
                    rely=0.025,
                    anchor='w',
                    x=85 + (6 * (1 - progress)),
                    y=3
                )
            
            self.parent.after(15, self._animate_in)
    
    def _animate_out(self):
        """Anima salida"""
        if self.animation_step > 0:
            self.animation_step -= 1
            progress = self.animation_step / self.max_animation_steps
            
            if self.popup_frame and self.popup_frame.winfo_exists():
                self.popup_frame.place(
                    relx=0.5,
                    rely=0.025,
                    anchor='w',
                    x=85 + (6 * (1 - progress)),
                    y=3
                )
            
            self.parent.after(15, self._animate_out)
        else:
            if self.popup_frame:
                try:
                    self.popup_frame.place_forget()
                except:
                    pass
    
    def _on_canvas_click(self, event):
        """Click fuera - cierra popup"""
        if not self.popup_visible:
            return
        
        try:
            if self.popup_frame and self.popup_frame.winfo_exists():
                px, py = self.popup_frame.winfo_x(), self.popup_frame.winfo_y()
                pw, ph = self.popup_frame.winfo_width(), self.popup_frame.winfo_height()
                
                if not (px <= event.x <= px + pw and py <= event.y <= py + ph):
                    bx, by = self.button.winfo_x(), self.button.winfo_y()
                    bw, bh = self.button.winfo_width(), self.button.winfo_height()
                    
                    if not (bx <= event.x <= bx + bw and by <= event.y <= by + bh):
                        self._hide_popup()
        except:
            pass
    
    def set_click_callback(self, callback):
        """Establece callback"""
        self.click_callback = callback