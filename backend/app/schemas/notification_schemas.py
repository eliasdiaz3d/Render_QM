# ========== backend/app/schemas/notification_schemas.py ==========
"""
Schemas Pydantic para notificaciones
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    type: str = Field(..., regex="^(email|whatsapp|telegram|slack)$")
    recipient: str
    subject: Optional[str] = None
    message: str
    attachment_path: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    status: str  # "sent", "failed", "pending"
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
