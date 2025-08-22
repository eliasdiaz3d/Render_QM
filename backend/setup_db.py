#!/usr/bin/env python3
"""
Script para configurar la base de datos inicial
"""
import sys
import os

def setup_database():
    try:
        print("🗄️ Configurando base de datos...")
        
        from app.core.database import engine, Base, SessionLocal
        from app.models.user import User
        from app.models.job import Job
        from app.models.node import Node
        from passlib.context import CryptContext
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas")
        
        # Crear usuario admin
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")
        
        db = SessionLocal()
        
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
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_database()
