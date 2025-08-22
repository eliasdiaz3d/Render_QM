#!/usr/bin/env python3
"""
Script para probar el backend de Render_QM
Ejecutar: python test_backend.py
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuración del servidor
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

class RenderQMTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health(self):
        """Test health endpoint"""
        print("🏥 Probando health check...")
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                data = await response.json()
                print(f"   ✅ Status: {data['status']}")
                return response.status == 200
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_auth(self):
        """Test authentication"""
        print("🔐 Probando autenticación...")
        try:
            # Intentar login con credenciales por defecto
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            async with self.session.post(
                f"{API_URL}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"   ✅ Login exitoso, token obtenido")
                    return True
                else:
                    print(f"   ❌ Login fallido: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error en login: {e}")
            return False
    
    def get_auth_headers(self):
        """Obtener headers de autenticación"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_node_registration(self):
        """Test node registration"""
        print("🖥️ Probando registro de nodo...")
        try:
            node_data = {
                "name": "test_node_01",
                "hostname": "test-machine",
                "ip_address": "192.168.1.100",
                "port": 8080,
                "cpu_cores": 8,
                "memory_total": 16.0,
                "gpu_count": 1,
                "max_concurrent_jobs": 2,
                "blender_version": "4.0.0",
                "supported_engines": ["CYCLES", "EEVEE"]
            }
            
            async with self.session.post(
                f"{API_URL}/nodes/register",
                json=node_data,
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Nodo registrado: {data['name']} (ID: {data['id']})")
                    return data['id']
                else:
                    error_data = await response.json()
                    print(f"   ❌ Error registrando nodo: {error_data.get('detail', 'Error desconocido')}")
                    return None
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    async def test_job_submission(self):
        """Test job submission"""
        print("📋 Probando envío de trabajo...")
        try:
            job_data = {
                "name": "Test Render Job",
                "description": "Trabajo de prueba para validar el sistema",
                "scene_path": "/tmp/test_scene.blend",
                "priority": 5,
                "frame_start": 1,
                "frame_end": 10,
                "engine": "CYCLES",
                "samples": 128,
                "resolution_x": 1920,
                "resolution_y": 1080,
                "notification_email": "test@example.com"
            }
            
            async with self.session.post(
                f"{API_URL}/jobs/submit",
                json=job_data,
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Trabajo enviado: {data['name']} (ID: {data['id']})")
                    return data['id']
                else:
                    error_data = await response.json()
                    print(f"   ❌ Error enviando trabajo: {error_data.get('detail', 'Error desconocido')}")
                    return None
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    async def test_queue_status(self):
        """Test queue status"""
        print("📊 Probando estado de cola...")
        try:
            async with self.session.get(
                f"{API_URL}/queue/status",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Estado de cola: {data['queue_status']}")
                    print(f"      - Trabajos pendientes: {data['pending_jobs']}")
                    print(f"      - Trabajos ejecutándose: {data['running_jobs']}")
                    print(f"      - Nodos disponibles: {data['available_nodes']}")
                    return True
                else:
                    print(f"   ❌ Error obteniendo estado: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_node_heartbeat(self, node_id):
        """Test node heartbeat"""
        print("💓 Probando heartbeat de nodo...")
        try:
            stats_data = {
                "cpu_usage": 45.5,
                "memory_usage": 8.2,
                "gpu_usage": 0.0,
                "disk_space_free": 250.0,
                "current_jobs": 0
            }
            
            async with self.session.post(
                f"{API_URL}/nodes/{node_id}/heartbeat",
                json=stats_data,
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Heartbeat recibido: {data['message']}")
                    print(f"      - Estado del nodo: {data['node_status']}")
                    print(f"      - Disponible: {data['is_available']}")
                    return True
                else:
                    print(f"   ❌ Error en heartbeat: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def test_settings(self):
        """Test settings endpoint"""
        print("⚙️ Probando configuraciones...")
        try:
            async with self.session.get(
                f"{API_URL}/settings/",
                headers=self.get_auth_headers()
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Configuraciones obtenidas:")
                    print(f"      - App: {data['app_name']} v{data['version']}")
                    print(f"      - Debug: {data['debug']}")
                    print(f"      - Max workers: {data['max_workers']}")
                    print(f"      - Blender path: {data['blender_path']}")
                    
                    features = data.get('features', {})
                    print(f"      - Funcionalidades:")
                    for feature, enabled in features.items():
                        status = "✅" if enabled else "❌"
                        print(f"        {status} {feature}")
                    
                    return True
                else:
                    print(f"   ❌ Error obteniendo configuraciones: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Iniciando pruebas del backend Render_QM")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Health check
        results['health'] = await self.test_health()
        
        # Test 2: Authentication
        results['auth'] = await self.test_auth()
        
        if not results['auth']:
            print("\n❌ No se pudo autenticar, saltando pruebas que requieren auth")
            return results
        
        # Test 3: Settings
        results['settings'] = await self.test_settings()
        
        # Test 4: Node registration
        node_id = await self.test_node_registration()
        results['node_registration'] = node_id is not None
        
        # Test 5: Node heartbeat (si se registró el nodo)
        if node_id:
            results['node_heartbeat'] = await self.test_node_heartbeat(node_id)
        
        # Test 6: Job submission
        job_id = await self.test_job_submission()
        results['job_submission'] = job_id is not None
        
        # Test 7: Queue status
        results['queue_status'] = await self.test_queue_status()
        
        return results

async def main():
    """Función principal"""
    try:
        async with RenderQMTester() as tester:
            results = await tester.run_all_tests()
            
            print("\n" + "=" * 50)
            print("📊 RESUMEN DE PRUEBAS")
            print("=" * 50)
            
            passed = sum(1 for result in results.values() if result)
            total = len(results)
            
            for test_name, result in results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{status} {test_name}")
            
            print(f"\nResultado: {passed}/{total} pruebas exitosas")
            
            if passed == total:
                print("🎉 ¡Todas las pruebas pasaron! El backend está funcionando correctamente.")
            else:
                print("⚠️ Algunas pruebas fallaron. Revisa la configuración del servidor.")
            
            return passed == total
            
    except Exception as e:
        print(f"❌ Error general en las pruebas: {e}")
        return False

async def test_websocket():
    """Probar conexión WebSocket"""
    print("\n🔌 Probando WebSocket...")
    try:
        import websockets
        
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("   ✅ Conexión WebSocket establecida")
            
            # Esperar mensaje de heartbeat
            message = await asyncio.wait_for(websocket.recv(), timeout=35)
            data = json.loads(message)
            
            if data.get('type') == 'heartbeat':
                print(f"   ✅ Heartbeat recibido: {data['timestamp']}")
                return True
            else:
                print(f"   ⚠️ Mensaje inesperado: {data}")
                return False
                
    except ImportError:
        print("   ⚠️ websockets no instalado, saltando prueba WebSocket")
        return True
    except Exception as e:
        print(f"   ❌ Error en WebSocket: {e}")
        return False

def check_requirements():
    """Verificar que el servidor esté disponible"""
    print("🔍 Verificando disponibilidad del servidor...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("   ✅ Servidor disponible en localhost:8000")
            return True
        else:
            print("   ❌ Servidor no disponible en localhost:8000")
            print("   💡 Asegúrate de que el servidor esté ejecutándose:")
            print("      cd backend && uvicorn app.main:app --reload")
            return False
            
    except Exception as e:
        print(f"   ❌ Error verificando servidor: {e}")
        return False

if __name__ == "__main__":
    print("🧪 RENDER_QM BACKEND TESTER")
    print("=" * 50)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que el servidor esté disponible
    if not check_requirements():
        exit(1)
    
    # Ejecutar pruebas principales
    success = asyncio.run(main())
    
    # Probar WebSocket
    websocket_success = asyncio.run(test_websocket())
    
    print("\n" + "=" * 50)
    if success and websocket_success:
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\n💡 El backend está listo para usar:")
        print("   • API REST: http://localhost:8000/docs")
        print("   • WebSocket: ws://localhost:8000/ws")
        print("   • Health: http://localhost:8000/health")
        exit(0)
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("\n🔧 Pasos para solucionar problemas:")
        print("   1. Verificar que el servidor esté ejecutándose")
        print("   2. Revisar logs del servidor")
        print("   3. Verificar configuración en .env")
        print("   4. Comprobar base de datos")
        exit(1)


# ========== SCRIPT ADICIONAL: run_backend.py ==========
"""
Script para ejecutar el backend con configuración automática
"""
#!/usr/bin/env python3

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def setup_environment():
    """Configurar entorno inicial"""
    print("🔧 Configurando entorno...")
    
    # Crear directorios necesarios
    directories = [
        "temp",
        "renders", 
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✓ {directory}/")
    
    # Crear archivo .env si no existe
    env_file = Path(".env")
    if not env_file.exists():
        print("   📝 Creando archivo .env...")
        with open(env_file, "w") as f:
            f.write('''# Render_QM Configuration
DATABASE_URL=sqlite:///./render_qm.db
REDIS_URL=redis://localhost:6379
SECRET_KEY=render-qm-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO
BLENDER_PATH=blender
TEMP_DIR=./temp
OUTPUT_DIR=./renders

# Email (opcional)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# WhatsApp via Twilio (opcional)
# TWILIO_ACCOUNT_SID=your-twilio-sid
# TWILIO_AUTH_TOKEN=your-twilio-token
# TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
''')
        print("   ✓ .env creado")

def setup_database():
    """Configurar base de datos inicial"""
    print("🗄️ Configurando base de datos...")
    
    db_path = "render_qm.db"
    
    if Path(db_path).exists():
        print("   ✓ Base de datos ya existe")
        return
    
    # Importar y crear tablas
    try:
        from app.core.database import engine, Base
        from app.models import Job, Node, User
        
        Base.metadata.create_all(bind=engine)
        print("   ✓ Tablas creadas")
        
        # Crear usuario admin
        from app.core.database import SessionLocal
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")
        
        db = SessionLocal()
        admin_user = User(
            username="admin",
            email="admin@render-qm.local",
            hashed_password=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.close()
        
        print("   ✓ Usuario admin creado (admin/admin123)")
        
    except ImportError as e:
        print(f"   ❌ Error importando modelos: {e}")
        print("   💡 Asegúrate de estar en el directorio backend/")

def check_dependencies():
    """Verificar dependencias"""
    print("📦 Verificando dependencias...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("   ✓ Dependencias principales disponibles")
        return True
    except ImportError as e:
        print(f"   ❌ Dependencias faltantes: {e}")
        print("   💡 Instalar con: pip install -r requirements.txt")
        return False

def run_server():
    """Ejecutar servidor"""
    print("🚀 Iniciando servidor...")
    
    try:
        # Cambiar al directorio correcto si es necesario
        if Path("app").exists() and Path("app/main.py").exists():
            print("   ✓ Directorio correcto detectado")
        else:
            print("   ⚠️ No se encontró app/main.py")
            print("   💡 Asegúrate de ejecutar desde el directorio backend/")
            return False
        
        # Ejecutar servidor
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]
        
        print("   🌐 Servidor disponible en:")
        print("      • API: http://localhost:8000")
        print("      • Docs: http://localhost:8000/docs")
        print("      • Health: http://localhost:8000/health")
        print("\n   📝 Credenciales por defecto:")
        print("      • Usuario: admin")
        print("      • Contraseña: admin123")
        print("\n   ⏹️ Presiona Ctrl+C para detener")
        print("=" * 50)
        
        subprocess.run(cmd)
        return True
        
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        return True
    except Exception as e:
        print(f"   ❌ Error ejecutando servidor: {e}")
        return False

def main():
    """Función principal"""
    print("🎬 RENDER_QM BACKEND LAUNCHER")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        return False
    
    # Configurar entorno
    setup_environment()
    
    # Configurar base de datos
    setup_database()
    
    # Ejecutar servidor
    return run_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)