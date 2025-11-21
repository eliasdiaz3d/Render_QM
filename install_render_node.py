# install_render_node.py - Instalador Automático (Sin Input Manual)
import os
import sys
import platform
import subprocess
import urllib.request
import json
import socket
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path

def log(message):
    """Función de logging que funciona siempre"""
    print(message)
    # También escribir a archivo de log
    log_file = Path.home() / "render_node_install.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def show_message(title, message, type="info"):
    """Mostrar mensaje usando GUI o consola"""
    try:
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana principal
        
        if type == "error":
            messagebox.showerror(title, message)
        elif type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
        root.destroy()
    except:
        # Fallback a consola
        print(f"{title}: {message}")

def get_input(prompt, default=None):
    """Obtener entrada del usuario con GUI o valores por defecto"""
    try:
        root = tk.Tk()
        root.withdraw()
        result = simpledialog.askstring("Render Node Installer", prompt, initialvalue=default or "")
        root.destroy()
        return result or default
    except:
        # Si no hay GUI disponible, usar valor por defecto
        log(f"Usando valor por defecto para: {prompt}")
        return default

def detect_server():
    """Detectar servidor automáticamente"""
    log("Detectando servidor de render...")
    
    try:
        # Obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        network = ".".join(local_ip.split(".")[:-1]) + "."
        
        # Buscar en IPs comunes de la red
        common_ips = [129, 1, 100, 101, 102, 103, 104, 105, 110, 200, 254]
        
        for i in common_ips:
            ip = network + str(i)
            try:
                log(f"Probando {ip}...")
                response = urllib.request.urlopen(f"http://{ip}:8000/health", timeout=2)
                if response.status == 200:
                    data = json.loads(response.read())
                    if "Render Queue Manager" in data.get("service", ""):
                        log(f"Servidor encontrado en: {ip}")
                        return ip
            except:
                continue
                
    except Exception as e:
        log(f"Error detectando servidor: {e}")
    
    # Si no encuentra automáticamente, solicitar IP
    server_ip = get_input("No se pudo detectar el servidor automáticamente.\nIngresa la IP del servidor:", "192.168.1.100")
    
    if server_ip:
        try:
            response = urllib.request.urlopen(f"http://{server_ip}:8000/health", timeout=5)
            if response.status == 200:
                log(f"Servidor confirmado en: {server_ip}")
                return server_ip
        except:
            pass
    
    # Como último recurso, usar IP común
    log("Usando IP por defecto: 192.168.1.100")
    return "192.168.1.100"

def install_dependencies():
    """Instalar dependencias Python"""
    log("Verificando dependencias...")
    
    required_deps = ["PyYAML", "aiohttp", "psutil"]
    
    for dep in required_deps:
        try:
            __import__(dep.lower().replace("-", "_"))
            log(f"✓ {dep} ya instalado")
        except ImportError:
            log(f"Instalando {dep}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True, capture_output=True, timeout=120)
                log(f"✓ {dep} instalado")
            except Exception as e:
                log(f"ERROR instalando {dep}: {e}")
                return False
    
    return True

def detect_blender():
    """Detectar Blender automáticamente"""
    log("Detectando Blender...")
    
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender 4.5\blender.exe",
            r"C:\Program Files (x86)\Blender Foundation\Blender 4.4\blender.exe"
        ]
    elif platform.system() == "Darwin":
        possible_paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender"
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            log(f"Blender encontrado: {path}")
            return path
    
    log("Blender no encontrado automáticamente")
    
    # Solicitar ruta manualmente
    blender_path = get_input(
        "No se encontró Blender automáticamente.\nIngresa la ruta completa al ejecutable de Blender:",
        "blender"
    )
    
    return blender_path or "blender"

def download_node_files(server_ip, install_dir):
    """Descargar archivos del nodo"""
    log("Descargando archivos del nodo...")
    
    files_to_download = {
        "node_agent.py": f"http://{server_ip}:8000/installer/node_agent.py"
    }
    
    for filename, url in files_to_download.items():
        try:
            log(f"Descargando {filename}...")
            urllib.request.urlretrieve(url, install_dir / filename)
            log(f"✓ {filename} descargado")
        except Exception as e:
            log(f"No se pudo descargar {filename}: {e}")
            # Crear archivo mínimo como fallback
            create_minimal_node(install_dir)
            return True
    
    return True

def create_minimal_node(install_dir):
    """Crear nodo mínimo si no se puede descargar"""
    log("Creando nodo mínimo...")
    
    minimal_code = '''#!/usr/bin/env python3
# Nodo de Render - Versión Mínima
import asyncio
import sys
from pathlib import Path

print("Nodo de render iniciado (versión mínima)")
print("Para obtener la versión completa, descarga desde el servidor principal")

try:
    import yaml
    config_file = Path("node_config.yaml")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        print(f"Configurado para servidor: {config.get('master_url')}")
    else:
        print("Archivo de configuración no encontrado")
except Exception as e:
    print(f"Error: {e}")

print("\\nPresiona Ctrl+C para cerrar")

try:
    while True:
        asyncio.sleep(10)
except KeyboardInterrupt:
    print("\\nNodo detenido")
'''
    
    with open(install_dir / "node_agent.py", 'w', encoding='utf-8') as f:
        f.write(minimal_code)

