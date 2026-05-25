import sys
import os
import bcrypt

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.auth.auth_manager import AuthManager
from src.database.conexion import get_pooled_connection

def debug_admins():
    print("--- DEBUGGING ADMINS ---")
    try:
        with get_pooled_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, rol, activo, password_hash FROM usuarios_sistema WHERE rol = 'admin'")
            admins = cursor.fetchall()
            print(f"Raw admins: {admins}")
            
            for row in admins:
                # Handle potential different row formats (tuple vs dict)
                if isinstance(row, dict):
                    username = row['username']
                    activo = row['activo']
                    pw_hash = row['password_hash']
                else:
                    username = row[0]
                    activo = row[2]
                    pw_hash = row[3]
                
                print(f"Admin: {username}, Active: {activo}")
                print(f"  Hash type: {type(pw_hash)}")
                print(f"  Hash value: {pw_hash!r}")
                
                if pw_hash and isinstance(pw_hash, str):
                    print(f"  Hash is str, len: {len(pw_hash)}")
                elif pw_hash and isinstance(pw_hash, bytes):
                    print(f"  Hash is bytes, len: {len(pw_hash)}")

    except Exception as e:
        print(f"Error querying DB: {e}")
        import traceback
        traceback.print_exc()

def test_verify(password):
    print(f"\n--- TESTING PASSWORD VERIFICATION: '{password}' ---")
    auth = AuthManager()
    try:
        result = auth.verify_admin_password(password)
        print(f"AuthManager.verify_admin_password result: {result}")
    except Exception as e:
        print(f"Error in verify_admin_password: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_admins()
    if len(sys.argv) > 1:
        test_verify(sys.argv[1])
