import os
import sys

# --- CONFIGURACIÓN ---
# Directorios y extensiones a ignorar para mantener el reporte limpio
IGNORED_DIRS = ('.git', 'node_modules', '__pycache__', 'venv', 'dist', 'build')
IGNORED_FILES = ('.DS_Store',)
# ---------------------

def generate_report(start_path):
    """Genera una estructura de árbol legible de directorios y archivos."""
    print("--- 📂 REPORTE DE ESTRUCTURA DEL REPOSITORIO (Render_QM) ---")
    
    for root, dirs, files in os.walk(start_path):
        # Modificar dirs in-place para podar la búsqueda
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        
        # Calcular el nivel de profundidad
        level = root.replace(start_path, '').count(os.sep)
        
        # Determinar la indentación
        indent = '│   ' * level
        
        # Imprimir el nombre de la carpeta actual (si no es la raíz)
        if root != start_path:
            folder_name = os.path.basename(root)
            print(f"{indent}├── **{folder_name}**/")

        # Aumentar la indentación para los archivos
        sub_indent = '│   ' * (level + 1)
        
        # Imprimir los archivos
        for f in files:
            if f not in IGNORED_FILES:
                # Usar └── solo para el último elemento o un carácter especial para archivos
                print(f"{sub_indent}— {f}")

if __name__ == "__main__":
    # La ruta de inicio es donde se ejecuta el script
    root_dir = os.getcwd()
    generate_report(root_dir)

    print("\n-------------------------------------------------------------")
    print("Por favor, compárteme la salida de este script.")