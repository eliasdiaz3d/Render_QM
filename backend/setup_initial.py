#!/usr/bin/env python3
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
        print("\n🎉 Configuración completada!")
        print("Ahora puedes iniciar el servidor con:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Error en la configuración")
