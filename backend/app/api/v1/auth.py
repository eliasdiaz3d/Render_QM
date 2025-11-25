"""
Sistema de autenticación básico adaptado para base de datos en memoria
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Dict, Any

from ...core.database import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Base de datos de usuarios en memoria (temporal)
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@render-qm.local",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "is_active": True,
        "is_admin": True,
        "created_at": "2025-01-01T00:00:00"
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """Autenticar usuario usando la base de datos en memoria"""
    user = users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def get_user_by_username(username: str) -> Dict[str, Any]:
    """Obtener usuario por nombre de usuario"""
    return users_db.get(username)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login de usuario"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token simple (en producción usar JWT)
    access_token = f"user_{user['id']}_token"
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
            "is_admin": user["is_admin"]
        }
    }

@router.get("/me")
async def get_current_user():
    """Obtener información del usuario actual"""
    # Por simplicidad, devolvemos el usuario admin por defecto
    # En un sistema real, verificarías el token
    user = get_user_by_username("admin")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "is_admin": user["is_admin"],
        "created_at": user["created_at"]
    }

@router.post("/register")
async def register_user(username: str, password: str, email: str):
    """Registrar nuevo usuario (endpoint básico)"""
    if username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    
    hashed_password = get_password_hash(password)
    new_user_id = len(users_db) + 1
    
    users_db[username] = {
        "id": new_user_id,
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "is_active": True,
        "is_admin": False,
        "created_at": "2025-01-01T00:00:00"
    }
    
    return {"message": "Usuario creado exitosamente", "user_id": new_user_id}

@router.get("/users")
async def list_users():
    """Listar todos los usuarios (solo info básica)"""
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
            "is_admin": user["is_admin"]
        }
        for user in users_db.values()
    ]