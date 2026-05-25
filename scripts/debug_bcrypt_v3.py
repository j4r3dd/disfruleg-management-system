import bcrypt

def verify_specific_hash():
    password = "12345678"
    # Hash retrieved from debug_auth.py output for user 'test'
    db_hash = "$2b$12$q45.dIfmK1ufE/Y8mCMg7.fYWXjxvaXoNHyI6y/mWJoXQCKBChIGW"
    
    print(f"Password: {password}")
    print(f"DB Hash: {db_hash}")
    
    try:
        check = bcrypt.checkpw(password.encode('utf-8'), db_hash.encode('utf-8'))
        print(f"Check result: {check}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_specific_hash()
