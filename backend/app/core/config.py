# app/core/config.py

import os
from typing import List, Union, Dict, Any
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Render Queue Manager"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Base de datos
    DATABASE_URL: str = "sqlite:///./render_queue.db"
    
    # Seguridad
    SECRET_KEY: str = "development_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de Blender (Valores por defecto)
    BLENDER_PATH: str = ""
    BLENDER_VERSION: str = ""
    BLENDER_AUTO_DETECT: bool = False
    BLENDER_LAST_VERIFIED: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore" # Ignorar variables extra en el .env

    # --- NUEVAS FUNCIONES PARA GESTIONAR LA CONFIGURACIÓN ---

    def get_blender_config(self) -> Dict[str, Any]:
        """Devuelve la configuración actual de Blender en formato diccionario"""
        return {
            "path": self.BLENDER_PATH,
            "version": self.BLENDER_VERSION,
            "auto_detect": self.BLENDER_AUTO_DETECT,
            "last_verified": self.BLENDER_LAST_VERIFIED,
            "custom_path": self.BLENDER_PATH # Alias para compatibilidad
        }

    def update_blender_config(self, config: Dict[str, Any]) -> bool:
        """
        Actualiza la configuración en memoria y la guarda en el archivo .env
        para que persista después de reiniciar.
        """
        try:
            # 1. Actualizar variables en memoria (Runtime)
            if "path" in config:
                self.BLENDER_PATH = config["path"]
            if "version" in config:
                self.BLENDER_VERSION = config["version"]
            if "auto_detect" in config:
                self.BLENDER_AUTO_DETECT = bool(config["auto_detect"])
            if "last_verified" in config:
                self.BLENDER_LAST_VERIFIED = config["last_verified"]

            # 2. Guardar en archivo .env (Persistencia)
            self._update_env_file({
                "BLENDER_PATH": self.BLENDER_PATH,
                "BLENDER_VERSION": self.BLENDER_VERSION,
                "BLENDER_AUTO_DETECT": str(self.BLENDER_AUTO_DETECT),
                "BLENDER_LAST_VERIFIED": self.BLENDER_LAST_VERIFIED
            })
            return True
        except Exception as e:
            print(f"Error guardando configuración: {e}")
            return False

    def _update_env_file(self, updates: Dict[str, str]):
        """Escribe los cambios en el archivo .env sin borrar lo demás"""
        env_path = ".env"
        
        # Leer contenido actual
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()

        # Crear mapa de claves existentes
        keys_map = {}
        for i, line in enumerate(lines):
            if "=" in line and not line.strip().startswith("#"):
                key = line.split("=")[0].strip()
                keys_map[key] = i

        # Actualizar o agregar líneas
        for key, value in updates.items():
            new_line = f"{key}={value}\n"
            if key in keys_map:
                lines[keys_map[key]] = new_line
            else:
                lines.append(new_line)

        # Escribir archivo
        with open(env_path, "w") as f:
            f.writelines(lines)

settings = Settings()