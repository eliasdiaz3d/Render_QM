"""
Endpoints para la cola
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.job import Job
from ...models.node import Node

router = APIRouter()

@router.get("/status")
async def get_queue_status(db: Session = Depends(get_db)):
    pending = db.query(Job).filter(Job.status == "pending").count()
    running = db.query(Job).filter(Job.status == "running").count()
    completed = db.query(Job).filter(Job.status == "completed").count()
    failed = db.query(Job).filter(Job.status == "failed").count()
    
    available_nodes = db.query(Node).filter(Node.is_available == True).count()
    
    return {
        "queue_status": "active" if pending > 0 or running > 0 else "idle",
        "job_counts": {
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed
        },
        "pending_jobs": pending,
        "running_jobs": running,
        "available_nodes": available_nodes
    }
