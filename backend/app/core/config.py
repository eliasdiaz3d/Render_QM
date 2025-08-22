"""
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
