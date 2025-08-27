import asyncio
from datetime import datetime, timedelta

async def cleanup_old_sessions():
    """Limpiar sesiones antiguas automáticamente"""
    from app.core.database import upload_sessions
    
    while True:
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in upload_sessions.items():
                if (current_time - session["created_at"]).seconds > 3600:
                    expired_sessions.append(session_id)
            
            # Lógica de limpieza...
            await asyncio.sleep(1800)
            
        except Exception as e:
            print(f"Error en tarea de limpieza: {e}")
            await asyncio.sleep(300)

async def start_cleanup_tasks():
    """Iniciar tareas de limpieza"""
    asyncio.create_task(cleanup_old_sessions())