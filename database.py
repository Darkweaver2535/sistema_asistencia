import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Tabla de usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # Tabla de registros de asistencia
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

    # Tabla de actividades de laboratorio
    c.execute('''
    CREATE TABLE IF NOT EXISTS actividades_lab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        responsable_id INTEGER NOT NULL,
        area TEXT,
        proyecto TEXT,
        tipo_trabajo TEXT,
        otro_tipo TEXT,
        actividades TEXT,
        equipos TEXT,
        otros_equipos TEXT,
        tiempo_uso TEXT,
        incidentes INTEGER,
        detalles_incidentes TEXT,
        observaciones TEXT,
        foto_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (responsable_id) REFERENCES users (id)
    )
    ''')

    # Tabla de proyectos de laboratorio
    c.execute('''
    CREATE TABLE IF NOT EXISTS proyectos_lab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        nombre_proyecto TEXT NOT NULL,
        tipo_trabajo TEXT,
        otro_tipo TEXT,
        responsable TEXT,
        personal_apoyo1 TEXT,
        personal_area1 TEXT,
        personal_apoyo2 TEXT,
        personal_area2 TEXT,
        equipos TEXT,
        materiales TEXT,
        descripcion TEXT,
        foto_path TEXT,
        observaciones TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabla de solicitudes de trabajo
    c.execute('''
    CREATE TABLE IF NOT EXISTS solicitudes_trabajo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_solicitud TEXT NOT NULL,
        solicitante_id INTEGER NOT NULL,
        nombre_solicitante TEXT NOT NULL,
        area_asignada TEXT,
        cargo_funcion TEXT,
        nombre_proyecto TEXT,
        descripcion_trabajo TEXT,
        equipos TEXT,
        materiales TEXT,
        herramientas TEXT,
        fecha_inicio TEXT,
        hora_inicio TEXT,
        fecha_fin TEXT,
        hora_fin TEXT,
        duracion_estimada TEXT,
        requiere_apoyo_tecnico INTEGER,
        observaciones TEXT,
        personal_involucrado TEXT,
        planos_adjuntos INTEGER,
        tipo_archivos TEXT,
        medio_entrega TEXT,
        observaciones_planos TEXT,
        firma_solicitante TEXT,
        fecha_firma TEXT,
        revisado_por TEXT,
        firma_revisado TEXT,
        aprobado_por TEXT,
        firma_aprobado TEXT,
        archivo_adjuntos_path TEXT,
        estado TEXT DEFAULT 'pendiente',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (solicitante_id) REFERENCES users (id)
    )
    ''')

    # Tabla de notificaciones del admin
    c.execute('''
    CREATE TABLE IF NOT EXISTS admin_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        mensaje TEXT NOT NULL,
        datos_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        mostrado INTEGER DEFAULT 0
    )
    ''')

    # Crear usuario admin si no existe
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

# --- CRUD para actividades ---
def add_actividad(data):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO actividades_lab (
            fecha, responsable_id, area, proyecto, tipo_trabajo, otro_tipo, actividades, equipos, otros_equipos,
            tiempo_uso, incidentes, detalles_incidentes, observaciones, foto_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['fecha'], data['responsable_id'], data['area'], data['proyecto'], data['tipo_trabajo'], data['otro_tipo'],
        data['actividades'], data['equipos'], data['otros_equipos'], data['tiempo_uso'], data['incidentes'],
        data['detalles_incidentes'], data['observaciones'], data['foto_path']
    ))
    conn.commit()
    actividad_id = c.lastrowid
    conn.close()
    return actividad_id

def get_actividades(user_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = '''
        SELECT a.*, u.full_name as responsable_nombre
        FROM actividades_lab a
        JOIN users u ON a.responsable_id = u.id
        WHERE 1=1
    '''
    params = []
    if user_id:
        query += ' AND a.responsable_id = ?'
        params.append(user_id)
    if start_date:
        query += ' AND date(a.fecha) >= date(?)'
        params.append(start_date)
    if end_date:
        query += ' AND date(a.fecha) <= date(?)'
        params.append(end_date)
    query += ' ORDER BY a.fecha DESC'
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_actividad(form_id):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT a.*, u.full_name as responsable_nombre
        FROM actividades_lab a
        JOIN users u ON a.responsable_id = u.id
        WHERE a.id = ?
    ''', (form_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- CRUD para proyectos ---
def add_proyecto(data):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO proyectos_lab (
            fecha_inicio, fecha_fin, nombre_proyecto, tipo_trabajo, otro_tipo, responsable,
            personal_apoyo1, personal_area1, personal_apoyo2, personal_area2, equipos, materiales,
            descripcion, foto_path, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['fecha_inicio'], data['fecha_fin'], data['nombre_proyecto'], data['tipo_trabajo'], data['otro_tipo'],
        data['responsable'], data['personal_apoyo1'], data['personal_area1'], data['personal_apoyo2'],
        data['personal_area2'], data['equipos'], data['materiales'], data['descripcion'],
        data['foto_path'], data['observaciones']
    ))
    conn.commit()
    proyecto_id = c.lastrowid
    conn.close()
    return proyecto_id

