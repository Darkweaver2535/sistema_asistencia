#!/usr/bin/env python3
import sqlite3
import datetime
import json
import sys
import os

# Agregar el directorio actual al path para importar database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database

def test_cleanup():
    """Prueba la funcionalidad de limpieza de registros"""
    print("🧪 Iniciando prueba de limpieza de registros...")
    
    # 1. Verificar registros pendientes antes de la limpieza
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    c.execute("""
        SELECT a.id, a.check_in, u.username, u.full_name
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.check_out IS NULL
    """)
    
    records_before = c.fetchall()
    print(f"\n📋 Registros pendientes ANTES de la limpieza: {len(records_before)}")
    
    for record in records_before:
        entry_time = datetime.datetime.fromisoformat(record[1])
        hours_ago = (datetime.datetime.now() - entry_time).total_seconds() / 3600
        print(f"   • {record[2]} ({record[3]}) - Hace {hours_ago:.1f} horas")
    
    # 2. Ejecutar la limpieza
    print("\n🗑️  Ejecutando limpieza automática...")
    deleted_records = database.auto_delete_incomplete_attendance()
    
    # 3. Verificar registros después de la limpieza
    c.execute("""
        SELECT a.id, a.check_in, u.username, u.full_name
        FROM attendance a
        JOIN users u ON a.user_id = u.id
        WHERE a.check_out IS NULL
    """)
    
    records_after = c.fetchall()
    print(f"\n📋 Registros pendientes DESPUÉS de la limpieza: {len(records_after)}")
    
    # 4. Mostrar resultados
    if deleted_records:
        print(f"\n✅ Se eliminaron {len(deleted_records)} registros:")
        for record in deleted_records:
            entry_time = datetime.datetime.fromisoformat(record[1])
            hours_ago = (datetime.datetime.now() - entry_time).total_seconds() / 3600
            print(f"   • {record[4]} ({record[3]}) - Entrada: {record[1]} (hace {hours_ago:.1f} horas)")
        
        # 5. Crear notificación para el admin
        usuarios_eliminados = []
        for record in deleted_records:
            usuarios_eliminados.append({
                'nombre': record[3],  # full_name
                'username': record[4],  # username
                'fecha_entrada': record[1],  # check_in
                'user_id': record[2]  # user_id
            })
        
        titulo = f"Registros eliminados por no marcar salida"
        mensaje = f"Se eliminaron {len(deleted_records)} registro(s) de asistencia por no marcar salida después de 8 horas"
        datos_json = json.dumps(usuarios_eliminados)
        
        database.add_admin_notification(titulo, mensaje, datos_json)
        print(f"\n📬 Notificación creada para el administrador")
        
    else:
        print("\n ℹ️  No hay registros para eliminar (todos están dentro del límite de 8 horas)")
    
    # 6. Verificar notificaciones pendientes
    notifications = database.get_admin_notifications()
    print(f"\n🔔 Notificaciones pendientes para admin: {len(notifications)}")
    
    for notif in notifications:
        print(f"   • {notif['titulo']} - {notif['created_at']}")
    
    conn.close()
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_cleanup()