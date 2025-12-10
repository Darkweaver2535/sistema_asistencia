import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import os
import database
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import threading
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

database.init_db()

# Lista de equipos para los formularios
EQUIPOS_LAB = [
    "Impresora 3D", "Torno CNC", "Soldadora", "Fresadora", "Sierra de disco",
    "Taladro de banco", "Rectificadora", "Cizalla", "Prensa hidráulica", "Lijadora", "Multímetro", "Osciloscopio"
]

@app.route('/')
def index():
    if 'user_id' in session:
        user = database.get_user(session['username'])
        pending_checkout = database.get_pending_checkout(user['id'])
        current_date = datetime.now()
        return render_template('dashboard.html', user=user, pending_checkout=pending_checkout, current_date=current_date)
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = database.get_user(username)
        
        if user and database.check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['is_admin'] = user['is_admin']
            flash('¡Inicio de sesión exitoso!', 'success')
            return redirect(url_for('index'))
        
        flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

@app.route('/check_in', methods=['POST'])
def check_in():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success, message = database.check_in(session['user_id'])
    
    if success:
        flash('Entrada registrada correctamente', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('index'))

@app.route('/check_out', methods=['POST'])
def check_out():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    description = request.form.get('description', '')
    success, message = database.check_out(session['user_id'], description)
    
    if success:
        flash('Salida registrada correctamente', 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    
    users = database.get_users()
    return render_template('admin.html', users=users)

@app.route('/admin/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso no autorizado'})
    
    username = request.form.get('username')
    password = request.form.get('password')
    full_name = request.form.get('full_name')
    is_admin = 1 if request.form.get('is_admin') else 0
    
    if not (username and password and full_name):
        return jsonify({'success': False, 'message': 'Todos los campos son obligatorios'})
    
    success = database.add_user(username, password, full_name, is_admin)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'})

