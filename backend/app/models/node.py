"""
Modelo de nodo de render
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Node(Base):
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    hostname = Column(String(255))
    ip_address = Column(String(45), nullable=False)
    port = Column(Integer, default=8080)
    status = Column(String(20), default="offline")
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)
    cpu_cores = Column(Integer, default=0)
    cpu_usage = Column(Float, default=0.0)
    memory_total = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    gpu_count = Column(Integer, default=0)
    gpu_usage = Column(Float, default=0.0)
    max_concurrent_jobs = Column(Integer, default=1)
    current_jobs = Column(Integer, default=0)
    blender_version = Column(String(50))
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    total_jobs_completed = Column(Integer, default=0)
    average_job_time = Column(Float, default=0.0)
