import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import datetime
import database

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializar base de datos
database.init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        user = database.get_user(session['username'])
        pending_checkout = database.get_pending_checkout(user['id'])
        current_date = datetime.datetime.now()
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
    for record in records:
        rec = dict(record)
        if rec['check_in']:
            rec['check_in'] = datetime.datetime.fromisoformat(rec['check_in'])
        if rec['check_out']:
            rec['check_out'] = datetime.datetime.fromisoformat(rec['check_out'])
            if rec['check_in']:
                # Calcular horas trabajadas
                diff = rec['check_out'] - rec['check_in']
                hours = diff.total_seconds() / 3600
                rec['hours_worked'] = round(hours, 2)
            else:
                rec['hours_worked'] = 0
        else:
            rec['hours_worked'] = 0
        processed_records.append(rec)
    
    return render_template('reports.html', users=users, records=processed_records, 
                           selected_user=user_id, start_date=start_date, end_date=end_date)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)