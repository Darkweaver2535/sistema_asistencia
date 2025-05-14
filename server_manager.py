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
from PIL import Image, ImageTk

# Definición de colores (esquema de azul, amarillo y blanco)
AZUL_OSCURO = "#003366"  # Azul institucional oscuro
AZUL_MEDIO = "#0055A4"   # Azul medio para botones
AMARILLO = "#FFD700"     # Amarillo dorado
BLANCO = "#FFFFFF"       # Blanco
GRIS_CLARO = "#F0F0F0"   # Gris muy claro (casi blanco) para áreas de texto


class FlaskServerManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Servidor Flask - EMI")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Variables
        self.server_process = None
        self.log_thread = None
        self.running = False
        self.venv_path = self.detect_venv_path()
        self.flask_app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
        
        # Establecer tema de la aplicación
        self.set_theme()

        # Crear elementos de la interfaz
        self.create_widgets()
        
        # Configurar cierre adecuado
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def set_theme(self):
        """Configura el tema visual de la aplicación"""
        # Configurar el fondo
        try:
            # Cargar imagen de fondo y ajustarla al tamaño
            bg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images", "fondo.jpg")
            if os.path.exists(bg_path):
                bg_image = Image.open(bg_path)
                bg_image = bg_image.resize((700, 500))  # Ajustar al tamaño inicial de la ventana
                self.bg_photo = ImageTk.PhotoImage(bg_image)
                
                # Crear un canvas como fondo
                self.bg_canvas = tk.Canvas(self.root, width=700, height=500)
                self.bg_canvas.pack(fill=tk.BOTH, expand=True)
                self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor=tk.NW)
                
                # Frame principal transparente sobre el canvas
                self.main_frame = tk.Frame(self.bg_canvas, bg='', padx=10, pady=10)  # Sin color de fondo
                self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.95, relheight=0.95)
            else:
                # Si no existe la imagen, usar un color de fondo
                self.root.configure(bg=AZUL_OSCURO)
                self.main_frame = tk.Frame(self.root, bg=AZUL_OSCURO, padx=10, pady=10)
                self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        except Exception as e:
            print(f"Error al cargar el fondo: {e}")
            # En caso de error, usar un color de fondo
            self.root.configure(bg=AZUL_OSCURO)
            self.main_frame = tk.Frame(self.root, bg=AZUL_OSCURO, padx=10, pady=10)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
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
        # Logo en recuadro blanco
        logo_frame = tk.Frame(self.main_frame, bg=BLANCO, bd=2, relief=tk.RIDGE)
        logo_frame.pack(pady=(0, 10))  # Solo ancho necesario, no expandir horizontalmente
        
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "images", "emi_logo.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80))  # Ajustar tamaño
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                logo_label = tk.Label(logo_frame, image=self.logo_photo, bg=BLANCO)
                logo_label.pack(side=tk.LEFT, padx=10, pady=10)
                
                # Título al lado del logo
                title_label = tk.Label(logo_frame, text="Gestor de Servidor Flask", 
                                   font=("Arial", 18, "bold"), 
                                   fg=AZUL_OSCURO, bg=BLANCO)
                title_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error al cargar el logo: {e}")
            # Si hay error, mostrar solo texto
            title_label = tk.Label(logo_frame, text="Gestor de Servidor Flask - EMI", 
                               font=("Arial", 18, "bold"), 
                               fg=AZUL_OSCURO, bg=BLANCO)
            title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Información del entorno virtual
        venv_frame = tk.Frame(self.main_frame, bg='')  # Sin color de fondo
        venv_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(venv_frame, text="Entorno Virtual:", bg='white', fg=BLANCO, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.venv_status = tk.Label(venv_frame, text="No detectado", fg=AMARILLO, bg='white')
        if self.venv_path:
            self.venv_status.config(text=f"Detectado en {self.venv_path}", fg=AMARILLO)
        self.venv_status.pack(side=tk.LEFT, padx=(5, 0))
        
        # Botones de control
        btn_frame = tk.Frame(self.main_frame, bg='')  # Sin color de fondo
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="Iniciar Servidor", 
                                 command=self.start_server, 
                                 bg=AZUL_MEDIO, fg=BLANCO, 
                                 padx=20, pady=10,
                                 font=("Arial", 12, "bold"),
                                 activebackground=AZUL_OSCURO,
                                 activeforeground=BLANCO)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="Detener Servidor", 
                                command=self.stop_server, 
                                bg=AMARILLO, fg=AZUL_OSCURO, 
                                padx=20, pady=10,
                                font=("Arial", 12, "bold"),
                                activebackground="#E6C200",  # Amarillo más oscuro para hover
                                activeforeground=AZUL_OSCURO,
                                state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        self.open_browser_btn = tk.Button(btn_frame, text="Abrir en Navegador", 
                                       command=self.open_in_browser, 
                                       bg=AZUL_MEDIO, fg=BLANCO, 
                                       padx=20, pady=10,
                                       font=("Arial", 12, "bold"),
                                       activebackground=AZUL_OSCURO,
                                       activeforeground=BLANCO,
                                       state=tk.DISABLED)
        self.open_browser_btn.pack(side=tk.RIGHT)
        
        # Estado del servidor
        status_frame = tk.Frame(self.main_frame, bg='')  # Sin color de fondo
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(status_frame, text="Estado:", bg='white', fg=BLANCO, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.status_label = tk.Label(status_frame, text="Detenido", fg=AMARILLO, bg='white')  # O cualquier color válido

        self.status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(status_frame, text="URL:", bg='white', fg=BLANCO, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(20, 0))

        self.url_label = tk.Label(status_frame, text="N/A", bg='white', fg=AMARILLO)
        self.url_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Área de logs - fondo semi-transparente
        log_frame = tk.LabelFrame(self.main_frame, text="Logs del Servidor", 
                               padx=5, pady=5, bg='', fg=BLANCO,
                               font=("Arial", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, 
                                             bg=AZUL_OSCURO, fg=AMARILLO,
                                             font=("Consolas", 9))
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
        self.status_label.config(text="Detenido", fg=AMARILLO)
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
        self.status_label.config(text="Detenido", fg=AMARILLO)
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