import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Crear tabla de usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # Crear tabla de registros de asistencia
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        check_in TIMESTAMP,
        check_out TIMESTAMP,
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Verificar si existe usuario admin, si no, crearlo
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, full_name, is_admin) VALUES (?, ?, ?, ?)",
                 ('admin', generate_password_hash('admin123'), 'Administrador', 1))
    
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    
    conn.close()
    return user

def add_user(username, password, full_name, is_admin=0):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO users (username, password, full_name, is_admin) VALUES (?, ?, ?, ?)",
                 (username, generate_password_hash(password), full_name, is_admin))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    
    conn.close()
    return success

def update_user(user_id, username=None, password=None, full_name=None, is_admin=None):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Obtener datos actuales del usuario
    c.execute("SELECT username, full_name, is_admin FROM users WHERE id = ?", (user_id,))
    current_user = c.fetchone()
    
    if not current_user:
        conn.close()
        return False, "Usuario no encontrado"
    
    # Usar valores actuales si no se proporcionan nuevos
    username = username if username is not None else current_user[0]
    full_name = full_name if full_name is not None else current_user[1]
    is_admin = is_admin if is_admin is not None else current_user[2]
    
    try:
        if password:
            # Si se proporcionó una nueva contraseña, actualizar todo incluyendo la contraseña
            c.execute("""
                UPDATE users 
                SET username = ?, password = ?, full_name = ?, is_admin = ? 
                WHERE id = ?
            """, (username, generate_password_hash(password), full_name, is_admin, user_id))
        else:
            # Si no hay nueva contraseña, actualizar todo excepto la contraseña
            c.execute("""
                UPDATE users 
                SET username = ?, full_name = ?, is_admin = ? 
                WHERE id = ?
            """, (username, full_name, is_admin, user_id))
        
        conn.commit()
        conn.close()
        return True, "Usuario actualizado correctamente"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El nombre de usuario ya existe"

def delete_user(user_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Verificar si el usuario existe
    c.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not c.fetchone():
        conn.close()
        return False, "Usuario no encontrado"
    
    # Verificar si el usuario tiene registros de asistencia
    c.execute("SELECT id FROM attendance WHERE user_id = ? LIMIT 1", (user_id,))
    if c.fetchone():
        # Opción 1: Impedir borrar usuarios con registros
        # conn.close()
        # return False, "No se puede eliminar el usuario porque tiene registros de asistencia"
        
        # Opción 2: Eliminar también los registros de asistencia (cascada)
        c.execute("DELETE FROM attendance WHERE user_id = ?", (user_id,))
    
    # Eliminar el usuario
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, "Usuario eliminado correctamente"

def check_in(user_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Verificar si ya hay un registro de entrada sin salida
    c.execute("SELECT id FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
    if c.fetchone():
        conn.close()
        return False, "Ya tienes una entrada registrada sin marcar salida"
    
    now = datetime.datetime.now()
    c.execute("INSERT INTO attendance (user_id, check_in) VALUES (?, ?)",
             (user_id, now))
    conn.commit()
    
    # Obtener el ID del registro recién creado
    c.execute("SELECT last_insert_rowid()")
    attendance_id = c.fetchone()[0]
    
    conn.close()
    return True, attendance_id

def check_out(user_id, description=""):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Buscar registro de entrada sin salida
    c.execute("SELECT id FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
    record = c.fetchone()
    
    if not record:
        conn.close()
        return False, "No hay registro de entrada pendiente"
    
    now = datetime.datetime.now()
    c.execute("UPDATE attendance SET check_out = ?, description = ? WHERE id = ?",
             (now, description, record[0]))
    conn.commit()
    conn.close()
    return True, "Salida registrada correctamente"

def get_users():
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Eliminar el filtro de is_admin para incluir todos los usuarios '...WHERE is_admin = 0'
    c.execute("SELECT id, username, full_name, is_admin FROM users")
    users = c.fetchall()
    
    conn.close()
    return users

def get_attendance_records(user_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    query = """
    SELECT a.id, a.check_in, a.check_out, a.description, u.full_name, u.username
    FROM attendance a
    JOIN users u ON a.user_id = u.id
    WHERE 1=1
    """
    params = []
    
    if user_id:
        query += " AND a.user_id = ?"
        params.append(user_id)
    
    if start_date:
        query += " AND date(a.check_in) >= date(?)"
        params.append(start_date)
    
    if end_date:
        query += " AND date(a.check_in) <= date(?)"
        params.append(end_date)
    
    query += " ORDER BY a.check_in DESC"
    
    c.execute(query, params)
    records = c.fetchall()
    
    conn.close()
    return records

def get_pending_checkout(user_id):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT id FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))
    record = c.fetchone()
    
    conn.close()
    return record['id'] if record else None