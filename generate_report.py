import os
import ast
import datetime

# --- CONFIGURACIÓN ---
# Carpetas a ignorar para que el reporte no sea gigante
IGNORE_DIRS = {
    'venv', '.git', '__pycache__', 'node_modules', 'dist', 'build', 
    '.idea', '.vscode', 'site-packages', 'Include', 'Lib', 'Scripts'
}
OUTPUT_FILE = "REPORTE_ESTRUCTURA.md"

def get_file_info(file_path):
    """Analiza un archivo Python y extrae imports, clases y funciones."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return "**Error de Sintaxis al leer este archivo**"

    info = []
    
    # Extraer Imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            for n in node.names:
                imports.append(f"{module}.{n.name}")
    
    if imports:
        info.append(f"**Librerías/Imports:** `{', '.join(sorted(list(set(imports))))}`")

    # Extraer Clases y Funciones
    info.append("\n**Estructura del Código:**")
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            info.append(f"- 🏛️ **Clase:** `{node.name}`")
            # Docstring de clase
            doc = ast.get_docstring(node)
            if doc:
                info.append(f"  - *Descripción:* {doc.strip().splitlines()[0]}")
            
            # Métodos dentro de la clase
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    info.append(f"  - 🔹 Método: `{item.name}`")

        elif isinstance(node, ast.FunctionDef):
            info.append(f"- ⚡ **Función:** `{node.name}`")
            doc = ast.get_docstring(node)
            if doc:
                info.append(f"  - *Descripción:* {doc.strip().splitlines()[0]}")
            
            # Detectar decoradores clave (como @app.get o @celery.task)
            if node.decorator_list:
                decorators = []
                for dec in node.decorator_list:
                    if isinstance(dec, ast.Name):
                        decorators.append(f"@{dec.id}")
                    elif isinstance(dec, ast.Attribute):
                        decorators.append(f"@{dec.attr}")
                    elif isinstance(dec, ast.Call):
                         # Intentar obtener el nombre de decoradores complejos
                         try:
                             if isinstance(dec.func, ast.Name):
                                 decorators.append(f"@{dec.func.id}(...)")
                             elif isinstance(dec.func, ast.Attribute):
                                 decorators.append(f"@{dec.func.attr}(...)")
                         except:
                             pass
                if decorators:
                    info.append(f"    *Decoradores:* {' '.join(decorators)}")

    return "\n".join(info)

def generate_tree(startpath):
    """Genera un árbol visual de directorios."""
    tree_str = "## 🌳 Árbol de Directorios\n```text\n"
    for root, dirs, files in os.walk(startpath):
        # Filtrar directorios ignorados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = '│   ' * (level)
        subindent = '│   ' * (level + 1)
        
        folder_name = os.path.basename(root)
        if folder_name == '': folder_name = '.'
        
        tree_str += f"{indent}📁 {folder_name}/\n"
        
        for f in files:
            if f.endswith('.py') or f.endswith('.js') or f.endswith('.json') or f == 'Dockerfile':
                tree_str += f"{subindent}📄 {f}\n"
    tree_str += "```\n"
    return tree_str

def main():
    root_dir = os.getcwd()
    print(f"🔍 Analizando proyecto en: {root_dir}")
    
    report = [f"# Reporte de Estructura del Proyecto: Render_QM"]
    report.append(f"**Fecha:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. Árbol de directorios
    report.append(generate_tree(root_dir))
    
    # 2. Análisis detallado de archivos Python
    report.append("## 🐍 Análisis Detallado de Backend (.py)\n")
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                print(f"   Analizando: {rel_path}...")
                
                report.append(f"### 📄 `{rel_path}`")
                content_analysis = get_file_info(file_path)
                if content_analysis.strip():
                    report.append(content_analysis)
                else:
                    report.append("*Archivo vacío o sin definiciones de alto nivel.*")
                report.append("\n---\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"\n✅ ¡Listo! Reporte guardado en: {OUTPUT_FILE}")
    print("👉 Por favor, revisa ese archivo o compártelo para depurar.")

if __name__ == "__main__":
    main()