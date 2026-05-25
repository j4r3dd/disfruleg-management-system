"""
Ubicuo AI - Sistema de Aprendizaje
Motor que aprende de las correcciones del usuario
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import shutil
import yaml


@dataclass
class LearningEntry:
    """Entrada en el diccionario de aprendizaje"""
    incorrect: str
    correct: str
    times_used: int
    first_added: str
    last_used: str
    confidence_boost: float = 0.05
    
    def to_dict(self) -> dict:
        return asdict(self)


class UbicuoLearning:
    """Sistema de aprendizaje automático basado en correcciones"""
    
    def __init__(self, config_path: str = "config/configuracion.yaml"):
        """
        Inicializa el sistema de aprendizaje
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.dict_path = self.config.get('learning', {}).get('dictionary_file', 'learning_dict.json')
        self.dictionary: Dict[str, LearningEntry] = {}
        self.auto_save = self.config.get('learning', {}).get('auto_save', True)
        self.changes_since_save = 0
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.dict_path) if os.path.dirname(self.dict_path) else '.', exist_ok=True)
        
        # Cargar diccionario existente
        self.load()
    
    def _load_config(self, config_path: str) -> dict:
        """Carga configuración desde YAML"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {
                'learning': {
                    'dictionary_file': 'learning_dict.json',
                    'auto_save': True,
                    'backup': {
                        'enabled': True,
                        'max_backups': 7
                    }
                }
            }
    
    def load(self) -> bool:
        """
        Carga el diccionario desde disco
        
        Returns:
            True si se cargó exitosamente, False si no existe o hay error
        """
        if not os.path.exists(self.dict_path):
            return False
        
        try:
            with open(self.dict_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convertir a LearningEntry objects
            self.dictionary = {}
            for incorrect, entry_data in data.items():
                self.dictionary[incorrect.lower()] = LearningEntry(
                    incorrect=entry_data['incorrect'],
                    correct=entry_data['correct'],
                    times_used=entry_data.get('times_used', 1),
                    first_added=entry_data.get('first_added', datetime.now().isoformat()),
                    last_used=entry_data.get('last_used', datetime.now().isoformat()),
                    confidence_boost=entry_data.get('confidence_boost', 0.05)
                )
            
            return True
            
        except Exception as e:
            print(f"Error cargando diccionario: {e}")
            return False
    
    def save(self, force: bool = False) -> bool:
        """
        Guarda el diccionario a disco
        
        Args:
            force: Forzar guardado incluso sin cambios
            
        Returns:
            True si se guardó exitosamente
        """
        if not force and self.changes_since_save == 0:
            return True
        
        try:
            # Crear backup si está habilitado
            if self.config.get('learning', {}).get('backup', {}).get('enabled', True):
                self._create_backup()
            
            # Convertir a formato serializable
            data = {
                incorrect: entry.to_dict()
                for incorrect, entry in self.dictionary.items()
            }
            
            # Guardar
            with open(self.dict_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.changes_since_save = 0
            return True
            
        except Exception as e:
            print(f"Error guardando diccionario: {e}")
            return False
    
    def _create_backup(self) -> None:
        """Crea un backup del diccionario actual"""
        if not os.path.exists(self.dict_path):
            return
        
        backup_config = self.config.get('learning', {}).get('backup', {})
        backup_dir = backup_config.get('path', 'backups/learning_dict')
        max_backups = backup_config.get('max_backups', 7)
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # Crear nombre de backup con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'learning_dict_{timestamp}.json')
        
        try:
            shutil.copy2(self.dict_path, backup_path)
            
            # Limpiar backups antiguos
            self._cleanup_old_backups(backup_dir, max_backups)
            
        except Exception as e:
            print(f"Error creando backup: {e}")
    
    def _cleanup_old_backups(self, backup_dir: str, max_backups: int) -> None:
        """Elimina backups antiguos si exceden el límite"""
        try:
            backups = [
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if f.startswith('learning_dict_') and f.endswith('.json')
            ]
            
            # Ordenar por fecha de modificación
            backups.sort(key=os.path.getmtime, reverse=True)
            
            # Eliminar los más antiguos
            for backup in backups[max_backups:]:
                os.remove(backup)
                
        except Exception as e:
            print(f"Error limpiando backups: {e}")
    
    def add_correction(self, incorrect: str, correct: str) -> bool:
        """
        Agrega o actualiza una corrección en el diccionario
        
        Args:
            incorrect: Texto incorrecto que escribió el usuario
            correct: Nombre correcto del producto
            
        Returns:
            True si se agregó/actualizó correctamente
        """
        incorrect_lower = incorrect.strip().lower()
        correct_lower = correct.strip().lower()
        
        # No agregar si son iguales
        if incorrect_lower == correct_lower:
            return False
        
        now = datetime.now().isoformat()
        
        if incorrect_lower in self.dictionary:
            # Actualizar entrada existente
            entry = self.dictionary[incorrect_lower]
            entry.correct = correct  # Actualizar corrección (por si cambió)
            entry.times_used += 1
            entry.last_used = now
        else:
            # Crear nueva entrada
            self.dictionary[incorrect_lower] = LearningEntry(
                incorrect=incorrect,
                correct=correct,
                times_used=1,
                first_added=now,
                last_used=now
            )
        
        self.changes_since_save += 1
        
        # Auto-guardar si está habilitado
        if self.auto_save and self.changes_since_save >= 5:
            self.save()
        
        return True
    
    def get_correction(self, incorrect: str) -> Optional[str]:
        """
        Obtiene la corrección para un texto incorrecto
        
        Args:
            incorrect: Texto a corregir
            
        Returns:
            Texto corregido o None si no existe
        """
        entry = self.dictionary.get(incorrect.strip().lower())
        if entry:
            # Actualizar uso
            entry.times_used += 1
            entry.last_used = datetime.now().isoformat()
            self.changes_since_save += 1
            
            if self.auto_save and self.changes_since_save >= 10:
                self.save()
            
            return entry.correct
        return None
    
    def get_all_corrections(self) -> Dict[str, str]:
        """
        Obtiene todas las correcciones como dict simple
        
        Returns:
            Dict {incorrect: correct}
        """
        return {
            incorrect: entry.correct
            for incorrect, entry in self.dictionary.items()
        }
    
    def remove_correction(self, incorrect: str) -> bool:
        """
        Elimina una corrección del diccionario
        
        Args:
            incorrect: Texto incorrecto a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        incorrect_lower = incorrect.strip().lower()
        
        if incorrect_lower in self.dictionary:
            del self.dictionary[incorrect_lower]
            self.changes_since_save += 1
            
            if self.auto_save:
                self.save()
            
            return True
        
        return False
    
    def get_statistics(self) -> dict:
        """Obtiene estadísticas del sistema de aprendizaje"""
        if not self.dictionary:
            return {
                'total_entries': 0,
                'total_uses': 0,
                'avg_uses_per_entry': 0,
                'most_used': None,
                'recent_additions': []
            }
        
        total_uses = sum(entry.times_used for entry in self.dictionary.values())
        avg_uses = total_uses / len(self.dictionary)
        
        # Entrada más usada
        most_used = max(
            self.dictionary.items(),
            key=lambda x: x[1].times_used
        )
        
        # Adiciones recientes (últimas 5)
        recent = sorted(
            self.dictionary.values(),
            key=lambda x: x.first_added,
            reverse=True
        )[:5]
        
        return {
            'total_entries': len(self.dictionary),
            'total_uses': total_uses,
            'avg_uses_per_entry': round(avg_uses, 2),
            'most_used': {
                'incorrect': most_used[1].incorrect,
                'correct': most_used[1].correct,
                'times_used': most_used[1].times_used
            },
            'recent_additions': [
                {
                    'incorrect': entry.incorrect,
                    'correct': entry.correct,
                    'added': entry.first_added
                }
                for entry in recent
            ]
        }
    
    def export_to_file(self, output_path: str, format: str = 'json') -> bool:
        """
        Exporta el diccionario a un archivo
        
        Args:
            output_path: Ruta del archivo de salida
            format: Formato ('json', 'csv', 'txt')
            
        Returns:
            True si se exportó correctamente
        """
        try:
            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    data = {
                        incorrect: entry.to_dict()
                        for incorrect, entry in self.dictionary.items()
                    }
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            elif format == 'csv':
                import csv
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Incorrecto', 'Correcto', 'Usos', 'Primera Vez', 'Último Uso'])
                    for entry in self.dictionary.values():
                        writer.writerow([
                            entry.incorrect,
                            entry.correct,
                            entry.times_used,
                            entry.first_added,
                            entry.last_used
                        ])
            
            elif format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    for entry in sorted(self.dictionary.values(), key=lambda x: x.times_used, reverse=True):
                        f.write(f"{entry.incorrect} → {entry.correct} (usado {entry.times_used} veces)\n")
            
            return True
            
        except Exception as e:
            print(f"Error exportando: {e}")
            return False
    
    def cleanup_old_entries(self, max_age_days: int = 180, min_usage: int = 1) -> int:
        """
        Limpia entradas antiguas poco usadas
        
        Args:
            max_age_days: Máximo de días de antigüedad
            min_usage: Mínimo de usos requeridos
            
        Returns:
            Número de entradas eliminadas
        """
        from datetime import timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()
        
        to_remove = []
        for incorrect, entry in self.dictionary.items():
            if entry.last_used < cutoff_date and entry.times_used < min_usage:
                to_remove.append(incorrect)
        
        for incorrect in to_remove:
            del self.dictionary[incorrect]
        
        if to_remove:
            self.changes_since_save += len(to_remove)
            if self.auto_save:
                self.save()
        
        return len(to_remove)


