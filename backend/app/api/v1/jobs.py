"""
Endpoints para trabajos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...models.job import Job
from ...schemas.job_schemas import JobCreate, JobResponse

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
async def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).limit(100).all()
    return jobs

@router.post("/submit", response_model=JobResponse)
async def submit_job(job_data: JobCreate, db: Session = Depends(get_db)):
    job = Job(
        name=job_data.name,
        description=job_data.description,
        scene_path=job_data.scene_path,
        priority=job_data.priority,
        frame_start=job_data.frame_start,
        frame_end=job_data.frame_end,
        engine=job_data.engine,
        samples=job_data.samples,
        resolution_x=job_data.resolution_x,
        resolution_y=job_data.resolution_y,
        notification_email=job_data.notification_email,
        notification_phone=job_data.notification_phone
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    return job
