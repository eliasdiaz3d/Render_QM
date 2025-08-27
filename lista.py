import os

def listar_directorio_a_txt(ruta_directorio, nombre_archivo_salida):
    """
    Recorre un directorio y guarda los nombres de las carpetas y archivos en un archivo .txt.

    Args:
        ruta_directorio (str): La ruta al directorio que quieres listar.
        nombre_archivo_salida (str): El nombre del archivo .txt donde se guardará la lista.
    """
    try:
        # Abre el archivo de salida en modo de escritura ('w')
        with open(nombre_archivo_salida, 'w', encoding='utf-8') as archivo_salida:
            # os.walk() recorre el árbol de directorios
            for ruta_actual, carpetas, archivos in os.walk(ruta_directorio):
                # Escribe la ruta del directorio actual
                archivo_salida.write(f"Directorio: {ruta_actual}\n")
                
                # Escribe los nombres de las subcarpetas
                for nombre_carpeta in carpetas:
                    archivo_salida.write(f"\t- Carpeta: {nombre_carpeta}\n")
                    
                # Escribe los nombres de los archivos
                for nombre_archivo in archivos:
                    archivo_salida.write(f"\t- Archivo: {nombre_archivo}\n")
                
                archivo_salida.write("\n") # Añade una línea en blanco para separar los directorios
                
        print(f"¡Éxito! La lista de directorios y archivos se ha guardado en '{nombre_archivo_salida}'")

    except FileNotFoundError:
        print(f"Error: El directorio '{ruta_directorio}' no fue encontrado.")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

# --- Cómo usar el script ---

# 1. Especifica la ruta del directorio que quieres analizar.
#    - Puedes usar una ruta absoluta (ej. "C:/Usuarios/TuUsuario/Documentos")
#    - o una ruta relativa (ej. "." para el directorio actual).
directorio_a_escanear = "D:\Render_QM" 

# 2. Especifica el nombre que quieres darle al archivo de texto de salida.
archivo_txt_de_salida = "lista_de_archivos.txt"

# 3. Llama a la función con los parámetros que definiste.
listar_directorio_a_txt(directorio_a_escanear, archivo_txt_de_salida)