def get_proyectos(user_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM proyectos_lab WHERE 1=1"
    params = []
    if user_id:
        # Busca por nombre del responsable (full_name)
        c2 = conn.cursor()
        c2.execute("SELECT full_name FROM users WHERE id = ?", (user_id,))
        user = c2.fetchone()
        if user:
            query += " AND responsable = ?"
            params.append(user['full_name'])
    if start_date:
        query += " AND fecha_inicio >= ?"
        params.append(start_date)
    if end_date:
        query += " AND fecha_fin <= ?"
        params.append(end_date)
    c.execute(query, params)
    proyectos = c.fetchall()
    conn.close()
    return proyectos

def get_proyecto(form_id):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM proyectos_lab WHERE id = ?', (form_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- CRUD para solicitudes de trabajo ---
def add_solicitud_trabajo(data):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO solicitudes_trabajo (
            fecha_solicitud, solicitante_id, nombre_solicitante, area_asignada, cargo_funcion, nombre_proyecto,
            descripcion_trabajo, equipos, materiales, herramientas, fecha_inicio, hora_inicio, fecha_fin, hora_fin,
            duracion_estimada, requiere_apoyo_tecnico, observaciones, personal_involucrado, planos_adjuntos,
            tipo_archivos, medio_entrega, observaciones_planos, firma_solicitante, fecha_firma, revisado_por,
            firma_revisado, aprobado_por, firma_aprobado, archivo_adjuntos_path, estado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['fecha_solicitud'], data['solicitante_id'], data['nombre_solicitante'], data['area_asignada'], data['cargo_funcion'],
        data['nombre_proyecto'], data['descripcion_trabajo'], data['equipos'], data['materiales'], data['herramientas'],
        data['fecha_inicio'], data['hora_inicio'], data['fecha_fin'], data['hora_fin'], data['duracion_estimada'],
        data['requiere_apoyo_tecnico'], data['observaciones'], data['personal_involucrado'], data['planos_adjuntos'],
        data['tipo_archivos'], data['medio_entrega'], data['observaciones_planos'], data['firma_solicitante'],
        data['fecha_firma'], data['revisado_por'], data['firma_revisado'], data['aprobado_por'], data['firma_aprobado'],
        data['archivo_adjuntos_path'], data.get('estado', 'pendiente')
    ))
    conn.commit()
    solicitud_id = c.lastrowid
    conn.close()
    return solicitud_id

