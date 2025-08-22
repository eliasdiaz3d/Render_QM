"""
Endpoints para nodos
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...models.node import Node
from ...schemas.node_schemas import NodeCreate, NodeResponse, NodeStats

router = APIRouter()

@router.get("/", response_model=List[NodeResponse])
async def get_nodes(db: Session = Depends(get_db)):
    nodes = db.query(Node).all()
    return nodes

@router.post("/register", response_model=NodeResponse)
async def register_node(node_data: NodeCreate, db: Session = Depends(get_db)):
    existing = db.query(Node).filter(
        (Node.name == node_data.name) | (Node.ip_address == node_data.ip_address)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Nodo ya existe")
    
    node = Node(
        name=node_data.name,
        hostname=node_data.hostname,
        ip_address=node_data.ip_address,
        port=node_data.port,
        cpu_cores=node_data.cpu_cores,
        memory_total=node_data.memory_total,
        gpu_count=node_data.gpu_count,
        max_concurrent_jobs=node_data.max_concurrent_jobs,
        blender_version=node_data.blender_version
    )
    
    db.add(node)
    db.commit()
    db.refresh(node)
    return node

@router.post("/{node_id}/heartbeat")
async def node_heartbeat(node_id: int, stats: NodeStats, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    
    node.status = "online"
    node.cpu_usage = stats.cpu_usage
    node.memory_usage = stats.memory_usage
    node.gpu_usage = stats.gpu_usage
    node.current_jobs = stats.current_jobs
    node.is_available = stats.current_jobs < node.max_concurrent_jobs
    
    db.commit()
    
    return {"message": "Heartbeat recibido", "node_status": node.status}
