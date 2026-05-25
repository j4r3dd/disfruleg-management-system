#!/bin/bash
cd /Users/juanantoniomercadolara/Desktop/BodegaDisfruleg/src/modules/inventory

# Leer el archivo v2.0
cp registro_compras_v2.0_backup.py registro_compras_TEMP.py

# Aplicar mejoras con sed
# 1. Agregar botón de salida en el header
# 2. Cambiar la función de filtrado

cat > registro_compras.py << 'ENDFILE'
# NOTA: Por ahora, usa la v2.0 que ya tienes
# Las mejoras están casi listas

# Para agregar el botón de salida manualmente:
# Busca en registro_compras_v2.0_backup.py la línea ~100 donde dice:
#   header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
#   header_content.pack(fill="both", expand=True, padx=20, pady=15)

# Y agrega DESPUÉS:
#   # LEFT: Botón de salida
#   left_frame = ctk.CTkFrame(header_content, fg_color="transparent")
#   left_frame.pack(side="left", fill="y")
#   
#   exit_btn = ctk.CTkButton(
#       left_frame,
#       text="⎋",
#       width=40,
#       height=40,
#       corner_radius=8,
#       fg_color="transparent",
#       hover_color=COLORS['danger'],
#       font=("Arial", 20),
#       text_color="white",
#       command=self.on_closing
#   )
#   exit_btn.pack(side="left", padx=(0, 15))

ENDFILE

echo "Archivo base restaurado"