def get_solicitudes_trabajo(user_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    query = "SELECT * FROM solicitudes_trabajo WHERE 1=1"
    params = []
    if user_id:
        query += " AND solicitante_id = ?"
        params.append(user_id)
    if start_date:
        query += " AND fecha_solicitud >= ?"
        params.append(start_date)
    if end_date:
        query += " AND fecha_solicitud <= ?"
        params.append(end_date)
    c.execute(query, params)
    solicitudes = c.fetchall()
    conn.close()
    return solicitudes

def get_solicitud_trabajo(solicitud_id):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT s.*, u.full_name as solicitante_nombre
        FROM solicitudes_trabajo s
        JOIN users u ON s.solicitante_id = u.id
        WHERE s.id = ?
    ''', (solicitud_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_estado_solicitud(solicitud_id, nuevo_estado):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('UPDATE solicitudes_trabajo SET estado = ? WHERE id = ?', (nuevo_estado, solicitud_id))
    conn.commit()
    conn.close()

def delete_solicitud_trabajo(solicitud_id):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('DELETE FROM solicitudes_trabajo WHERE id = ?', (solicitud_id,))
    conn.commit()
    conn.close()

def duplicar_solicitud_trabajo(solicitud_id):
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    # Obtener la solicitud original
    c.execute('SELECT * FROM solicitudes_trabajo WHERE id = ?', (solicitud_id,))
    original = c.fetchone()
    if not original:
        conn.close()
        return None
    # Crear una copia (omitimos id y created_at)
    campos = [col for col in original.keys() if col not in ('id', 'created_at')]
    valores = [original[campo] for campo in campos]
    # Insertar la copia
    placeholders = ','.join(['?'] * len(campos))
    c.execute(f'''
        INSERT INTO solicitudes_trabajo ({','.join(campos)})
        VALUES ({placeholders})
    ''', valores)
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id

def set_user_notification(user_id, mensaje):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("UPDATE users SET notificacion = ? WHERE id = ?", (mensaje, user_id))
    conn.commit()
    conn.close()

def auto_delete_incomplete_attendance():
    """Elimina registros de asistencia incompletos después de 8 horas"""
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Buscar registros sin checkout de más de 8 horas
    eight_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=8)
    
    # Obtener información de los registros que se van a eliminar (para notificar al admin)
    c.execute("""
        SELECT a.id, a.check_in, u.id as user_id, u.full_name, u.username
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.check_out IS NULL 
        AND a.check_in < ?
    """, (eight_hours_ago,))
    
    deleted_records = c.fetchall()
    
    # Eliminar los registros
    c.execute("""
        DELETE FROM attendance 
        WHERE check_out IS NULL 
        AND check_in < ?
    """, (eight_hours_ago,))
    
    conn.commit()
    conn.close()
    
    return deleted_records

def get_admin_notifications():
    """Obtiene notificaciones pendientes para mostrar al admin"""
    conn = sqlite3.connect('attendance.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM admin_notifications WHERE mostrado = 0 ORDER BY created_at DESC")
    notifications = c.fetchall()
    
    conn.close()
    return notifications

def mark_admin_notification_read(notification_id):
    """Marca una notificación del admin como leída"""
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute("UPDATE admin_notifications SET mostrado = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

def add_admin_notification(titulo, mensaje, datos_json=None):
    """Agrega una notificación para el admin"""
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute("""
        INSERT INTO admin_notifications (titulo, mensaje, datos_json, created_at, mostrado)
        VALUES (?, ?, ?, ?, 0)
    """, (titulo, mensaje, datos_json, datetime.datetime.now()))
    
    conn.commit()
    conn.close()

def auto_delete_incomplete_attendance():
    """Elimina registros de asistencia incompletos después de 8 horas"""
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # Buscar registros sin checkout de más de 8 horas
    eight_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=8)
    
    # Obtener información de los registros que se van a eliminar (para notificar al admin)
    c.execute("""
        SELECT a.id, a.check_in, u.id as user_id, u.full_name, u.username
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.check_out IS NULL 
        AND a.check_in < ?
    """, (eight_hours_ago,))
    
    deleted_records = c.fetchall()
    
    # Eliminar los registros
    c.execute("""
        DELETE FROM attendance 
        WHERE check_out IS NULL 
        AND check_in < ?
    """, (eight_hours_ago,))
    
    conn.commit()
    conn.close()
    
    return deleted_records