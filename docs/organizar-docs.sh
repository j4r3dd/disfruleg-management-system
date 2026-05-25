#!/bin/bash

# Script para organizar archivos de docs en la estructura correcta

echo "🔧 Organizando estructura de documentación..."
echo ""

cd /Users/juanantoniomercadolara/Desktop/BodegaDisfruleg/docs

# Verificar que estamos en la carpeta correcta
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: No se encontró mkdocs.yml"
    echo "Debes estar en: /Users/juanantoniomercadolara/Desktop/BodegaDisfruleg/docs"
    exit 1
fi

echo "✅ Ubicación correcta encontrada"
echo ""

# Crear carpeta source si no existe
if [ ! -d "source" ]; then
    echo "📁 Creando carpeta 'source'..."
    mkdir -p source
fi

# Mover archivos individuales a source
echo "📂 Moviendo archivos .md..."

# Archivo raíz
if [ -f "index.md" ]; then
    mv index.md source/
    echo "  ✅ index.md"
fi

# Carpetas
for dir in introduccion guias faq modulos; do
    if [ -d "$dir" ]; then
        echo "  ✅ Moviendo $dir/"
        mv "$dir" source/
    fi
done

echo ""
echo "✅ Archivos organizados en source/"
echo ""
echo "Estructura final:"
echo ""
echo "docs/"
echo "├── mkdocs.yml"
echo "└── source/"
echo "    ├── index.md"
echo "    ├── introduccion/"
echo "    ├── guias/"
echo "    ├── faq/"
echo "    └── modulos/"
echo ""
echo "Ejecuta: mkdocs serve"
echo ""

