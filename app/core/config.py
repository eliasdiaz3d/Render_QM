# app/core/config.py - Configuración del sistema
from pathlib import Path
from typing import Dict, Any
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_CONFIG = {
    "blender": {
        "path": None,
        "auto_detect": True,
        "custom_path": None,
        "version": None,
        "last_verified": None
    },
    "render": {
        "default_engine": "CYCLES",
        "max_concurrent_jobs": 3,
        "auto_cleanup": True,
        "default_output_format": "PNG"
    },
    "system": {
        "check_updates": True,
        "telemetry": False
    },
    "distributed": {
        "enabled": True,
        "max_nodes": 10,
        "heartbeat_timeout": 30,
        "job_timeout": 3600
    }
}

def load_config(config_file: Path) -> Dict[str, Any]:
    """Cargar configuración desde archivo"""
    try:
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge con configuración por defecto para nuevas opciones
                return merge_configs(DEFAULT_CONFIG, config)
        else:
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.error(f"❌ Error cargando configuración: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any], config_file: Path) -> bool:
    """Guardar configuración a archivo"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logger.error(f"❌ Error guardando configuración: {e}")
        return False

def merge_configs(default: dict, user: dict) -> dict:
    """Merge configuración del usuario con la por defecto"""
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

class Settings:
    """Clase de configuración singleton para el sistema"""
    
    def __init__(self):
        # Directorios base
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.UPLOAD_DIR = self.BASE_DIR / "uploads"
        self.OUTPUT_DIR = self.BASE_DIR / "renders"
        self.TEMP_DIR = self.BASE_DIR / "temp"
        self.CONFIG_FILE = self.BASE_DIR / "config.json"
        
        # Cargar configuración
        self.config = load_config(self.CONFIG_FILE)
        
        # Configuración de API
        self.API_VERSION = "2.0.0"
        self.API_TITLE = "Render Queue Manager API"
        self.API_DESCRIPTION = "API completa para gestión de colas de render de Blender"
        
        # Configuración de seguridad
        self.SECRET_KEY = "your-secret-key-change-in-production"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        # Configuración de archivos
        self.MAX_UPLOAD_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
        self.ALLOWED_EXTENSIONS = [".blend"]
        self.CHUNK_SIZE = 10 * 1024 * 1024  # 10MB
        
        # Configuración de render
        self.DEFAULT_RENDER_ENGINE = self.config["render"]["default_engine"]
        self.MAX_CONCURRENT_JOBS = self.config["render"]["max_concurrent_jobs"]
        
        # Configuración de limpieza automática
        self.CLEANUP_INTERVAL = 1800  # 30 minutos
        self.SESSION_TIMEOUT = 3600  # 1 hora
        self.OLD_JOBS_CLEANUP_DAYS = 7  # Limpiar trabajos de más de 7 días
    
    def get_blender_config(self) -> Dict[str, Any]:
        """Obtener configuración específica de Blender"""
        return self.config["blender"]
    
    def update_blender_config(self, new_config: Dict[str, Any]) -> bool:
        """Actualizar configuración de Blender"""
        self.config["blender"].update(new_config)
        return self.save_config()
    
    def get_render_config(self) -> Dict[str, Any]:
        """Obtener configuración de render"""
        return self.config["render"]
    
    def update_render_config(self, new_config: Dict[str, Any]) -> bool:
        """Actualizar configuración de render"""
        self.config["render"].update(new_config)
        return self.save_config()
    
    def save_config(self) -> bool:
        """Guardar configuración actual"""
        return save_config(self.config, self.CONFIG_FILE)
    
    def reload_config(self) -> bool:
        """Recargar configuración desde archivo"""
        try:
            self.config = load_config(self.CONFIG_FILE)
            return True
        except Exception as e:
            logger.error(f"Error recargando configuración: {e}")
            return False
    
    def reset_config(self) -> bool:
        """Resetear configuración a valores por defecto"""
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Obtener información del sistema"""
        import platform
        import sys
        
        return {
            "version": self.API_VERSION,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine(),
            "base_dir": str(self.BASE_DIR),
            "upload_dir": str(self.UPLOAD_DIR),
            "output_dir": str(self.OUTPUT_DIR),
            "temp_dir": str(self.TEMP_DIR)
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validar configuración actual"""
        issues = []
        warnings = []
        
        # Validar directorios
        if not self.UPLOAD_DIR.exists():
            issues.append(f"Directorio de uploads no existe: {self.UPLOAD_DIR}")
        
        if not self.OUTPUT_DIR.exists():
            issues.append(f"Directorio de renders no existe: {self.OUTPUT_DIR}")
        
        # Validar configuración de Blender
        blender_config = self.config["blender"]
        if not blender_config["path"] and not blender_config["auto_detect"]:
            issues.append("Blender no está configurado")
        
        # Validar configuración de render
        render_config = self.config["render"]
        if render_config["max_concurrent_jobs"] < 1:
            issues.append("max_concurrent_jobs debe ser mayor a 0")
        
        if render_config["max_concurrent_jobs"] > 10:
            warnings.append("max_concurrent_jobs muy alto, puede afectar el rendimiento")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

# Instancia singleton de configuración
settings = Settings()

# Función de conveniencia para acceder a la configuración
def get_settings() -> Settings:
    """Obtener instancia de configuración"""
    return settings