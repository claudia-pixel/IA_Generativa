import sqlite3
import time
import os

def connect_db():
    """Connect to SQLite database with timeout and WAL mode"""
    # Obtener el directorio base del proyecto (dos niveles arriba desde src/models/)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "doc_sage.sqlite")
    conn = sqlite3.connect(db_path, timeout=30.0)
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
    
    # Create tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            estado TEXT DEFAULT 'abierto',
            prioridad TEXT DEFAULT 'normal',
            titulo TEXT NOT NULL,
            descripcion TEXT,
            cliente_email TEXT,
            cliente_nombre TEXT,
            cliente_telefono TEXT,
            producto_id TEXT,
            factura_numero TEXT,
            fecha_devolucion TEXT,
            motivo_devolucion TEXT,
            numero_seguimiento TEXT,
            guia_seguimiento TEXT,
            cantidad INTEGER DEFAULT 1,
            total DECIMAL(10, 2),
            notas TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME
        )
    """)
    
    # Create chat_memory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            memory_key TEXT NOT NULL,
            memory_value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            UNIQUE(session_id, memory_key)
        )
    """)
    
    # Create google_auth table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS google_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            google_id TEXT UNIQUE NOT NULL,
            name TEXT,
            picture_url TEXT,
            email_verified BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """)
    
    # Create otp_codes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            expires_at DATETIME NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

# CRUD Operations for 'tickets' table
def generate_ticket_number():
    """Generate a unique ticket number"""
    import uuid
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"TKT-{timestamp}-{unique_id}"

def create_ticket(
    tipo: str,
    titulo: str,
    descripcion: str = None,
    cliente_email: str = None,
    cliente_nombre: str = None,
    cliente_telefono: str = None,
    producto_id: str = None,
    factura_numero: str = None,
    cantidad: int = 1,
    total: float = None,
    prioridad: str = "normal",
    estado: str = "abierto",
    **kwargs
):
    """Create a new ticket"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Generate unique ticket number
    ticket_number = generate_ticket_number()
    
    # Prepare all fields
    fields = {
        "ticket_number": ticket_number,
        "tipo": tipo,
        "estado": estado,
        "prioridad": prioridad,
        "titulo": titulo,
        "descripcion": descripcion,
        "cliente_email": cliente_email,
        "cliente_nombre": cliente_nombre,
        "cliente_telefono": cliente_telefono,
        "producto_id": producto_id,
        "factura_numero": factura_numero,
        "cantidad": cantidad,
        "total": total,
        "fecha_devolucion": kwargs.get("fecha_devolucion"),
        "motivo_devolucion": kwargs.get("motivo_devolucion"),
        "numero_seguimiento": kwargs.get("numero_seguimiento"),
        "guia_seguimiento": kwargs.get("guia_seguimiento"),
        "notas": kwargs.get("notas")
    }
    
    # Filter out None values and build query
    filtered_fields = {k: v for k, v in fields.items() if v is not None}
    columns = ", ".join(filtered_fields.keys())
    placeholders = ", ".join(["?"] * len(filtered_fields))
    values = tuple(filtered_fields.values())
    
    cursor.execute(f"INSERT INTO tickets ({columns}) VALUES ({placeholders})", values)
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"id": ticket_id, "ticket_number": ticket_number}

def get_ticket(ticket_number):
    """Get a ticket by ticket number"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_number = ?", (ticket_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result))
    return None

def get_ticket_by_id(ticket_id):
    """Get a ticket by ID"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, result))
    return None

def list_tickets(tipo=None, estado=None, cliente_email=None):
    """List tickets with optional filters"""
    conn = connect_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tickets WHERE 1=1"
    params = []
    
    if tipo:
        query += " AND tipo = ?"
        params.append(tipo)
    
    if estado:
        query += " AND estado = ?"
        params.append(estado)
    
    if cliente_email:
        query += " AND cliente_email = ?"
        params.append(cliente_email)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, tuple(params))
    results = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in results]

