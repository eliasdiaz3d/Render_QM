import psutil
import platform
from typing import Dict, Any

class SystemMonitor:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            return {
                "cpu_usage": int(cpu_percent),
                "memory_usage": int(memory.percent),
                "memory_available": memory.available,
                "memory_total": memory.total
            }
        except:
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "memory_available": 0,
                "memory_total": 0
            }

system_monitor = SystemMonitor()