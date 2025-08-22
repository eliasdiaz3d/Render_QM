#!/usr/bin/env python3
"""
Script de solución rápida para crear todos los archivos del backend
Ejecutar desde D:\Render_QM\backend\
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Crear archivo con contenido"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ {filepath}")

def main():
    print("🔧 Creando todos los archivos del backend...")
    
    # Verificar que estamos en backend/
    if not os.getcwd().endswith('backend'):
        print("❌ Por favor ejecuta este script desde D:\\Render_QM\\backend\\")
        return False
    
    # ========== 1. Archivos __init__.py ==========
    init_files = {
        "app/__init__.py": "",
        "app/api/__init__.py": "",
        "app/api/v1/__init__.py": "",
        "app/core/__init__.py": "",
        "app/models/__init__.py": "",
        "app/schemas/__init__.py": ""
    }
    
    for file_path, content in init_files.items():
        create_file(file_path, content)
    
    # ========== 2. Core files ==========
    
    # app/core/database.py
    create_file("app/core/database.py", '''"""
Configuración de base de datos
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./render_qm.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')
    
    # app/core/config.py
    create_file("app/core/config.py", '''"""
Configuración global de la aplicación
"""
from typing import Optional

class Settings:
    app_name: str = "Render_QM"
    version: str = "1.0.0"
    debug: bool = True
    database_url: str = "sqlite:///./render_qm.db"
    secret_key: str = "render-qm-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    max_workers: int = 4
    blender_path: str = "blender"
    temp_dir: str = "./temp"
    output_dir: str = "./renders"
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None

settings = Settings()
''')
    
    # ========== 3. Models ==========
    
    # app/models/user.py
    create_file("app/models/user.py", '''"""
Modelo de usuario
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
''')
    
    # app/models/job.py
    create_file("app/models/job.py", '''"""
Modelo de trabajo de render
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from ..core.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scene_path = Column(String(500), nullable=False)
    output_path = Column(String(500))
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=5)
    progress = Column(Float, default=0.0)
    frame_start = Column(Integer, default=1)
    frame_end = Column(Integer, default=1)
    frame_current = Column(Integer, default=1)
    engine = Column(String(50), default="CYCLES")
    samples = Column(Integer, default=128)
    resolution_x = Column(Integer, default=1920)
    resolution_y = Column(Integer, default=1080)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    assigned_node_id = Column(Integer)
    error_message = Column(Text)
    notification_email = Column(String(255))
    notification_phone = Column(String(50))
''')
    
    # app/models/node.py
    create_file("app/models/node.py", '''"""
Modelo de nodo de render
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    hostname = Column(String(255))
    ip_address = Column(String(45), nullable=False)
    port = Column(Integer, default=8080)
    status = Column(String(20), default="offline")
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    cpu_cores = Column(Integer, default=0)
    cpu_usage = Column(Float, default=0.0)
    memory_total = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    gpu_count = Column(Integer, default=0)
    gpu_usage = Column(Float, default=0.0)
    max_concurrent_jobs = Column(Integer, default=1)
    current_jobs = Column(Integer, default=0)
    blender_version = Column(String(50))
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    total_jobs_completed = Column(Integer, default=0)
    average_job_time = Column(Float, default=0.0)
''')
    
    # ========== 4. Schemas ==========
    
    # app/schemas/job_schemas.py
    create_file("app/schemas/job_schemas.py", '''"""
Schemas para trabajos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scene_path: str
    priority: int = Field(default=5, ge=1, le=10)
    frame_start: int = Field(default=1, ge=1)
    frame_end: int = Field(default=1, ge=1)
    engine: str = Field(default="CYCLES")
    samples: int = Field(default=128, ge=1)
    resolution_x: int = Field(default=1920, ge=1)
    resolution_y: int = Field(default=1080, ge=1)
    notification_email: Optional[str] = None
    notification_phone: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    scene_path: str
    status: str
    priority: int
    progress: float
    frame_start: int
    frame_end: int
    frame_current: int
    engine: str
    samples: int
    resolution_x: int
    resolution_y: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_node_id: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
''')
    
    # app/schemas/node_schemas.py
    create_file("app/schemas/node_schemas.py", '''"""
Schemas para nodos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    hostname: Optional[str] = None
    ip_address: str
    port: int = Field(default=8080, ge=1, le=65535)
    cpu_cores: int = Field(default=0, ge=0)
    memory_total: float = Field(default=0.0, ge=0)
    gpu_count: int = Field(default=0, ge=0)
    max_concurrent_jobs: int = Field(default=1, ge=1)
    blender_version: Optional[str] = None

class NodeStats(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0)
    gpu_usage: float = Field(default=0, ge=0, le=100)
    current_jobs: int = Field(default=0, ge=0)

class NodeResponse(BaseModel):
    id: int
    name: str
    hostname: Optional[str] = None
    ip_address: str
    port: int
    status: str
    is_active: bool
    is_available: bool
    cpu_cores: int
    cpu_usage: float
    memory_total: float
    memory_usage: float
    gpu_count: int
    gpu_usage: float
    max_concurrent_jobs: int
    current_jobs: int
    blender_version: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    total_jobs_completed: int
    average_job_time: float
    
    class Config:
        from_attributes = True
''')
    
    # app/schemas/user_schemas.py
    create_file("app/schemas/user_schemas.py", '''"""
Schemas para usuarios
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
''')
    
    # ========== 5. API Endpoints ==========
    
    # app/api/v1/auth.py
    create_file("app/api/v1/auth.py", '''"""
Sistema de autenticación básico
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ...core.database import get_db
from ...models.user import User
from ...schemas.user_schemas import UserResponse, Token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    return {"access_token": f"user_{user.id}_token", "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
''')
    
    # app/api/v1/jobs.py
    create_file("app/api/v1/jobs.py", '''"""
Endpoints para trabajos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...models.job import Job
from ...schemas.job_schemas import JobCreate, JobResponse

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
async def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).limit(100).all()
    return jobs

@router.post("/submit", response_model=JobResponse)
async def submit_job(job_data: JobCreate, db: Session = Depends(get_db)):
    job = Job(
        name=job_data.name,
        description=job_data.description,
        scene_path=job_data.scene_path,
        priority=job_data.priority,
        frame_start=job_data.frame_start,
        frame_end=job_data.frame_end,
        engine=job_data.engine,
        samples=job_data.samples,
        resolution_x=job_data.resolution_x,
        resolution_y=job_data.resolution_y,
        notification_email=job_data.notification_email,
        notification_phone=job_data.notification_phone
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job
''')
    
    # app/api/v1/nodes.py
    create_file("app/api/v1/nodes.py", '''"""
Endpoints para nodos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...models.node import Node
from ...schemas.node_schemas import NodeCreate, NodeResponse, NodeStats

router = APIRouter()

@router.get("/", response_model=List[NodeResponse])
async def get_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).all()
    return nodes

@router.post("/register", response_model=NodeResponse)
async def register_node(node_data: NodeCreate, db: Session = Depends(get_db)):
    existing = db.query(Node).filter(
        (Node.name == node_data.name) | (Node.ip_address == node_data.ip_address)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Nodo ya existe")
    
    node = Node(
        name=node_data.name,
        hostname=node_data.hostname,
        ip_address=node_data.ip_address,
        port=node_data.port,
        cpu_cores=node_data.cpu_cores,
        memory_total=node_data.memory_total,
        gpu_count=node_data.gpu_count,
        max_concurrent_jobs=node_data.max_concurrent_jobs,
        blender_version=node_data.blender_version
    )
    
    db.add(node)
    db.commit()
    db.refresh(node)
    return node

@router.post("/{node_id}/heartbeat")
async def node_heartbeat(node_id: int, stats: NodeStats, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    node.status = "online"
    node.cpu_usage = stats.cpu_usage
    node.memory_usage = stats.memory_usage
    node.gpu_usage = stats.gpu_usage
    node.current_jobs = stats.current_jobs
    node.is_available = stats.current_jobs < node.max_concurrent_jobs
    
    db.commit()
    
    return {"message": "Heartbeat recibido", "node_status": node.status}
''')
    
    # app/api/v1/queue.py
    create_file("app/api/v1/queue.py", '''"""
Endpoints para la cola
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.job import Job
from ...models.node import Node

router = APIRouter()

@router.get("/status")
async def get_queue_status(db: Session = Depends(get_db)):
    pending = db.query(Job).filter(Job.status == "pending").count()
    running = db.query(Job).filter(Job.status == "running").count()
    completed = db.query(Job).filter(Job.status == "completed").count()
    failed = db.query(Job).filter(Job.status == "failed").count()
    
    available_nodes = db.query(Node).filter(Node.is_available == True).count()
    
    return {
        "queue_status": "active" if pending > 0 or running > 0 else "idle",
        "job_counts": {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed
        },
        "pending_jobs": pending,
        "running_jobs": running,
        "available_nodes": available_nodes
    }
''')
    
    # app/api/v1/settings.py
    create_file("app/api/v1/settings.py", '''"""
Configuración del sistema
"""
from fastapi import APIRouter
from ...core.config import settings

router = APIRouter()

@router.get("/")
async def get_settings():
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "max_workers": settings.max_workers,
        "blender_path": settings.blender_path,
        "temp_dir": settings.temp_dir,
        "output_dir": settings.output_dir
    }
''')
    
    # app/api/v1/notifications.py
    create_file("app/api/v1/notifications.py", '''"""
Sistema de notificaciones básico
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/send")
async def send_notification():
    return {"message": "Notificación enviada (funcionalidad pendiente)"}
''')
    
    # ========== 6. Main application ==========
    
    # app/main.py
    create_file("app/main.py", '''"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .api.v1 import jobs, nodes, queue, auth, notifications, settings
from .core.database import engine, Base

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Render_QM API",
    description="Sistema de gestión de colas de render distribuido",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
app.include_router(queue.router, prefix="/api/v1/queue", tags=["queue"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])

@app.get("/")
async def root():
    return {
        "message": "Render_QM API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
''')
    
    # ========== 7. Configuración y scripts ==========
    
    # .env
    create_file(".env", '''DATABASE_URL=sqlite:///./render_qm.db
SECRET_KEY=render-qm-secret-key-change-in-production
DEBUG=true
LOG_LEVEL=INFO
BLENDER_PATH=blender
TEMP_DIR=./temp
OUTPUT_DIR=./renders
''')
    
    # requirements.txt
    create_file("requirements.txt", '''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
''')
    
    # setup_db.py - Script para crear la base de datos
    create_file("setup_db.py", '''#!/usr/bin/env python3
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
''')
    
    # start_server.bat
    create_file("start_server.bat", '''@echo off
echo 🚀 Iniciando Render_QM Backend...
echo.

REM Crear directorios
if not exist "temp" mkdir temp
if not exist "renders" mkdir renders
if not exist "logs" mkdir logs

REM Configurar base de datos
echo 🗄️ Configurando base de datos...
python setup_db.py

echo.
echo 🌐 Servidor disponible en:
echo    • API: http://localhost:8000
echo    • Docs: http://localhost:8000/docs
echo    • Health: http://localhost:8000/health
echo.
echo 👤 Credenciales:
echo    • Usuario: admin
echo    • Contraseña: admin123
echo.
echo ⏹️ Presiona Ctrl+C para detener
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
''')
    
    # Crear directorios necesarios
    dirs = ["temp", "renders", "logs"]
    for directory in dirs:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 {directory}/")
    
    print("\n🎉 ¡Todos los archivos creados exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. python setup_db.py")
    print("2. start_server.bat")
    print("   O: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n3. Abrir: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    main()