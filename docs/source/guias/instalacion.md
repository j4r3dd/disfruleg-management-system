# 💻 Instalación de CHUMI

## Requisitos Previos

✅ Python 3.8+  
✅ MySQL 8.0+ o PostgreSQL  
✅ Git  
✅ 500 MB disco libre  

## Instalación Rápida (10 min)

### Paso 1: Clonar Repositorio
```bash
git clone https://github.com/Ubicuo22/di_senos.git
cd BodegaDisfruleg
```

### Paso 2: Crear Entorno Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos
```bash
mysql -u root -p < database/schema.sql
```

### Paso 5: Crear .env
```bash
cp .env.example .env
# Editar con tus datos
```

### Paso 6: Ejecutar
```bash
python main.py
```

**¡Listo! CHUMI está corriendo**

**Siguiente:** [Configuración](configuracion.md)
