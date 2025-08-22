"""
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
