"""
Schemas para trabajos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scene_path: str
    priority: int = Field(default=5, ge=1, le=10)
    frame_start: int = Field(default=1, ge=1)
    frame_end: int = Field(default=1, ge=1)
    engine: str = Field(default="CYCLES")
    samples: int = Field(default=128, ge=1)
    resolution_x: int = Field(default=1920, ge=1)
    resolution_y: int = Field(default=1080, ge=1)
    notification_email: Optional[str] = None
    notification_phone: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    scene_path: str
    status: str
    priority: int
    progress: float
    frame_start: int
    frame_end: int
    frame_current: int
    engine: str
    samples: int
    resolution_x: int
    resolution_y: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_node_id: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
