"""
Schemas para nodos
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    hostname: Optional[str] = None
    ip_address: str
    port: int = Field(default=8080, ge=1, le=65535)
    cpu_cores: int = Field(default=0, ge=0)
    memory_total: float = Field(default=0.0, ge=0)
    gpu_count: int = Field(default=0, ge=0)
    max_concurrent_jobs: int = Field(default=1, ge=1)
    blender_version: Optional[str] = None

class NodeStats(BaseModel):
    cpu_usage: float = Field(..., ge=0, le=100)
    memory_usage: float = Field(..., ge=0)
    gpu_usage: float = Field(default=0, ge=0, le=100)
    current_jobs: int = Field(default=0, ge=0)

class NodeResponse(BaseModel):
    id: int
    name: str
    hostname: Optional[str] = None
    ip_address: str
    port: int
    status: str
    is_active: bool
    is_available: bool
    cpu_cores: int
    cpu_usage: float
    memory_total: float
    memory_usage: float
    gpu_count: int
    gpu_usage: float
    max_concurrent_jobs: int
    current_jobs: int
    blender_version: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    created_at: datetime
    total_jobs_completed: int
    average_job_time: float
    
    class Config:
        from_attributes = True
