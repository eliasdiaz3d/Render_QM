"""
Aplicación principal FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .api.v1 import jobs, nodes, queue, auth, notifications, settings, config
from .core.database import engine, Base

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Render_QM API",
    description="Sistema de gestión de colas de render distribuido",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
app.include_router(queue.router, prefix="/api/v1/queue", tags=["queue"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])

@app.get("/")
async def root():
    return {
        "message": "Render_QM API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
