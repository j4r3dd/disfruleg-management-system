#!/usr/bin/env python3
"""
Ubicuo AI - Database Inspector
Analiza automáticamente la estructura de BD y el código existente
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import ast


class DatabaseInspector:
    """Inspector inteligente de bases de datos y código"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.findings = {
            'db_files': [],
            'db_connections': [],
            'table_structures': [],
            'product_models': [],
            'sql_queries': [],
            'config_files': []
        }
    
    def scan_project(self):
        """Escanea todo el proyecto buscando archivos relacionados con BD"""
        print("=" * 70)
        print("🔍 UBICUO AI - DATABASE INSPECTOR")
        print("=" * 70)
        print(f"\n📂 Escaneando proyecto en: {self.project_path.absolute()}\n")
        
        # Buscar archivos Python
        py_files = list(self.project_path.rglob("*.py"))
        print(f"📄 Encontrados {len(py_files)} archivos Python")
        
        for py_file in py_files:
            if self._is_excluded(py_file):
                continue
            
            self._analyze_python_file(py_file)
        
        # Buscar archivos de configuración
        self._find_config_files()
        
        # Buscar archivos SQL
        sql_files = list(self.project_path.rglob("*.sql"))
        print(f"📄 Encontrados {len(sql_files)} archivos SQL")
        
        for sql_file in sql_files:
            self._analyze_sql_file(sql_file)
        
        # Generar reporte
        self._generate_report()
    
    def _is_excluded(self, path: Path) -> bool:
        """Verifica si el archivo debe ser excluido"""
        exclude_patterns = ['venv', '__pycache__', '.git', 'node_modules', 'test']
        return any(pattern in str(path) for pattern in exclude_patterns)
    
    def _analyze_python_file(self, file_path: Path):
        """Analiza un archivo Python buscando código de BD"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Detectar conexiones a BD
            if self._has_db_connection(content):
                info = self._extract_db_info(content, file_path)
                if info:
                    self.findings['db_files'].append({
                        'file': str(file_path.relative_to(self.project_path)),
                        'info': info
                    })
            
            # Detectar modelos de productos
            if self._has_product_model(content):
                model_info = self._extract_product_model(content, file_path)
                if model_info:
                    self.findings['product_models'].append(model_info)
            
            # Detectar queries SQL
            queries = self._extract_sql_queries(content)
            if queries:
                self.findings['sql_queries'].extend([{
                    'file': str(file_path.relative_to(self.project_path)),
                    'query': q
                } for q in queries])
        
        except Exception as e:
            print(f"⚠️  Error leyendo {file_path}: {e}")
    
    def _has_db_connection(self, content: str) -> bool:
        """Detecta si el archivo tiene código de conexión a BD"""
        patterns = [
            r'mysql\.connector',
            r'pymysql',
            r'SQLAlchemy',
            r'create_engine',
            r'connect\(',
            r'cursor\(',
            r'\.execute\(',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _has_product_model(self, content: str) -> bool:
        """Detecta si el archivo tiene modelos de productos"""
        patterns = [
            r'class.*Product',
            r'productos',
            r'get_products',
            r'load_products',
            r'tabla.*producto',
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)
    
    def _extract_db_info(self, content: str, file_path: Path) -> Dict:
        """Extrae información de conexión a BD"""
        info = {
            'file': str(file_path.name),
            'type': 'unknown',
            'host': None,
            'database': None,
            'user': None,
            'tables': [],
            'connection_method': None
        }
        
        # Detectar tipo de conexión
        if 'mysql.connector' in content:
            info['type'] = 'mysql-connector'
            info['connection_method'] = 'mysql.connector.connect()'
        elif 'pymysql' in content:
            info['type'] = 'pymysql'
            info['connection_method'] = 'pymysql.connect()'
        elif 'SQLAlchemy' in content or 'create_engine' in content:
            info['type'] = 'sqlalchemy'
            info['connection_method'] = 'create_engine()'
        
        # Extraer host
        host_match = re.search(r'host\s*=\s*["\']([^"\']+)["\']', content)
        if host_match:
            info['host'] = host_match.group(1)
        
        # Extraer database
        db_match = re.search(r'database\s*=\s*["\']([^"\']+)["\']', content)
        if db_match:
            info['database'] = db_match.group(1)
        
        # Extraer user
        user_match = re.search(r'user\s*=\s*["\']([^"\']+)["\']', content)
        if user_match:
            info['user'] = user_match.group(1)
        
        # Buscar nombres de tablas
        table_patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'["\']([a-zA-Z_][a-zA-Z0-9_]*)["\'].*table',
        ]
        
        for pattern in table_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                table_name = match.group(1)
                if table_name not in info['tables'] and not table_name.startswith('_'):
                    info['tables'].append(table_name)
        
        return info
    
    def _extract_product_model(self, content: str, file_path: Path) -> Optional[Dict]:
        """Extrae estructura de modelos de productos"""
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if 'product' in node.name.lower() or 'producto' in node.name.lower():
                        fields = []
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name):
                                        fields.append(target.id)
                        
                        return {
                            'file': str(file_path.relative_to(self.project_path)),
                            'class_name': node.name,
                            'fields': fields
                        }
        except:
            pass
        
        return None
    
    def _extract_sql_queries(self, content: str) -> List[str]:
        """Extrae queries SQL del código"""
        queries = []
        
        # Buscar queries en strings
        patterns = [
            r'["\']SELECT\s+.*?["\']',
            r'["\']INSERT\s+.*?["\']',
            r'["\']UPDATE\s+.*?["\']',
            r'["\']CREATE\s+TABLE.*?["\']',
            r'["\']ALTER\s+TABLE.*?["\']',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                query = match.group(0).strip('"\'')
                if len(query) < 500:  # Limitar tamaño
                    queries.append(query)
        
        return queries[:10]  # Máximo 10 queries por archivo
    
    def _find_config_files(self):
        """Busca archivos de configuración"""
        patterns = ['*.yaml', '*.yml', '*.json', '*.ini', '*.conf', '.env']
        
        for pattern in patterns:
            for config_file in self.project_path.rglob(pattern):
                if self._is_excluded(config_file):
                    continue
                
                try:
                    content = config_file.read_text(encoding='utf-8')
                    if any(keyword in content.lower() for keyword in ['database', 'db', 'host', 'mysql', 'port']):
                        self.findings['config_files'].append({
                            'file': str(config_file.relative_to(self.project_path)),
                            'type': config_file.suffix[1:]
                        })
                except:
                    pass
    
    def _analyze_sql_file(self, file_path: Path):
        """Analiza archivos SQL"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Buscar CREATE TABLE
            create_tables = re.finditer(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s*\((.*?)\);',
                content,
                re.IGNORECASE | re.DOTALL
            )
            
            for match in create_tables:
                table_name = match.group(1)
                columns_text = match.group(2)
                
                # Extraer columnas
                columns = []
                for line in columns_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith(('PRIMARY', 'KEY', 'CONSTRAINT', 'INDEX')):
                        col_match = re.match(r'`?([a-zA-Z_][a-zA-Z0-9_]*)`?\s+([A-Z]+)', line)
                        if col_match:
                            columns.append({
                                'name': col_match.group(1),
                                'type': col_match.group(2)
                            })
                
                self.findings['table_structures'].append({
                    'file': str(file_path.relative_to(self.project_path)),
                    'table': table_name,
                    'columns': columns
                })
        
        except Exception as e:
            print(f"⚠️  Error analizando SQL {file_path}: {e}")
    
    def _generate_report(self):
        """Genera reporte del análisis"""
        print("\n" + "=" * 70)
        print("📊 REPORTE DE ANÁLISIS")
        print("=" * 70)
        
        # Archivos de BD encontrados
        if self.findings['db_files']:
            print("\n🗄️  ARCHIVOS DE CONEXIÓN A BASE DE DATOS:")
            print("-" * 70)
            for db_file in self.findings['db_files']:
                print(f"\n📄 {db_file['file']}")
                info = db_file['info']
                print(f"   Tipo: {info['type']}")
                print(f"   Método: {info['connection_method']}")
                if info['host']:
                    print(f"   Host: {info['host']}")
                if info['database']:
                    print(f"   Database: {info['database']}")
                if info['user']:
                    print(f"   Usuario: {info['user']}")
                if info['tables']:
                    print(f"   Tablas detectadas: {', '.join(info['tables'][:5])}")
        
        # Modelos de productos
        if self.findings['product_models']:
            print("\n📦 MODELOS DE PRODUCTOS ENCONTRADOS:")
            print("-" * 70)
            for model in self.findings['product_models']:
                print(f"\n📄 {model['file']}")
                print(f"   Clase: {model['class_name']}")
                print(f"   Campos: {', '.join(model['fields'][:10])}")
        
        # Estructuras de tablas
        if self.findings['table_structures']:
            print("\n🗂️  ESTRUCTURA DE TABLAS (de archivos SQL):")
            print("-" * 70)
            for table in self.findings['table_structures']:
                print(f"\n📄 Tabla: {table['table']}")
                print(f"   Archivo: {table['file']}")
                print(f"   Columnas:")
                for col in table['columns'][:15]:
                    print(f"      - {col['name']}: {col['type']}")
        
        # Queries SQL
        if self.findings['sql_queries']:
            print(f"\n💾 QUERIES SQL ENCONTRADAS: {len(self.findings['sql_queries'])}")
            print("-" * 70)
            for i, query_info in enumerate(self.findings['sql_queries'][:5], 1):
                print(f"\n{i}. En {query_info['file']}:")
                print(f"   {query_info['query'][:100]}...")
        
        # Archivos de configuración
        if self.findings['config_files']:
            print("\n⚙️  ARCHIVOS DE CONFIGURACIÓN:")
            print("-" * 70)
            for config in self.findings['config_files']:
                print(f"   - {config['file']} ({config['type']})")
        
        # Resumen
        print("\n" + "=" * 70)
        print("📈 RESUMEN")
        print("=" * 70)
        print(f"✓ Archivos de BD: {len(self.findings['db_files'])}")
        print(f"✓ Modelos de Productos: {len(self.findings['product_models'])}")
        print(f"✓ Tablas detectadas: {len(self.findings['table_structures'])}")
        print(f"✓ Queries SQL: {len(self.findings['sql_queries'])}")
        print(f"✓ Archivos de config: {len(self.findings['config_files'])}")
        
        # Guardar resultado
        self._save_results()
    
    def _save_results(self):
        """Guarda los resultados en JSON"""
        output_file = self.project_path / "db_inspection_results.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {output_file}")
        print("\n" + "=" * 70)
    
    def get_integration_suggestions(self):
        """Genera sugerencias para integración"""
        print("\n🔧 SUGERENCIAS PARA INTEGRACIÓN:")
        print("-" * 70)
        
        if self.findings['db_files']:
            db_file = self.findings['db_files'][0]
            print(f"\n1. Usar el archivo de conexión existente:")
            print(f"   📄 {db_file['file']}")
            print(f"   💡 Importar la conexión desde este archivo")
        
        if self.findings['table_structures']:
            table = self.findings['table_structures'][0]
            print(f"\n2. Estructura de tabla de productos detectada:")
            print(f"   📊 Tabla: {table['table']}")
            print(f"   💡 Adaptar Ubicuo AI para leer estas columnas")
        
        if self.findings['product_models']:
            model = self.findings['product_models'][0]
            print(f"\n3. Modelo de producto encontrado:")
            print(f"   📦 Clase: {model['class_name']}")
            print(f"   💡 Usar esta clase para cargar productos en Ubicuo AI")
        
        print("\n" + "=" * 70)


def main():
    """Función principal"""
    import sys
    
    # Obtener path del proyecto
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = input("\n📂 Ruta del proyecto a analizar (Enter para directorio actual): ").strip()
        if not project_path:
            project_path = "."
    
    # Crear inspector y ejecutar
    inspector = DatabaseInspector(project_path)
    inspector.scan_project()
    inspector.get_integration_suggestions()
    
    print("\n✅ Análisis completado!")
    print("📖 Revisa 'db_inspection_results.json' para más detalles\n")


if __name__ == "__main__":
    main()
    