def update_ticket(ticket_number, **kwargs):
    """Update a ticket"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Filter valid fields
    valid_fields = [
        "tipo", "estado", "prioridad", "titulo", "descripcion",
        "cliente_email", "cliente_nombre", "cliente_telefono",
        "producto_id", "factura_numero", "cantidad", "total",
        "fecha_devolucion", "motivo_devolucion", "numero_seguimiento",
        "guia_seguimiento", "notas", "resolved_at"
    ]
    
    filtered_updates = {k: v for k, v in kwargs.items() if k in valid_fields and v is not None}
    
    if not filtered_updates:
        conn.close()
        return False
    
    # Add updated_at
    filtered_updates["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    set_clause = ", ".join([f"{k} = ?" for k in filtered_updates.keys()])
    values = list(filtered_updates.values()) + [ticket_number]
    
    cursor.execute(f"UPDATE tickets SET {set_clause} WHERE ticket_number = ?", values)
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_ticket(ticket_number):
    """Delete a ticket"""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE ticket_number = ?", (ticket_number,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# CRUD Operations for 'chat_memory' table
def store_memory(session_id: str, memory_key: str, memory_value: str, ttl_minutes: int = 5) -> bool:
    """
    Store a memory with TTL
    
    Args:
        session_id: Session identifier
        memory_key: Key for the memory
        memory_value: Value to store
        ttl_minutes: Time to live in minutes (default: 5)
        
    Returns:
        bool: True if successful
    """
    from datetime import datetime, timedelta
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Calculate expiration time
    expires_at = datetime.now() + timedelta(minutes=ttl_minutes)
    
    try:
        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute("""
            INSERT OR REPLACE INTO chat_memory (session_id, memory_key, memory_value, expires_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, memory_key, memory_value, expires_at.isoformat()))
        
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error storing memory: {e}")
        conn.rollback()
        success = False
    finally:
        conn.close()
    
    return success

def get_memory(session_id: str, memory_key: str = None) -> dict:
    """
    Retrieve memory(ies) for a session
    
    Args:
        session_id: Session identifier
        memory_key: Specific key to retrieve (optional)
        
    Returns:
        dict: Memory value(s)
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # First, clean up expired memories
        cursor.execute("DELETE FROM chat_memory WHERE expires_at < datetime('now')")
        
        # Retrieve memories
        if memory_key:
            cursor.execute("""
                SELECT memory_key, memory_value 
                FROM chat_memory 
                WHERE session_id = ? AND memory_key = ? AND expires_at >= datetime('now')
            """, (session_id, memory_key))
        else:
            cursor.execute("""
                SELECT memory_key, memory_value 
                FROM chat_memory 
                WHERE session_id = ? AND expires_at >= datetime('now')
            """, (session_id,))
        
        rows = cursor.fetchall()
        
        # If specific key requested, return just the value
        if memory_key and rows:
            return rows[0][1]  # memory_value
        
        # Otherwise return all as dict
        memories = {row[0]: row[1] for row in rows}
        
        conn.commit()
        return memories
        
    except Exception as e:
        print(f"Error retrieving memory: {e}")
        return {}
    finally:
        conn.close()

def delete_memory(session_id: str, memory_key: str = None) -> bool:
    """
    Delete memory(ies) for a session
    
    Args:
        session_id: Session identifier
        memory_key: Specific key to delete (optional, if None deletes all)
        
    Returns:
        bool: True if successful
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        if memory_key:
            cursor.execute("DELETE FROM chat_memory WHERE session_id = ? AND memory_key = ?", 
                         (session_id, memory_key))
        else:
            cursor.execute("DELETE FROM chat_memory WHERE session_id = ?", (session_id,))
        
        conn.commit()
        deleted = cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting memory: {e}")
        conn.rollback()
        deleted = False
    finally:
        conn.close()
    
    return deleted

def cleanup_expired_memories():
    """Remove expired memories from the database"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM chat_memory WHERE expires_at < datetime('now')")
        conn.commit()
        deleted = cursor.rowcount
        return deleted
    except Exception as e:
        print(f"Error cleaning up memories: {e}")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()