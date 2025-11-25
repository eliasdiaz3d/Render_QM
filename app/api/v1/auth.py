"""
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
