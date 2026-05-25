"""
Resource Path Utility
Handles file paths correctly for both development and PyInstaller bundled environments
"""
import sys
import os
from pathlib import Path


def get_base_path():
    """
    Get the base path of the application.
    Works correctly in both development and PyInstaller bundled environments.

    Returns:
        Path: Base path of the application
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    else:
        # Running in normal Python environment
        # Go up from src/utils/ to project root
        return Path(__file__).parent.parent.parent


def get_resource_path(relative_path):
    """
    Get absolute path to a resource file.
    Works correctly in both development and PyInstaller bundled environments.

    Args:
        relative_path (str): Relative path from project root (e.g., 'assets/icons/logo.png')

    Returns:
        Path: Absolute path to the resource
    """
    return get_base_path() / relative_path


def get_writable_path(relative_path):
    """
    Get a writable path for logs, temp files, etc.
    When bundled and installed to Program Files, uses AppData.
    Otherwise uses directory next to executable.

    Args:
        relative_path (str): Relative path from writable directory

    Returns:
        Path: Absolute path to writable location
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        exe_dir = Path(sys.executable).parent

        # Check if installed in Program Files (read-only location)
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')

        exe_dir_str = str(exe_dir).lower()
        if program_files.lower() in exe_dir_str or program_files_x86.lower() in exe_dir_str:
            # Installed in Program Files - use AppData instead
            appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
            base_path = Path(appdata) / 'DISFRULEG'
        else:
            # Running from writable location - use next to executable
            base_path = exe_dir
    else:
        # Running in development - use project root
        base_path = get_base_path()

    full_path = base_path / relative_path

    # Create directory if it doesn't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)

    return full_path


def is_frozen():
    """
    Check if application is running as a frozen executable.

    Returns:
        bool: True if running as PyInstaller bundle, False otherwise
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


if __name__ == "__main__":
    # Test the utility
    print(f"Is frozen: {is_frozen()}")
    print(f"Base path: {get_base_path()}")
    print(f"Resource path (credentials.json): {get_resource_path('credentials.json')}")
    print(f"Writable path (logs/app.log): {get_writable_path('logs/app.log')}")
