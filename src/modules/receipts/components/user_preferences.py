"""
User Preferences Manager
Handles saving and loading user preferences like export paths
"""

import os
import json
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

# Get the user's documents folder or home directory
def get_default_documents_folder():
    """Get the user's Documents folder"""
    if os.name == 'nt':  # Windows
        # Try to get Documents folder
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
            documents_path = winreg.QueryValueEx(key, 'Personal')[0]
            winreg.CloseKey(key)
            return documents_path
        except:
            # Fallback to user home
            return str(Path.home() / 'Documents')
    else:  # Linux, Mac
        return str(Path.home() / 'Documents')

# Path to preferences file
PREFERENCES_DIR = Path.home() / '.disfruleg'
PREFERENCES_FILE = PREFERENCES_DIR / 'preferences.json'

class UserPreferences:
    """Manages user preferences for the application"""

    def __init__(self):
        self.preferences = self._load_preferences()

    def _load_preferences(self):
        """Load preferences from file or create default"""
        # Create preferences directory if it doesn't exist
        PREFERENCES_DIR.mkdir(parents=True, exist_ok=True)

        if PREFERENCES_FILE.exists():
            try:
                with open(PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading preferences: {e}")
                return self._get_default_preferences()
        else:
            return self._get_default_preferences()

    def _get_default_preferences(self):
        """Get default preferences"""
        default_base_path = Path(get_default_documents_folder()) / 'Disfruleg'

        return {
            'export_paths': {
                'pdf': None,  # Will be set on first export
                'excel': None  # Will be set on first export
            },
            'last_export_base_path': str(default_base_path)
        }

    def _save_preferences(self):
        """Save preferences to file"""
        try:
            with open(PREFERENCES_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False

    def get_export_path(self, export_type='pdf'):
        """
        Get export path for specified type (pdf or excel)

        Args:
            export_type: 'pdf' or 'excel'

        Returns:
            Path string or None if not configured
        """
        return self.preferences['export_paths'].get(export_type)

    def set_export_path(self, export_type, path):
        """
        Set export path for specified type

        Args:
            export_type: 'pdf' or 'excel'
            path: Directory path as string

        Returns:
            bool: True if saved successfully
        """
        self.preferences['export_paths'][export_type] = str(path)
        return self._save_preferences()

    def get_last_export_base_path(self):
        """Get the last used export base path"""
        return self.preferences.get('last_export_base_path', get_default_documents_folder())

    def set_last_export_base_path(self, path):
        """Set the last used export base path"""
        self.preferences['last_export_base_path'] = str(path)
        self._save_preferences()

    def prompt_for_export_path(self, export_type='pdf', parent=None):
        """
        Prompt user to select export directory

        Args:
            export_type: 'pdf' or 'excel'
            parent: Parent window for dialog

        Returns:
            Selected path or None if cancelled
        """
        # Create a temporary root window if no parent provided
        if parent is None:
            root = tk.Tk()
            root.withdraw()
            use_temp_root = True
        else:
            use_temp_root = False

        # Get initial directory
        initial_dir = self.get_last_export_base_path()

        # Show folder selection dialog
        title = f"Seleccionar carpeta para guardar {export_type.upper()}"
        selected_path = filedialog.askdirectory(
            parent=parent,
            title=title,
            initialdir=initial_dir,
            mustexist=False
        )

        # Cleanup temp root if created
        if use_temp_root:
            root.destroy()

        if selected_path:
            # Save the selected path
            self.set_export_path(export_type, selected_path)
            self.set_last_export_base_path(os.path.dirname(selected_path))

            # Create directory if it doesn't exist
            Path(selected_path).mkdir(parents=True, exist_ok=True)

            print(f"✅ Ruta de {export_type} configurada: {selected_path}")
            return selected_path

        return None

    def get_or_prompt_export_path(self, export_type='pdf', parent=None):
        """
        Get export path, prompting user if not configured

        Args:
            export_type: 'pdf' or 'excel'
            parent: Parent window for dialog

        Returns:
            Export path or None if cancelled
        """
        # Check if path is already configured
        path = self.get_export_path(export_type)

        if path and os.path.exists(path):
            return path

        # Path not configured or doesn't exist, prompt user
        return self.prompt_for_export_path(export_type, parent)

    def reset_export_paths(self):
        """Reset all export paths (will prompt again on next export)"""
        self.preferences['export_paths']['pdf'] = None
        self.preferences['export_paths']['excel'] = None
        self._save_preferences()
        print("✅ Rutas de exportación reiniciadas")


# Singleton instance
_preferences_instance = None

def get_preferences():
    """Get singleton instance of UserPreferences"""
    global _preferences_instance
    if _preferences_instance is None:
        _preferences_instance = UserPreferences()
    return _preferences_instance