@app.route('/admin/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        # Obtener información del usuario
        conn = sqlite3.connect('attendance.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT id, username, full_name, is_admin FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('admin'))
        
        return render_template('update_user.html', user=user)
    
    elif request.method == 'POST':
        # Actualizar usuario
        username = request.form.get('username')
        password = request.form.get('password')  # Puede ser vacío si no cambia
        full_name = request.form.get('full_name')
        is_admin = 1 if request.form.get('is_admin') else 0
        
        if not (username and full_name):
            return jsonify({'success': False, 'message': 'Usuario y nombre son obligatorios'})
        
        success, message = database.update_user(user_id, username, password, full_name, is_admin)
        
        return jsonify({'success': success, 'message': message})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Acceso no autorizado'})
    
    # No permitir eliminar el propio usuario administrador
    if user_id == session['user_id']:
        return jsonify({'success': False, 'message': 'No puedes eliminar tu propio usuario'})
    
    success, message = database.delete_user(user_id)
    return jsonify({'success': success, 'message': message})

@app.route('/admin/reports')
def reports():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    users = database.get_users()
    records = database.get_attendance_records(user_id, start_date, end_date)
    
    # Procesar registros para calcular horas trabajadas
    processed_records = []
    total_hours = 0
    for record in records:
        rec = dict(record)
        if rec['check_in']:
            rec['check_in'] = datetime.fromisoformat(rec['check_in'])
        if rec['check_out']:
            rec['check_out'] = datetime.fromisoformat(rec['check_out'])
            if rec['check_in']:
                diff = rec['check_out'] - rec['check_in']
                hours = diff.total_seconds() / 3600
                rec['hours_worked'] = round(hours, 2)
                total_hours += hours
            else:
                rec['hours_worked'] = 0
        else:
            rec['hours_worked'] = 0
        processed_records.append(rec)
    total_hours = round(total_hours, 2)
    
    return render_template('reports.html', users=users, records=processed_records, 
                           selected_user=user_id, start_date=start_date, end_date=end_date,
                           total_hours=total_hours)

@app.route('/laboratorio')
def laboratorio():
    return render_template('laboratorio.html')

# --- Registro de Actividades ---
@app.route('/laboratorio/actividades', methods=['GET', 'POST'])
def actividades_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_date = datetime.now()
    if request.method == 'POST':
        data = {
            'fecha': request.form.get('fecha'),
            'responsable_id': session['user_id'],
            'area': ', '.join(request.form.getlist('area')),
            'proyecto': request.form.get('proyecto'),
            'tipo_trabajo': request.form.get('tipo_trabajo'),
            'otro_tipo': request.form.get('otro_tipo'),
            'actividades': request.form.get('actividades'),
            'equipos': ', '.join(request.form.getlist('equipos')),
            'otros_equipos': request.form.get('otros_equipos'),
            'tiempo_uso': request.form.get('tiempo_uso'),
            'incidentes': 1 if request.form.get('incidentes') == 'Si' else 0,
            'detalles_incidentes': request.form.get('detalles_incidentes'),
            'observaciones': request.form.get('observaciones'),
            'foto_path': None
        }
        # Guardar foto si existe
        foto = request.files.get('foto')
        if foto and foto.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['foto_path'] = f"{UPLOAD_FOLDER}/{filename}"
        actividad_id = database.add_actividad(data)
        flash('Registro de actividad guardado correctamente', 'success')
        return redirect(url_for('ver_actividad', form_id=actividad_id))
    return render_template('registro_actividades.html', equipos=EQUIPOS_LAB, current_date=current_date)

@app.route('/laboratorio/actividades/<int:form_id>')
def ver_actividad(form_id):
    actividad = database.get_actividad(form_id)
    if not actividad:
        flash('Registro no encontrado', 'error')
        return redirect(url_for('ver_registros'))
    return render_template('ver_actividad.html', actividad=actividad)

@app.route('/laboratorio/actividades/pdf/<int:form_id>')
def actividad_pdf(form_id):
    actividad = database.get_actividad(form_id)
    if not actividad:
        return "No encontrado", 404
    current_date = datetime.now()
    return render_template('actividad_pdf.html', actividad=actividad, current_date=current_date)

# --- Registro de Proyectos ---
@app.route('/laboratorio/proyectos', methods=['GET', 'POST'])
def proyectos_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_date = datetime.now()
    if request.method == 'POST':
        data = {
            'fecha_inicio': request.form.get('fecha_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'nombre_proyecto': request.form.get('nombre_proyecto'),
            'tipo_trabajo': request.form.get('tipo_trabajo'),
            'otro_tipo': request.form.get('otro_tipo'),
            'responsable': request.form.get('responsable'),
            'personal_apoyo1': request.form.get('personal_apoyo1'),
            'personal_area1': request.form.get('personal_area1'),
            'personal_apoyo2': request.form.get('personal_apoyo2'),
            'personal_area2': request.form.get('personal_area2'),
            'equipos': ', '.join(request.form.getlist('equipos')),
            'materiales': request.form.get('materiales'),
            'descripcion': request.form.get('descripcion'),
            'foto_path': None,
            'observaciones': request.form.get('observaciones')
        }
        foto = request.files.get('foto')
        if foto and foto.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{foto.filename}")
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['foto_path'] = f"{UPLOAD_FOLDER}/{filename}"
        proyecto_id = database.add_proyecto(data)
        flash('Registro de proyecto guardado correctamente', 'success')
        return redirect(url_for('ver_proyecto', form_id=proyecto_id))
    return render_template('registro_proyectos.html', equipos=EQUIPOS_LAB, current_date=current_date)

@app.route('/laboratorio/proyectos/<int:form_id>')
def ver_proyecto(form_id):
    proyecto = database.get_proyecto(form_id)
    if not proyecto:
        flash('Registro no encontrado', 'error')
        return redirect(url_for('ver_registros'))
    return render_template('ver_proyecto.html', proyecto=proyecto)

@app.route('/laboratorio/proyectos/pdf/<int:form_id>')
def proyecto_pdf(form_id):
    proyecto = database.get_proyecto(form_id)
    if not proyecto:
        return "No encontrado", 404
    current_date = datetime.now()
    return render_template('proyecto_pdf.html', proyecto=proyecto, current_date=current_date)

# --- Listado de registros (ambos formularios) ---
@app.route('/laboratorio/registros')
def ver_registros():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = request.args.get('user_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    actividades = database.get_actividades(user_id, start_date, end_date)
    proyectos = database.get_proyectos(user_id, start_date, end_date)
    solicitudes = database.get_solicitudes_trabajo(user_id, start_date, end_date)
    users = database.get_users()
    selected_user = user_id if user_id else ''
    return render_template('ver_registros.html', actividades=actividades, proyectos=proyectos, solicitudes=solicitudes, users=users, selected_user=selected_user, start_date=start_date, end_date=end_date)

# --- Solicitud de Formulario de Trabajo ---

@app.route('/laboratorio/solicitud_trabajo', methods=['GET', 'POST'])
def solicitud_trabajo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_date = datetime.now()
    if request.method == 'POST':
        data = {
            'fecha_solicitud': request.form.get('fecha_solicitud'),
            'solicitante_id': session['user_id'],
            'nombre_solicitante': session.get('full_name'),
            'area_asignada': ', '.join(request.form.getlist('area_asignada')),
            'cargo_funcion': request.form.get('cargo_funcion'),
            'nombre_proyecto': request.form.get('nombre_proyecto'),
            'descripcion_trabajo': request.form.get('descripcion_trabajo'),
            'equipos': request.form.get('equipos'),
            'materiales': request.form.get('materiales'),
            'herramientas': request.form.get('herramientas'),
            'fecha_inicio': request.form.get('fecha_inicio'),
            'hora_inicio': request.form.get('hora_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'hora_fin': request.form.get('hora_fin'),
            'duracion_estimada': request.form.get('duracion_estimada'),
            'requiere_apoyo_tecnico': 1 if request.form.get('requiere_apoyo_tecnico') == 'Si' else 0,
            'observaciones': request.form.get('observaciones'),
            'personal_involucrado': request.form.get('personal_involucrado'),
            'planos_adjuntos': 0,  # o 1 si quieres marcar por defecto
            'tipo_archivos': request.form.get('tipo_archivos', ''),
            'medio_entrega': request.form.get('medio_entrega', ''),
            'observaciones_planos': request.form.get('observaciones_planos', ''),
            'firma_solicitante': '',  # o lo que corresponda
            'fecha_firma': '',
            'revisado_por': '',
            'firma_revisado': '',
            'aprobado_por': '',
            'firma_aprobado': '',
            'archivo_adjuntos_path': None,
            'estado': 'pendiente'
            
        }
        # Guardar archivo adjunto si existe
        archivo = request.files.get('archivo_adjuntos')
        if archivo and archivo.filename:
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{archivo.filename}")
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            data['archivo_adjuntos_path'] = f"{UPLOAD_FOLDER}/{filename}"
        solicitud_id = database.add_solicitud_trabajo(data)
        flash('Solicitud enviada correctamente', 'success')
        return redirect(url_for('ver_solicitud', solicitud_id=solicitud_id))
    return render_template('solicitud_trabajo.html', current_date=current_date)

@app.route('/laboratorio/solicitud_trabajo/<int:solicitud_id>')
def ver_solicitud(solicitud_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    solicitud = database.get_solicitud_trabajo(solicitud_id)
    if not solicitud:
        flash('Solicitud no encontrada', 'error')
        return redirect(url_for('laboratorio'))
    return render_template('ver_solicitud.html', solicitud=solicitud)

@app.route('/laboratorio/solicitud_trabajo/pdf/<int:solicitud_id>')
def solicitud_pdf(solicitud_id):
    solicitud = database.get_solicitud_trabajo(solicitud_id)
    if not solicitud:
        return "No encontrado", 404
    current_date = datetime.now().strftime('%d/%m/%Y %H:%M')
    return render_template('solicitud_pdf.html', solicitud=solicitud, current_date=current_date)

# --- Listar solicitudes y notificaciones (solo admin) ---
@app.route('/notificaciones')
def notificaciones():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    solicitudes = database.get_solicitudes_trabajo()
    stats = {
        'pendientes': sum(1 for s in solicitudes if s['estado'] == 'pendiente'),
        'revisado': sum(1 for s in solicitudes if s['estado'] == 'revisado'),
        'aprobado': sum(1 for s in solicitudes if s['estado'] == 'aprobado'),
        'rechazado': sum(1 for s in solicitudes if s['estado'] == 'rechazado'),
    }
    return render_template('notificaciones.html', solicitudes=solicitudes, stats=stats)

# --- Cambiar estado de solicitud (solo admin) ---
@app.route('/notificaciones/estado/<int:solicitud_id>', methods=['GET', 'POST'])
def cambiar_estado_solicitud(solicitud_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    nuevo_estado = request.args.get('estado') or request.form.get('estado')
    if not nuevo_estado:
        flash('Estado no especificado', 'error')
        return redirect(url_for('notificaciones'))
    database.update_estado_solicitud(solicitud_id, nuevo_estado)
    # Notificación persistente para el solicitante
    solicitud = database.get_solicitud_trabajo(solicitud_id)
    if solicitud:
        mensaje = None
        if nuevo_estado == 'aprobado':
            mensaje = f"Tu solicitud de trabajo N° {solicitud_id} ha sido APROBADA."
        elif nuevo_estado == 'rechazado':
            mensaje = f"Tu solicitud de trabajo N° {solicitud_id} ha sido RECHAZADA."
        if mensaje:
            database.set_user_notification(solicitud['solicitante_id'], mensaje)
    flash(f'Solicitud cambiada a {nuevo_estado}', 'success')
    return redirect(url_for('notificaciones'))

# --- Editar solicitud ---
@app.route('/solicitudes/editar/<int:id>', methods=['GET', 'POST'], endpoint='solicitudes.editar')
def solicitudes_editar(id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    solicitud = database.get_solicitud_trabajo(id)
    if not solicitud:
        flash('Solicitud no encontrada', 'error')
        return redirect(url_for('notificaciones'))
    if request.method == 'POST':
        # Actualiza los campos necesarios aquí
        # database.update_solicitud_trabajo(id, request.form)
        flash('Solicitud actualizada correctamente', 'success')
        return redirect(url_for('ver_solicitud', solicitud_id=id))
    return render_template('editar_solicitud.html', solicitud=solicitud)

# --- Aprobar solicitud ---
@app.route('/solicitudes/aprobar/<int:id>', endpoint='solicitudes.aprobar')
def solicitudes_aprobar(id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    database.update_estado_solicitud(id, 'aprobado')
    flash('Solicitud aprobada', 'success')
    return redirect(url_for('ver_solicitud', solicitud_id=id))

# --- Rechazar solicitud ---
@app.route('/solicitudes/rechazar/<int:id>', endpoint='solicitudes.rechazar')
def solicitudes_rechazar(id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    database.update_estado_solicitud(id, 'rechazado')
    flash('Solicitud rechazada', 'info')
    return redirect(url_for('ver_solicitud', solicitud_id=id))

# --- Duplicar solicitud ---
@app.route('/solicitudes/duplicar/<int:id>', endpoint='solicitudes.duplicar')
def solicitudes_duplicar(id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Acceso no autorizado', 'error')
        return redirect(url_for('index'))
    nueva_id = database.duplicar_solicitud_trabajo(id)
    flash('Solicitud duplicada', 'success')
    return redirect(url_for('ver_solicitud', solicitud_id=nueva_id))

# --- Servir archivos subidos (fotos) ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/usuario/ocultar_notificacion', methods=['POST'])
def ocultar_notificacion():
    if 'user_id' not in session:
        return '', 401
    database.set_user_notification(session['user_id'], None)
    return '', 204

@app.context_processor
def inject_pendientes_count():
    if 'user_id' in session and session.get('is_admin'):
        solicitudes = database.get_solicitudes_trabajo()
        pendientes = sum(1 for s in solicitudes if s['estado'] == 'pendiente')
        return dict(num_pendientes=pendientes)
    return dict(num_pendientes=0)

def cleanup_incomplete_attendance():
    """Función que se ejecuta periódicamente para limpiar asistencias incompletas y anormales"""
    while True:
        try:
            # 1. Limpiar registros pendientes (sin check_out) de más de 8 horas
            deleted_records = database.auto_delete_incomplete_attendance()
            
            if deleted_records:
                # Preparar datos para la notificación
                usuarios_eliminados = []
                for record in deleted_records:
                    usuarios_eliminados.append({
                        'nombre': record[3],  # full_name
                        'username': record[4],  # username
                        'fecha_entrada': record[1],  # check_in
                        'user_id': record[2]  # user_id
                    })
                
                # Crear notificación para el admin
                titulo = f"Registros eliminados por no marcar salida"
                mensaje = f"Se eliminaron {len(deleted_records)} registro(s) de asistencia por no marcar salida después de 12 horas"
                datos_json = json.dumps(usuarios_eliminados)
                
                database.add_admin_notification(titulo, mensaje, datos_json)
                
                print(f"[{datetime.now()}] Se eliminaron {len(deleted_records)} registros incompletos")
            
            # 2. Limpiar registros cerrados anormales (más de 8 horas)
            abnormal_records = database.auto_delete_abnormal_closed_attendance()
            
            if abnormal_records:
                # Preparar datos para la notificación de registros anormales
                usuarios_anormales = []
                total_horas_falsas = 0
                for record in abnormal_records:
                    horas = record[6]  # horas_trabajadas
                    total_horas_falsas += horas
                    usuarios_anormales.append({
                        'nombre': record[4],  # full_name
                        'username': record[5],  # username
                        'fecha_entrada': record[1],  # check_in
                        'fecha_salida': record[2],  # check_out
                        'horas_trabajadas': round(horas, 1),
                        'user_id': record[3]  # user_id
                    })
                
                # Crear notificación para el admin sobre registros anormales
                titulo_anormal = f"Registros anormales eliminados (más de 12 horas)"
                mensaje_anormal = f"Se eliminaron {len(abnormal_records)} registro(s) con horas anormales. Total de horas falsas: {total_horas_falsas:.1f}"
                datos_json_anormal = json.dumps(usuarios_anormales)
                
                database.add_admin_notification(titulo_anormal, mensaje_anormal, datos_json_anormal)
                
                print(f"[{datetime.now()}] Se eliminaron {len(abnormal_records)} registros anormales con {total_horas_falsas:.1f} horas falsas")
            
        except Exception as e:
            print(f"Error en cleanup_incomplete_attendance: {e}")
        
        # Esperar 10 segundos para testing (cambiar a 1800 en producción)
        time.sleep(1800)

# Iniciar hilo de limpieza automática
cleanup_thread = threading.Thread(target=cleanup_incomplete_attendance, daemon=True)
cleanup_thread.start()

@app.route('/admin/notifications')
def admin_notifications():
    """Obtiene notificaciones pendientes para el admin"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'notifications': []})
    
    notifications = database.get_admin_notifications()
    notifications_data = []
    
    for notif in notifications:
        notif_data = {
            'id': notif['id'],
            'titulo': notif['titulo'],
            'mensaje': notif['mensaje'],
            'created_at': notif['created_at'],
            'usuarios': []
        }
        
        if notif['datos_json']:
            try:
                notif_data['usuarios'] = json.loads(notif['datos_json'])
            except:
                pass
        
        notifications_data.append(notif_data)
    
    return jsonify({'notifications': notifications_data})

@app.route('/admin/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Marca una notificación como leída"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False})
    
    database.mark_admin_notification_read(notification_id)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)