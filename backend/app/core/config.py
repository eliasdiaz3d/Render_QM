# D:\Render_QM\Render_QM\backend\app\core\config.py

import json
from pathlib import Path
from typing import Any, Dict
from pydantic_settings import BaseSettings

# --- Paso 1: Clase para cargar secretos desde el archivo .env ---
# Esta clase se encarga de las contraseñas, tokens y claves de API.
class EnvSettings(BaseSettings):
    # Variables para Email (leídas desde .env)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    
    # Variables para Twilio (leídas desde .env)
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_WHATSAPP_FROM: str | None = None
    
    # Variables para Telegram (leídas desde .env)
    TELEGRAM_BOT_TOKEN: str | None = None

    class Config:
        # Le decimos a Pydantic que lea el archivo .env desde la carpeta raíz del backend
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = 'utf-8'

# --- Paso 2: Clase principal de configuración que combina todo ---
class Settings:
    def __init__(self, env_settings: EnvSettings):
        # Cargar las credenciales desde la clase de entorno
        self.smtp_server = env_settings.SMTP_SERVER
        self.smtp_port = env_settings.SMTP_PORT
        self.smtp_user = env_settings.SMTP_USER
        self.smtp_password = env_settings.SMTP_PASSWORD
        self.twilio_account_sid = env_settings.TWILIO_ACCOUNT_SID
        self.twilio_auth_token = env_settings.TWILIO_AUTH_TOKEN
        self.twilio_whatsapp_from = env_settings.TWILIO_WHATSAPP_FROM
        self.telegram_bot_token = env_settings.TELEGRAM_BOT_TOKEN

        # Cargar la configuración de la aplicación desde config.json
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.CONFIG_FILE = self.BASE_DIR / "config.json"
        
        self.app_config = self._load_app_config()

    def _load_app_config(self) -> Dict[str, Any]:
        """Carga la configuración desde config.json y la une con valores por defecto."""
        default_config = {
            "blender": {
                "path": None,
                "auto_detect": True,
                "custom_path": None,
                "version": None,
                "last_verified": None
            },
            "render": {
                "default_engine": "CYCLES",
                "max_concurrent_jobs": 3
            }
        }
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Unir configuración por defecto con la del usuario
                    # (esto asegura que no falten claves si el json está incompleto)
                    for key, value in default_config.items():
                        if key in user_config and isinstance(value, dict):
                            value.update(user_config[key])
                    return default_config
            return default_config
        except Exception as e:
            print(f"⚠️ Error cargando config.json: {e}. Usando configuración por defecto.")
            return default_config

    def save_app_config(self):
        """Guarda la configuración actual en config.json."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.app_config, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"❌ Error guardando config.json: {e}")

# --- Paso 3: Crear una única instancia global para toda la aplicación ---
# Primero se cargan las variables de entorno, y luego se pasan a la clase principal.
env_settings = EnvSettings()
settings = Settings(env_settings)