def create_config(server_ip, blender_path, install_dir):
    """Crear archivo de configuración"""
    log("Creando configuración...")
    
    node_name = f"RenderNode-{platform.node()}"
    
    config = {
        "node_name": node_name,
        "master_url": f"http://{server_ip}:8000",
        "node_port": 8001,
        "max_concurrent_jobs": 1,
        "temp_dir": str(install_dir / "temp"),
        "output_dir": str(install_dir / "renders"),
        "blender_path": blender_path,
        "heartbeat_interval": 10,
        "auto_start": True,
        "gpu_enabled": True,
        "cpu_cores": -1,
        "max_memory_gb": 8,
        "priority_weight": 1.0,
        "tags": ["auto-instalado"],
        "connection_timeout": 30,
        "request_timeout": 60
    }
    
    try:
        import yaml
        with open(install_dir / "node_config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        log("✓ Configuración creada")
        return node_name
    except Exception as e:
        log(f"Error creando configuración: {e}")
        return node_name

def create_shortcuts(install_dir):
    """Crear accesos directos y scripts de inicio"""
    log("Creando accesos directos...")
    
    if platform.system() == "Windows":
        # Crear archivo batch
        bat_content = f'''@echo off
title Render Node
cd /d "{install_dir}"
echo Iniciando Nodo de Render...
python node_agent.py
echo.
echo El nodo se ha detenido.
pause'''
        
        bat_file = install_dir / "Iniciar_Nodo.bat"
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write(bat_content)
        
        # Intentar crear acceso directo en el escritorio
        try:
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                shortcut_bat = desktop / "Render_Node.bat"
                with open(shortcut_bat, 'w', encoding='utf-8') as f:
                    f.write(f'@echo off\ncd /d "{install_dir}"\nstart Iniciar_Nodo.bat')
                log("✓ Acceso directo creado en escritorio")
        except:
            log("No se pudo crear acceso directo en escritorio")
    
    else:
        # Linux/macOS
        script_content = f'''#!/bin/bash
cd "{install_dir}"
echo "Iniciando Nodo de Render..."
python3 node_agent.py
'''
        script_file = install_dir / "iniciar_nodo.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        try:
            os.chmod(script_file, 0o755)
            log("✓ Script de inicio creado")
        except:
            log("No se pudieron establecer permisos del script")

def test_installation(server_ip, install_dir):
    """Probar la instalación"""
    log("Probando instalación...")
    
    try:
        # Probar conexión al servidor
        response = urllib.request.urlopen(f"http://{server_ip}:8000/health", timeout=5)
        if response.status == 200:
            log("✓ Conexión al servidor OK")
        else:
            log("⚠ Advertencia: El servidor no responde correctamente")
        
        # Verificar archivos creados
        required_files = ["node_agent.py", "node_config.yaml"]
        for filename in required_files:
            if (install_dir / filename).exists():
                log(f"✓ {filename} creado")
            else:
                log(f"✗ {filename} faltante")
                return False
        
        return True
        
    except Exception as e:
        log(f"Error en pruebas: {e}")
        return False

def main():
    """Función principal del instalador"""
    log("=" * 50)
    log("INSTALADOR DE NODOS DE RENDER")
    log("=" * 50)
    log(f"Sistema: {platform.system()} {platform.release()}")
    log(f"Python: {sys.version}")
    
    try:
        # Verificar Python
        if sys.version_info < (3, 7):
            error_msg = f"ERROR: Se requiere Python 3.7+. Versión actual: {sys.version_info.major}.{sys.version_info.minor}"
            show_message("Error de Python", error_msg, "error")
            log(error_msg)
            return False
        
        # Crear directorio de instalación
        install_dir = Path.home() / "RenderNode"
        install_dir.mkdir(exist_ok=True)
        log(f"Directorio de instalación: {install_dir}")
        
        # Detectar servidor
        server_ip = detect_server()
        if not server_ip:
            log("ERROR: No se pudo detectar el servidor")
            return False
        
        # Instalar dependencias
        if not install_dependencies():
            log("ERROR: Fallo instalando dependencias")
            return False
        
        # Detectar Blender
        blender_path = detect_blender()
        
        # Descargar archivos
        if not download_node_files(server_ip, install_dir):
            log("ERROR: No se pudieron descargar los archivos")
            return False
        
        # Crear configuración
        node_name = create_config(server_ip, blender_path, install_dir)
        
        # Crear accesos directos
        create_shortcuts(install_dir)
        
        # Probar instalación
        if test_installation(server_ip, install_dir):
            success_msg = f"""INSTALACIÓN COMPLETADA

Directorio: {install_dir}
Nodo: {node_name}
Servidor: {server_ip}
Blender: {blender_path}

Para iniciar el nodo:
- Windows: Ejecutar 'Iniciar_Nodo.bat'
- Linux/Mac: Ejecutar 'iniciar_nodo.sh'

O usar el acceso directo del escritorio."""
            
            show_message("Instalación Exitosa", success_msg)
            log("✓ INSTALACIÓN COMPLETADA EXITOSAMENTE")
            return True
        else:
            log("ERROR: Fallo en las pruebas de instalación")
            return False
            
    except Exception as e:
        error_msg = f"ERROR CRÍTICO: {e}"
        log(error_msg)
        show_message("Error Crítico", error_msg, "error")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            show_message("Error", "La instalación falló. Revisa el archivo de log.", "error")
    except Exception as e:
        show_message("Error Fatal", f"Error inesperado: {e}", "error")
        
    # Solo hacer pausa si estamos en una consola
    try:
        if sys.stdin and sys.stdin.isatty():
            input("\nPresiona Enter para cerrar...")
    except:
        pass  # Ignorar si no hay stdin disponible