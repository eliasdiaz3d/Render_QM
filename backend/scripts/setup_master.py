# ========== backend/scripts/setup_master.py ==========
"""
Script para configurar el servidor master
"""
import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        "/tmp/render_qm",
        "./renders",
        "./logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado: {directory}")

def setup_database():
    """Configurar base de datos inicial"""
    db_path = "./render_qm.db"
    
    if not Path(db_path).exists():
        # Crear base de datos SQLite
        conn = sqlite3.connect(db_path)
        print(f"✓ Base de datos creada: {db_path}")
        
        # Crear usuario admin por defecto
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_password = pwd_context.hash("admin123")
        
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME
            )
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, email, hashed_password, is_admin)
            VALUES (?, ?, ?, ?)
        """, ("admin", "admin@render-qm.local", admin_password, 1))
        
        conn.commit()
        conn.close()
        
        print("✓ Usuario admin creado (admin/admin123)")

def install_dependencies():
    """Instalar dependencias de Python"""
    print("Instalando dependencias...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✓ Dependencias instaladas")

def setup_systemd_service():
    """Configurar servicio systemd (Linux)"""
    if os.name != 'posix':
        print("⚠️ Servicio systemd solo disponible en Linux")
        return
    
    service_content = """[Unit]
Description=Render_QM Master Server
After=network.target

[Service]
Type=simple
User=render
WorkingDirectory=/opt/render_qm
Environment=PATH=/opt/render_qm/venv/bin
ExecStart=/opt/render_qm/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    service_path = "/etc/systemd/system/render-qm.service"
    try:
        with open(service_path, 'w') as f:
            f.write(service_content)
        
        subprocess.run(["systemctl", "daemon-reload"])
        subprocess.run(["systemctl", "enable", "render-qm"])
        
        print(f"✓ Servicio systemd configurado: {service_path}")
        print("  Para iniciar: systemctl start render-qm")
        print("  Para ver logs: journalctl -u render-qm -f")
    except PermissionError:
        print("⚠️ Se requieren permisos de root para configurar systemd")

def main():
    """Función principal de configuración"""
    print("🚀 Configurando Render_QM Master Server...\n")
    
    create_directories()
    install_dependencies()
    setup_database()
    setup_systemd_service()
    
    print("\n✅ Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("  1. Revisar configuración en .env")
    print("  2. Iniciar servidor: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("  3. Acceder a: http://localhost:8000/docs")
    print("  4. Login con admin/admin123")

if __name__ == "__main__":
    main()api/v1/auth.py ==========
"""
Sistema de autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from ...core.database import get_db
from ...core.config import settings
from ...models.user import User
from ...schemas.user_schemas import UserCreate, UserResponse, Token

router = APIRouter()

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    db_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Usuario o email ya registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin if hasattr(user_data, 'is_admin') else False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login y obtener token de acceso"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (invalidar token)"""
    # En un sistema real, aquí se invalidaría el token
    return {"message": "Logout exitoso"}

