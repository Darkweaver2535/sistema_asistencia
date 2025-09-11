import sqlite3
import datetime
from werkzeug.security import generate_password_hash

# Conectar a la base de datos
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

# Tiempo de hace 7 horas y 57 minutos
test_time = datetime.datetime.now() - datetime.timedelta(hours=7, minutes=57)

# Buscar un usuario existente
c.execute("SELECT id, username, full_name FROM users WHERE is_admin = 0 LIMIT 1")
user = c.fetchone()

# Si no hay usuarios, crear uno de prueba
if not user:
    hashed_password = generate_password_hash('test123')
    c.execute("INSERT INTO users (username, password, full_name, is_admin) VALUES (?, ?, ?, ?)",
             ('estudiante_test', hashed_password, 'Estudiante de Prueba', 0))
    user_id = c.lastrowid
    username = 'estudiante_test'
    full_name = 'Estudiante de Prueba'
else:
    user_id = user[0]
    username = user[1]
    full_name = user[2]

# Eliminar cualquier registro pendiente existente
c.execute("DELETE FROM attendance WHERE user_id = ? AND check_out IS NULL", (user_id,))

# Insertar registro de prueba
c.execute("INSERT INTO attendance (user_id, check_in, check_out) VALUES (?, ?, NULL)",
         (user_id, test_time))

conn.commit()
conn.close()

print(f"✅ Registro creado para {username} ({full_name})")
print(f"📅 Entrada: {test_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"⏰ Hace: 7 horas y 57 minutos")
print(f"🗑️  Se eliminará automáticamente en aproximadamente 3 minutos")
print(f"👤 User ID: {user_id}")