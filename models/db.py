import sqlite3
import time

def connect_db():
    """Connect to SQLite database with timeout and WAL mode"""
    conn = sqlite3.connect("doc_sage.sqlite", timeout=30.0)
    # Enable WAL mode for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=1000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn

def init_database():
    """Initialize all database tables"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Create 'chat' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create 'sources' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_text TEXT,
            type TEXT DEFAULT "document",
            chat_id INTEGER,
            FOREIGN KEY (chat_id) REFERENCES chat(id)
        )
    """)
    
    # Create 'messages' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chat(id)
        );
    """)
    
    # Create admin_users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create sessions table
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
    
    # Initialize default chats if they don't exist
    cursor.execute("SELECT COUNT(*) FROM chat")
    if cursor.fetchone()[0] == 0:
        # Create system chat (ID=1) for knowledge base
        cursor.execute("INSERT INTO chat (id, title) VALUES (1, 'Sistema - Base de Conocimiento')")
        # Create public chat (ID=2) for customer queries
        cursor.execute("INSERT INTO chat (id, title) VALUES (2, 'Chat Público - Clientes')")
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

# CRUD Operations for 'chat' table
def create_chat(title):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat (title) VALUES (?)", (title,))
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return chat_id

def list_chats():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat ORDER BY created_at DESC")
    chats = cursor.fetchall()
    conn.close()
    return chats

def read_chat(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat WHERE id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_chat(chat_id, new_title):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE chat SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_title, chat_id),
    )
    conn.commit()
    conn.close()

def delete_chat(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

# CRUD Operations for 'sources' table
def create_source(name, source_text, chat_id, source_type="document"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sources (name, source_text, chat_id, type) VALUES (?, ?, ?, ?)",
        (name, source_text, chat_id, source_type),
    )
    conn.commit()
    conn.close()

def read_source(source_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_source(source_id, new_name, new_source_text):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sources SET name = ?, source_text = ? WHERE id = ?",
        (new_name, new_source_text, source_id),
    )
    conn.commit()
    conn.close()

def list_sources(chat_id, source_type=None):
    conn = connect_db()
    cursor = conn.cursor()
    if source_type:
        cursor.execute(
            "SELECT * FROM sources WHERE chat_id = ? AND type = ?",
            (chat_id, source_type),
        )
    else:
        cursor.execute("SELECT * FROM sources WHERE chat_id = ?", (chat_id,))
    sources = cursor.fetchall()
    conn.close()
    return sources

def delete_source(source_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()

# CRUD Operations for 'messages' table
def create_message(chat_id, sender, content):
    conn = None
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)",
                (chat_id, sender, content),
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and retry_count < max_retries - 1:
                retry_count += 1
                print(f"Database locked, retrying... ({retry_count}/{max_retries})")
                if conn:
                    conn.close()
                time.sleep(0.1 * retry_count)  # Exponential backoff
                continue
            else:
                print(f"Error creating message: {e}")
                if conn:
                    conn.rollback()
                return False
        except Exception as e:
            print(f"Error creating message: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
        break
    
    return False

def get_messages(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sender, content FROM messages WHERE chat_id = ? ORDER BY timestamp ASC",
        (chat_id,),
    )
    messages = cursor.fetchall()
    conn.close()
    return messages

def delete_messages(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()