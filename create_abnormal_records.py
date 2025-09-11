#!/usr/bin/env python3
import sqlite3
import datetime
from werkzeug.security import generate_password_hash

def create_abnormal_records():
    """Crea registros de prueba con horas anormales (ya cerrados)"""
    print("🧪 Creando registros de prueba con horas anormales...")
    
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()

    # Buscar un usuario existente
    c.execute("SELECT id, username, full_name FROM users WHERE is_admin = 0 LIMIT 1")
    user = c.fetchone()

    if not user:
        # Crear usuario de prueba
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

    # Crear 3 registros anormales de diferentes días
    registros_creados = []
    
    for i in range(3):
        # Fecha de entrada: hace varios días
        dias_atras = 7 - i  # 7, 6, 5 días atrás
        entrada = datetime.datetime.now() - datetime.timedelta(days=dias_atras, hours=8)
        
        # Fecha de salida: hace menos días (simulando que marcó salida esta semana)
        salida = datetime.datetime.now() - datetime.timedelta(days=1, hours=2)
        
        # Insertar registro anormal
        c.execute("""
            INSERT INTO attendance (user_id, check_in, check_out, description) 
            VALUES (?, ?, ?, ?)
        """, (user_id, entrada, salida, f"Registro anormal #{i+1} - Prueba"))
        
        # Calcular horas trabajadas
        horas_trabajadas = (salida - entrada).total_seconds() / 3600
        
        registros_creados.append({
            'entrada': entrada.strftime('%Y-%m-%d %H:%M:%S'),
            'salida': salida.strftime('%Y-%m-%d %H:%M:%S'),
            'horas': round(horas_trabajadas, 1)
        })

    conn.commit()
    conn.close()

    print(f"✅ Se crearon {len(registros_creados)} registros anormales para {username} ({full_name}):")
    print()
    
    total_horas_falsas = 0
    for i, registro in enumerate(registros_creados, 1):
        total_horas_falsas += registro['horas']
        print(f"📋 Registro #{i}:")
        print(f"   🕐 Entrada: {registro['entrada']}")
        print(f"   🕐 Salida:  {registro['salida']}")
        print(f"   ⏰ Horas trabajadas: {registro['horas']} horas")
        print(f"   🔴 ESTADO: ANORMAL (más de 8 horas)")
        print()
    
    print(f"💰 Total horas falsas creadas: {total_horas_falsas:.1f} horas")
    print()
    print("🚀 Ahora el sistema automáticamente:")
    print("   1. Detectará estos registros anormales")
    print("   2. Los eliminará automáticamente")
    print("   3. Notificará al administrador")

if __name__ == "__main__":
    create_abnormal_records()