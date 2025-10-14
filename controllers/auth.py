import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from models.db import connect_db

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_table():
    """Create admin users table"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        conn = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES admin_users(id)
                )
            """)
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and retry_count < max_retries - 1:
                retry_count += 1
                print(f"Database locked in create_admin_table, retrying... ({retry_count}/{max_retries})")
                if conn:
                    conn.close()
                time.sleep(0.1 * retry_count)  # Exponential backoff
                continue
            else:
                print(f"Error creating admin table: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error creating admin table: {e}")
            return False
        finally:
            if conn:
                conn.close()
        break
    
    return False

def create_admin_user(username: str, password: str, email: str = None) -> bool:
    """Create a new admin user"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        conn = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO admin_users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # User already exists
            return False
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and retry_count < max_retries - 1:
                retry_count += 1
                print(f"Database locked in create_admin_user, retrying... ({retry_count}/{max_retries})")
                if conn:
                    conn.close()
                time.sleep(0.1 * retry_count)  # Exponential backoff
                continue
            else:
                print(f"Error creating admin user: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error creating admin user: {e}")
            return False
        finally:
            if conn:
                conn.close()
        break
    
    return False

def verify_admin(username: str, password: str) -> dict:
    """Verify admin credentials and return user info"""
    conn = connect_db()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    
    cursor.execute(
        "SELECT id, username, email FROM admin_users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2]
        }
    return None

def create_session(user_id: int) -> str:
    """Create a session token for authenticated user"""
    conn = connect_db()
    cursor = conn.cursor()
    
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    cursor.execute(
        "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (?, ?, ?)",
        (user_id, session_token, expires_at)
    )
    conn.commit()
    conn.close()
    
    return session_token

def verify_session(session_token: str) -> dict:
    """Verify if session is valid and return user info"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.user_id, a.username, a.email, s.expires_at
        FROM sessions s
        JOIN admin_users a ON s.user_id = a.id
        WHERE s.session_token = ?
    """, (session_token,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        expires_at = datetime.fromisoformat(result[3])
        if expires_at > datetime.now():
            return {
                "id": result[0],
                "username": result[1],
                "email": result[2]
            }
    return None

def logout_session(session_token: str):
    """Delete a session (logout)"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
    conn.commit()
    conn.close()

def cleanup_expired_sessions():
    """Remove expired sessions"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE expires_at < ?", (datetime.now(),))
    conn.commit()
    conn.close()