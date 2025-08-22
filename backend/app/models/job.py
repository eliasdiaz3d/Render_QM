"""
Modelo de trabajo de render
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from ..core.database import Base

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    scene_path = Column(String(500), nullable=False)
    output_path = Column(String(500))
    status = Column(String(20), default="pending")
    priority = Column(Integer, default=5)
    progress = Column(Float, default=0.0)
    frame_start = Column(Integer, default=1)
    frame_end = Column(Integer, default=1)
    frame_current = Column(Integer, default=1)
    engine = Column(String(50), default="CYCLES")
    samples = Column(Integer, default=128)
    resolution_x = Column(Integer, default=1920)
    resolution_y = Column(Integer, default=1080)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    assigned_node_id = Column(Integer)
    error_message = Column(Text)
    notification_email = Column(String(255))
    notification_phone = Column(String(50))
