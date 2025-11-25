"""
Sistema de notificaciones básico
"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/send")
async def send_notification():
    return {"message": "Notificación enviada (funcionalidad pendiente)"}