# Ejemplo de uso
if __name__ == "__main__":
    print("=" * 60)
    print("UBICUO AI - SISTEMA DE APRENDIZAJE")
    print("=" * 60)
    
    # Inicializar
    learning = UbicuoLearning()
    
    # Agregar correcciones de ejemplo
    corrections = [
        ('aguacte', 'Aguacate'),
        ('chile cerrano', 'Chile Serrano'),
        ('jitomat', 'Jitomate'),
        ('limom', 'Limón'),
        ('papa cambay', 'Papa Cambray'),
    ]
    
    print("\n📝 Agregando correcciones...")
    for incorrect, correct in corrections:
        learning.add_correction(incorrect, correct)
        print(f"  ✓ {incorrect} → {correct}")
    
    # Guardar
    learning.save(force=True)
    print("\n Diccionario guardado")
    
    # Estadísticas
    stats = learning.get_statistics()
    print(f"\n ESTADÍSTICAS")
    print(f"  • Total de entradas: {stats['total_entries']}")
    print(f"  • Usos totales: {stats['total_uses']}")
    print(f"  • Promedio de usos: {stats['avg_uses_per_entry']}")
    
    # Probar correcciones
    print(f"\n🔍 PRUEBAS DE CORRECCIÓN")
    test_words = ['aguacte', 'jitomat', 'palabra_no_existe']
    for word in test_words:
        correction = learning.get_correction(word)
        if correction:
            print(f"  ✓ '{word}' → '{correction}'")
        else:
            print(f"  ✗ '{word}' → No hay corrección")
    
    # Exportar
    print(f"\nExportando a TXT...")
    learning.export_to_file('learning_export.txt', 'txt')
    print("  ✓ Exportado a learning_export.txt")