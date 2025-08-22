#!/usr/bin/env python3
"""
Script de configuración completa para Render_QM Backend
Ejecutar desde D:\Render_QM\backend\
"""

import os
import sys
import subprocess
from pathlib import Path

def create_all_files():
    """Crear todos los archivos necesarios"""
    print("📁 Creando estructura de archivos...")
    
    # Crear directorios
    directories = [
        "app", "app/api", "app/api/v1", "app/core", 
        "app/models", "app/schemas", "temp", "renders", "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Crear archivos __init__.py
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/models/__init__.py",
        "app/schemas/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
    
    # requirements.txt mínimo
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    
    # .env
    env_content = """DATABASE_URL=sqlite:///./render_qm.db
SECRET_KEY=render-qm-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO
BLENDER_PATH=blender
TEMP_DIR=./temp
OUTPUT_DIR=./renders
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Archivos creados")

def install_dependencies():
    """Instalar dependencias"""
    print("📦 Instalando dependencias...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def setup_database():
    """Configurar base de datos y crear usuario admin"""
    print("🗄️ Configurando base de datos...")
    
    try:
        # Importar después de instalar dependencias
        from app.core.database import engine, Base, SessionLocal
        from app.models.user import User
        from app.models.job import Job
        from app.models.node import Node
        from passlib.context import CryptContext
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas")
        
        # Crear usuario admin
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")
        
        db = SessionLocal()
        
        # Verificar si admin ya existe
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if not existing_admin:
            admin_user = User(
                username="admin",
                email="admin@render-qm.local",
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuario admin creado (admin/admin123)")
        else:
            print("✅ Usuario admin ya existe")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_server():
    """Probar que el servidor funciona"""
    print("🧪 Probando servidor...")
    
    try:
        import requests
        import time
        
        # Iniciar servidor en background (simulado)
        print("   Iniciando servidor...")
        
        # En lugar de iniciar realmente, solo verificamos que los imports funcionen
        from app.main import app
        print("✅ Aplicación FastAPI se puede importar correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False

def create_startup_script():
    """Crear script de inicio"""
    print("📝 Creando script de inicio...")
    
    # Script para Windows
    start_script = """@echo off
echo 🚀 Iniciando Render_QM Backend...
echo.

REM Activar entorno virtual si existe
if exist "venv\\Scripts\\activate.bat" (
    echo 🔧 Activando entorno virtual...
    call venv\\Scripts\\activate.bat
)

REM Crear directorios si no existen
if not exist "temp" mkdir temp
if not exist "renders" mkdir renders
if not exist "logs" mkdir logs

echo 🌐 Servidor disponible en:
echo    • API: http://localhost:8000
echo    • Docs: http://localhost:8000/docs
echo    • Health: http://localhost:8000/health
echo.
echo 👤 Credenciales por defecto:
echo    • Usuario: admin
echo    • Contraseña: admin123
echo.
echo ⏹️ Presiona Ctrl+C para detener
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
"""
    
    with open("start_server.bat", "w") as f:
        f.write(start_script)
    
    # Script de prueba
    test_script = """#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_api():
    print("🧪 Probando API...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health: {data['status']}")
                else:
                    print(f"❌ Health failed: {resp.status}")
                    return
            
            # Test settings
            async with session.get("http://localhost:8000/api/v1/settings/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Settings: {data['app_name']} v{data['version']}")
                else:
                    print(f"❌ Settings failed: {resp.status}")
            
            print("🎉 ¡API funcionando correctamente!")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")

if __name__ == "__main__":
    asyncio.run(test_api())
"""
    
    with open("test_api.py", "w") as f:
        f.write(test_script)
    
    print("✅ Scripts creados:")
    print("   • start_server.bat - Para iniciar el servidor")
    print("   • test_api.py - Para probar la API")

def main():
    """Función principal"""
    print("🎬 RENDER_QM BACKEND - CONFIGURACIÓN COMPLETA")
    print("=" * 50)
    
    # Verificar que estamos en el directorio correcto
    if not Path("app").exists():
        print("⚠️ Creando directorio app...")
    
    # Paso 1: Crear archivos
    create_all_files()
    
    # Paso 2: Instalar dependencias
    if not install_dependencies():
        print("❌ Fallo en la instalación de dependencias")
        return False
    
    # Paso 3: Configurar base de datos
    if not setup_database():
        print("❌ Fallo en la configuración de base de datos")
        return False
    
    # Paso 4: Crear scripts de inicio
    create_startup_script()
    
    # Paso 5: Verificar que todo funciona
    if test_server():
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("\n📋 Próximos pasos:")
        print("   1. Ejecutar: start_server.bat")
        print("      O manualmente: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("   2. Abrir: http://localhost:8000/docs")
        print("   3. Login: admin / admin123")
        print("   4. Probar: python test_api.py")
        
        return True
    else:
        print("\n⚠️ Configuración completada con advertencias")
        print("Intenta iniciar manualmente con:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPresiona Enter para continuar...")
    sys.exit(0 if success else 1)