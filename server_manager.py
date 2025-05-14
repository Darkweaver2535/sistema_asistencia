#tener descargado python, wsl --install y git bash
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import os
import sys
import socket
import threading
import webbrowser
import signal
import platform

class FlaskServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Servidor Flask")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.server_process = None
        self.log_thread = None
        self.running = False
        self.venv_path = self.detect_venv_path()
        self.flask_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        
        # Crear elementos de la interfaz
        self.create_widgets()
        
        # Configurar cierre adecuado
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def detect_venv_path(self):
        """Detecta la ruta del entorno virtual"""
        # Buscar en ubicaciones comunes
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Comprobar si estamos en un entorno virtual
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            return sys.prefix
        
        # Buscar un entorno virtual en el directorio actual
        venv_folders = ['venv', 'env', '.venv', '.env']
        for folder in venv_folders:
            possible_path = os.path.join(current_dir, folder)
            if os.path.exists(possible_path):
                # Determinar la ruta al activador según el sistema operativo
                if platform.system() == 'Windows':
                    if os.path.exists(os.path.join(possible_path, 'Scripts', 'activate.bat')):
                        return possible_path
                else:
                    if os.path.exists(os.path.join(possible_path, 'bin', 'activate')):
                        return possible_path
        
        return None
    
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del entorno virtual
        venv_frame = tk.Frame(main_frame)
        venv_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(venv_frame, text="Entorno Virtual:").pack(side=tk.LEFT)
        self.venv_status = tk.Label(venv_frame, text="No detectado", fg="red")
        if self.venv_path:
            self.venv_status.config(text=f"Detectado en {self.venv_path}", fg="green")
        self.venv_status.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones de control
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Iniciar Servidor", 
                                 command=self.start_server, 
                                 bg="#4CAF50", fg="white", 
                                 padx=20, pady=10,
                                 font=("Arial", 12, "bold"))
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="Detener Servidor", 
                                command=self.stop_server, 
                                bg="#F44336", fg="white", 
                                padx=20, pady=10,
                                font=("Arial", 12, "bold"),
                                state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        self.open_browser_btn = tk.Button(btn_frame, text="Abrir en Navegador", 
                                       command=self.open_in_browser, 
                                       bg="#2196F3", fg="white", 
                                       padx=20, pady=10,
                                       font=("Arial", 12, "bold"),
                                       state=tk.DISABLED)
        self.open_browser_btn.pack(side=tk.RIGHT)
        
        # Estado del servidor
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(status_frame, text="Estado:").pack(side=tk.LEFT)
        self.status_label = tk.Label(status_frame, text="Detenido", fg="red")
        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(status_frame, text="URL:").pack(side=tk.LEFT, padx=(20, 0))
        self.url_label = tk.Label(status_frame, text="N/A")
        self.url_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Área de logs
        log_frame = tk.LabelFrame(main_frame, text="Logs del Servidor", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, bg="#f5f5f5")
        self.log_area.pack(fill=tk.BOTH, expand=True)
    
    def get_local_ip(self):
        """Obtiene la IP local de la máquina"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def start_server(self):
        """Inicia el servidor Flask"""
        if self.running:
            return
        
        # Verificar que existe app.py
        if not os.path.exists(self.flask_app_path):
            messagebox.showerror("Error", f"No se encontró el archivo 'app.py' en {os.path.dirname(self.flask_app_path)}")
            return
            
        # Verificar entorno virtual
        if not self.venv_path:
            response = messagebox.askyesno("Advertencia", 
                                          "No se detectó un entorno virtual. Esto podría causar problemas. ¿Desea continuar?")
            if not response:
                return
        
        # Construir comando para ejecutar
        if platform.system() == 'Windows':
            if self.venv_path:
                # En Windows, usamos cmd para activar el entorno y ejecutar
                cmd = f'cmd /c "cd /d {os.path.dirname(self.flask_app_path)} && "{os.path.join(self.venv_path, "Scripts", "activate.bat")}" && python app.py"'
            else:
                cmd = f'cmd /c "cd /d {os.path.dirname(self.flask_app_path)} && python app.py"'
            
            # Usar shell=True en Windows para manejar comandos complejos
            self.server_process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        else:
            # En Unix/Linux/Mac
            if self.venv_path:
                activate_script = os.path.join(self.venv_path, "bin", "activate")
                cmd = f'bash -c "source {activate_script} && cd {os.path.dirname(self.flask_app_path)} && python app.py"'
                self.server_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
            else:
                cmd = ["python", self.flask_app_path]
                self.server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=os.path.dirname(self.flask_app_path)
                )
        
        # Iniciar hilo para leer la salida
        self.running = True
        self.log_thread = threading.Thread(target=self.read_output)
        self.log_thread.daemon = True
        self.log_thread.start()
        
        # Actualizar interfaz
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="En ejecución", fg="green")
    
    def read_output(self):
        """Lee la salida del servidor en un hilo separado"""
        server_url = None
        
        while self.running and self.server_process and self.server_process.poll() is None:
            line = self.server_process.stdout.readline()
            if line:
                self.update_log(line)
                
                # Buscar la URL del servidor en la salida
                if " * Running on " in line:
                    try:
                        server_url = line.split(" * Running on ")[1].split(" ")[0].strip()
                        if "127.0.0.1" in server_url or "localhost" in server_url:
                            ip = self.get_local_ip()
                            port = server_url.split(":")[-1]
                            network_url = f"http://{ip}:{port}"
                            
                            self.root.after(0, lambda: self.url_label.config(
                                text=f"Local: {server_url} | Red: {network_url}"))
                            self.root.after(0, lambda: self.open_browser_btn.config(state=tk.NORMAL))
                        else:
                            self.root.after(0, lambda: self.url_label.config(text=server_url))
                            self.root.after(0, lambda: self.open_browser_btn.config(state=tk.NORMAL))
                    except:
                        pass
        
        # Si llegamos aquí, el servidor se detuvo
        if self.running:
            self.root.after(0, self.handle_server_stopped)
    
    def update_log(self, text):
        """Actualiza el área de logs desde un hilo"""
        self.root.after(0, lambda: self.log_area.insert(tk.END, text))
        self.root.after(0, lambda: self.log_area.see(tk.END))
    
    def handle_server_stopped(self):
        """Maneja el caso cuando el servidor se detiene inesperadamente"""
        self.running = False
        self.server_process = None
        
        # Actualizar UI
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.open_browser_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Detenido", fg="red")
        self.url_label.config(text="N/A")
        
        # Informar al usuario
        self.update_log("\n[Sistema] El servidor se ha detenido.\n")
    
    def stop_server(self):
        """Detiene el servidor Flask"""
        if not self.running or not self.server_process:
            return
        
        # Intentar detener el proceso de manera correcta
        try:
            if platform.system() == 'Windows':
                # En Windows usamos taskkill para asegurarnos de matar todos los procesos hijo
                subprocess.run(f"taskkill /F /T /PID {self.server_process.pid}", 
                             shell=True, check=False)
            else:
                # En sistemas Unix, enviamos una señal SIGTERM
                os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
        except:
            # Si falla, intentamos matar el proceso directamente
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
        
        self.running = False
        self.update_log("\n[Sistema] Servidor detenido por el usuario.\n")
        
        # Actualizar interfaz
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.open_browser_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Detenido", fg="red")
        self.url_label.config(text="N/A")
    
    def open_in_browser(self):
        """Abre la URL del servidor en el navegador predeterminado"""
        url_text = self.url_label.cget("text")
        if url_text != "N/A":
            local_url = url_text.split(" | ")[0].replace("Local: ", "") if " | " in url_text else url_text
            webbrowser.open(local_url)
    
    def on_closing(self):
        """Función llamada al cerrar la aplicación"""
        if self.running:
            if messagebox.askyesno("Confirmar salida", 
                                  "El servidor está en ejecución. ¿Desea detenerlo y salir?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()

# Función principal para crear un ejecutable autónomo
def main():
    root = tk.Tk()
    app = FlaskServerManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()