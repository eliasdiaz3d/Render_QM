#!/usr/bin/env python3
"""
Script para crear archivos faltantes en Windows
Ejecutar desde D:\Render_QM\backend\
"""

import os
from pathlib import Path

def create_file(filepath, content=""):
    """Crear archivo con contenido"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Creado: {filepath}")

def main():
    print("🔧 Creando archivos faltantes para Render_QM...")
    
    # Archivos __init__.py necesarios
    init_files = [
        "app/__init__.py",
        "app/api/__init__.py", 
        "app/api/v1/__init__.py",
        "app/core/__init__.py",
        "app/models/__init__.py",
        "app/services/__init__.py",
        "app/schemas/__init__.py"
    ]
    
    for file_path in init_files:
        create_file(file_path, "")
    
    # requirements.txt
    requirements_content = """fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiofiles==23.2.1
aiohttp==3.9.1
python-dotenv==1.0.0
websockets==12.0
"""
    
    create_file("requirements.txt", requirements_content)
    
    # .env básico
    env_content = """# Render_QM Configuration
DATABASE_URL=sqlite:///./render_qm.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=render-qm-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO
BLENDER_PATH=blender
TEMP_DIR=./temp
OUTPUT_DIR=./renders
"""
    
    create_file(".env", env_content)
    
    # Script de inicio rápido para Windows
    start_script = """@echo off
echo 🚀 Iniciando Render_QM Backend...

REM Verificar si existe el entorno virtual
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\\Scripts\\activate

REM Instalar dependencias
echo 📥 Instalando dependencias...
pip install -r requirements.txt

REM Crear directorios necesarios
if not exist "temp" mkdir temp
if not exist "renders" mkdir renders
if not exist "logs" mkdir logs

REM Iniciar servidor
echo 🌐 Iniciando servidor en http://localhost:8000
echo 📖 Documentación en http://localhost:8000/docs
echo 👤 Usuario: admin | Contraseña: admin123
echo.
echo ⏹️ Presiona Ctrl+C para detener el servidor
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
"""
    
    create_file("start_server.bat", start_script)
    
    # Script de configuración inicial
    setup_script = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def setup_database():
    print("🗄️ Configurando base de datos...")
    try:
        # Importar después de instalar dependencias
        from app.core.database import engine, Base
        from app.models.job import Job
        from app.models.node import Node  
        from app.models.user import User
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✓ Tablas creadas")
        
        # Crear usuario admin
        from app.core.database import SessionLocal
        from passlib.context import CryptContext
        
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
            print("✓ Usuario admin creado")
        else:
            print("✓ Usuario admin ya existe")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

def create_directories():
    dirs = ["temp", "renders", "logs"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directorio: {directory}/")

if __name__ == "__main__":
    print("⚙️ Configuración inicial de Render_QM")
    print("=" * 40)
    
    create_directories()
    
    if setup_database():
        print("\\n🎉 Configuración completada!")
        print("Ahora puedes iniciar el servidor con:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\\n❌ Error en la configuración")
"""
    
    create_file("setup_initial.py", setup_script)
    
    # Script de prueba simple
    test_script = """#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_api():
    print("🧪 Probando API de Render_QM...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test health
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check: {data['status']}")
                else:
                    print(f"❌ Health check falló: {resp.status}")
                    return
            
            # Test login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            async with session.post(
                "http://localhost:8000/api/v1/auth/login",
                data=login_data
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data["access_token"]
                    print("✅ Login exitoso")
                    
                    # Test authenticated endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(
                        "http://localhost:8000/api/v1/settings/",
                        headers=headers
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"✅ Settings: {data['app_name']} v{data['version']}")
                        else:
                            print(f"❌ Settings falló: {resp.status}")
                else:
                    print(f"❌ Login falló: {resp.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")

if __name__ == "__main__":
    asyncio.run(test_api())
"""
    
    create_file("test_simple.py", test_script)
    
    print("\n🎉 Archivos creados exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar: start_server.bat")
    print("   O manualmente:")
    print("   - pip install -r requirements.txt")
    print("   - python setup_initial.py")
    print("   - uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n2. Probar: python test_simple.py")
    print("\n3. Abrir: http://localhost:8000/docs")

if __name__ == "__main__":
    main()