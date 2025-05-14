import sys
import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, messagebox
import shutil
import pkg_resources

# Asegúrate de que el script principal exista
def check_required_files():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    manager_script = os.path.join(script_dir, "server_manager.py")
    
    if not os.path.exists(manager_script):
        messagebox.showerror("Error", "No se encontró el archivo server_manager.py. Asegúrate de que esté en el mismo directorio que este instalador.")
        return False
    
    return True

def install_dependencies():
    try:
        # Verificar que tkinter está disponible (viene con Python, no es un paquete pip)
        import tkinter
        return True
    except ImportError:
        messagebox.showerror("Error de dependencias", 
                           "No se encontró tkinter, que es necesario para esta aplicación.\n\n"
                           "tkinter viene incluido con la instalación estándar de Python, pero parece que "
                           "no está disponible en tu sistema.\n\n"
                           "Para solucionar esto:\n"
                           "- En Ubuntu/Debian: sudo apt-get install python3-tk\n"
                           "- En Fedora: sudo dnf install python3-tkinter\n"
                           "- En macOS: Reinstala Python desde python.org\n"
                           "- En Windows: Reinstala Python y asegúrate de marcar la opción 'tcl/tk and IDLE'")
        return False

def create_shortcut(target_script, output_path, shortcut_name):
    """Crea un acceso directo al script"""
    if platform.system() == "Windows":
        try:
            # En Windows, crear un archivo .bat
            bat_path = os.path.join(output_path, f"{shortcut_name}.bat")
            with open(bat_path, 'w') as bat_file:
                bat_file.write(f'@echo off\n')
                bat_file.write(f'start pythonw "{target_script}"\n')
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el acceso directo: {str(e)}")
            return False
    else:
        try:
            # En Linux/Mac, crear un archivo .sh
            sh_path = os.path.join(output_path, f"{shortcut_name}.sh")
            with open(sh_path, 'w') as sh_file:
                sh_file.write(f'#!/bin/bash\n')
                sh_file.write(f'python3 "{target_script}" &\n')
            # Hacer el archivo ejecutable
            os.chmod(sh_path, 0o755)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el acceso directo: {str(e)}")
            return False

def get_desktop_path():
    """Obtiene la ruta del escritorio del usuario"""
    if platform.system() == "Windows":
        return os.path.join(os.path.expanduser("~"), "Desktop")
    else:
        return os.path.join(os.path.expanduser("~"), "Desktop")

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instalador del Gestor de Servidor Flask")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Variables
        self.install_path = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "FlaskServerManager"))
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        
        # Crear interface
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Instalador del Gestor de Servidor Flask", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Ruta de instalación
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(path_frame, text="Ruta de instalación:").pack(side=tk.LEFT)
        ttk.Entry(path_frame, textvariable=self.install_path, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(path_frame, text="...", width=3, command=self.browse_path).pack(side=tk.LEFT)
        
        # Opciones
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        ttk.Checkbutton(options_frame, text="Crear acceso directo en el escritorio", 
                      variable=self.create_desktop_shortcut).pack(anchor=tk.W)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="Instalar", command=self.install, 
                 style="Accent.TButton", width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.root.destroy, 
                 width=15).pack(side=tk.RIGHT, padx=5)
        
        # Configurar estilo para el botón de Instalar
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#007bff")
    
    def browse_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Seleccionar carpeta de instalación")
        if path:
            self.install_path.set(path)
    
    def install(self):
        # Verificar archivos requeridos
        if not check_required_files():
            return
        
        # Obtener la ruta de instalación
        install_path = self.install_path.get()
        
        # Crear directorio si no existe
        try:
            os.makedirs(install_path, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el directorio de instalación: {str(e)}")
            return
        
        # Instalar dependencias
        if not install_dependencies():
            return
        
        # Copiar archivos
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            manager_script = os.path.join(script_dir, "server_manager.py")
            shutil.copy2(manager_script, install_path)
            
            messagebox.showinfo("Éxito", "Instalación completada con éxito.")
            
            # Crear acceso directo si está seleccionado
            if self.create_desktop_shortcut.get():
                target = os.path.join(install_path, "server_manager.py")
                create_shortcut(target, get_desktop_path(), "Gestor Servidor Flask")
            
            # Preguntamos si quiere abrir la aplicación
            if messagebox.askyesno("Instalación completada", 
                                 "¿Desea abrir el Gestor de Servidor Flask ahora?"):
                # Ejecutar la aplicación
                target = os.path.join(install_path, "server_manager.py")
                subprocess.Popen([sys.executable, target])
            
            # Cerrar instalador
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la instalación: {str(e)}")

def main():
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()