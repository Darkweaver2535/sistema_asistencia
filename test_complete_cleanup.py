#!/usr/bin/env python3
import sqlite3
import datetime
import json
import sys
import os

# Agregar el directorio actual al path para importar database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import database

def test_complete_cleanup():
    """Prueba la funcionalidad completa de limpieza"""
    print("🧪 Iniciando prueba COMPLETA de limpieza...")
    print("=" * 70)
    
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # 1. Verificar registros pendientes
    c.execute("""
        SELECT COUNT(*) FROM attendance WHERE check_out IS NULL
    """)
    pending_count = c.fetchone()[0]
    print(f"📋 Registros pendientes (sin salida): {pending_count}")
    
    # 2. Verificar registros anormales (cerrados con más de 8 horas)
    c.execute("""
        SELECT COUNT(*), SUM((julianday(check_out) - julianday(check_in)) * 24) as total_horas
        FROM attendance 
        WHERE check_out IS NOT NULL
        AND (julianday(check_out) - julianday(check_in)) * 24 > 8
    """)
    abnormal_data = c.fetchone()
    abnormal_count = abnormal_data[0]
    abnormal_hours = abnormal_data[1] or 0
    print(f"⚠️  Registros anormales (más de 8h): {abnormal_count} ({abnormal_hours:.1f} horas falsas)")
    
    print("\n" + "=" * 70)
    print("🗑️  EJECUTANDO LIMPIEZA AUTOMÁTICA...")
    print("=" * 70)
    
    # 3. Ejecutar limpieza de registros pendientes
    print("\n1️⃣ Limpiando registros pendientes...")
    deleted_pending = database.auto_delete_incomplete_attendance()
    
    if deleted_pending:
        print(f"   ✅ Eliminados: {len(deleted_pending)} registros pendientes")
        for record in deleted_pending:
            entry_time = datetime.datetime.fromisoformat(record[1])
            hours_ago = (datetime.datetime.now() - entry_time).total_seconds() / 3600
            print(f"      • {record[4]} ({record[3]}) - hace {hours_ago:.1f} horas")
    else:
        print("   ℹ️  No hay registros pendientes para eliminar")
    
    # 4. Ejecutar limpieza de registros anormales
    print("\n2️⃣ Limpiando registros anormales...")
    deleted_abnormal = database.auto_delete_abnormal_closed_attendance()
    
    if deleted_abnormal:
        total_false_hours = sum(record[6] for record in deleted_abnormal)
        print(f"   ✅ Eliminados: {len(deleted_abnormal)} registros anormales")
        print(f"   💰 Horas falsas eliminadas: {total_false_hours:.1f} horas")
        
        for record in deleted_abnormal:
            print(f"      • {record[5]} ({record[4]}) - {record[6]:.1f} horas falsas")
    else:
        print("   ℹ️  No hay registros anormales para eliminar")
    
    # 5. Verificar estado final
    print("\n" + "=" * 70)
    print("📊 ESTADO FINAL:")
    print("=" * 70)
    
    c.execute("SELECT COUNT(*) FROM attendance WHERE check_out IS NULL")
    final_pending = c.fetchone()[0]
    
    c.execute("""
        SELECT COUNT(*), COALESCE(SUM((julianday(check_out) - julianday(check_in)) * 24), 0)
        FROM attendance 
        WHERE check_out IS NOT NULL
        AND (julianday(check_out) - julianday(check_in)) * 24 > 8
    """)
    final_abnormal_data = c.fetchone()
    final_abnormal = final_abnormal_data[0]
    final_abnormal_hours = final_abnormal_data[1]
    
    print(f"📋 Registros pendientes restantes: {final_pending}")
    print(f"⚠️  Registros anormales restantes: {final_abnormal} ({final_abnormal_hours:.1f} horas)")
    
    # 6. Verificar notificaciones creadas
    print("\n🔔 NOTIFICACIONES CREADAS:")
    print("-" * 40)
    
    notifications = database.get_admin_notifications()
    if notifications:
        for notif in notifications[-5:]:  # Últimas 5 notificaciones
            print(f"   • {notif['titulo']}")
            print(f"     {notif['mensaje']}")
            print(f"     Fecha: {notif['created_at']}")
            print()
    else:
        print("   ℹ️  No hay notificaciones pendientes")
    
    conn.close()
    
    print("✅ PRUEBA COMPLETA FINALIZADA")
    print("=" * 70)
    
    # Resumen
    total_eliminated = len(deleted_pending) + len(deleted_abnormal)
    total_false_hours_eliminated = sum(record[6] for record in deleted_abnormal) if deleted_abnormal else 0
    
    if total_eliminated > 0:
        print(f"\n🎯 RESUMEN:")
        print(f"   📊 Total registros eliminados: {total_eliminated}")
        print(f"   💰 Total horas falsas eliminadas: {total_false_hours_eliminated:.1f}")
        print(f"   🔔 Notificaciones creadas: {len([n for n in notifications if 'eliminados' in n['titulo']])}")
    
    return total_eliminated

if __name__ == "__main__":
    test_complete_cleanup()