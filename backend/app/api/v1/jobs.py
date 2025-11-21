# app/api/v1/jobs.py - Endpoints para gestión de trabajos de render
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional, Dict, Any
import zipfile
from io import BytesIO
import uuid
import os
import shutil
from datetime import datetime
from pathlib import Path
import asyncio

from app.models.job import (
    JobCreate, JobUpdate, JobResponse, JobListResponse, 
    JobFilter, JobSearch, BlendFileAnalysis, JobExport
)
from app.core.database import (
    jobs_db, create_job, get_job, update_job, delete_job,
    get_jobs_by_status, search_jobs, get_queue_statistics
)
from app.services.render_service import render_service
from app.services.blender_service import blender_service
from app.core.config import settings

router = APIRouter()

# ==================== ENDPOINTS DE CREACIÓN Y UPLOAD ====================

@router.post("/jobs/upload", response_model=Dict[str, Any])
async def upload_and_create_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    frame_start: int = Form(1),
    frame_end: int = Form(1),
    render_engine: str = Form("CYCLES"),
    priority: str = Form("normal"),
    distribution_type: str = Form("local")
):
    """Subir archivo .blend y crear trabajo de render local"""
    
    # Validar archivo
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    # Validar parámetros
    if frame_end < frame_start:
        raise HTTPException(status_code=400, detail="frame_end debe ser >= frame_start")
    
    if (frame_end - frame_start + 1) > 2000:
        raise HTTPException(status_code=400, detail="Máximo 2000 frames por trabajo")
    
    try:
        # Generar ID único
        job_id = str(uuid.uuid4())
        
        # Guardar archivo
        file_path = settings.UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear datos del trabajo
        job_data = {
            "name": name,
            "file_path": str(file_path),
            "original_filename": file.filename,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "render_engine": render_engine,
            "priority": priority,
            "distribution_type": distribution_type,
            "file_size": file_path.stat().st_size,
            "user_id": "default"  # TODO: obtener del contexto de autenticación
        }
        
        # Crear trabajo en la base de datos
        job_id = create_job(job_data)
        job = get_job(job_id)
        
        # Iniciar render en background
        asyncio.create_task(render_service.render_job_background(job_id))  
        
        return {
            "message": "Archivo subido y trabajo creado exitosamente",
            "job_id": job_id,
            "job": job,
            "estimated_queue_time": await render_service.estimate_queue_time(job_data)
        }
        
    except Exception as e:
        # Limpiar archivo si hubo error
        if 'file_path' in locals() and file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error creando trabajo: {str(e)}")

@router.post("/jobs/upload-distributed", response_model=Dict[str, Any])
async def upload_and_create_distributed_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    frame_start: int = Form(1),
    frame_end: int = Form(1),
    render_engine: str = Form("CYCLES"),
    priority: str = Form("normal")
):
    """Subir archivo .blend y crear trabajo de render distribuido"""
    
    # Validar archivo
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    try:
        # Generar ID único
        job_id = str(uuid.uuid4())
        
        # Guardar archivo
        file_path = settings.UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear datos del trabajo
        job_data = {
            "name": name,
            "file_path": str(file_path),
            "original_filename": file.filename,
            "frame_start": frame_start,
            "frame_end": frame_end,
            "render_engine": render_engine,
            "priority": priority,
            "distribution_type": "distributed",
            "file_size": file_path.stat().st_size,
            "user_id": "default"
        }
        
        # Crear trabajo en la base de datos
        job_id = create_job(job_data)
        job = get_job(job_id)
        
        # Añadir a cola distribuida
        from app.core.database import add_job_to_queue
        add_job_to_queue(job_id, priority)
        
        return {
            "message": "Trabajo distribuido creado exitosamente",
            "job_id": job_id,
            "job": job,
            "queue_position": len([j for j in jobs_db.values() if j["status"] == "pending"])
        }
        
    except Exception as e:
        if 'file_path' in locals() and file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error creando trabajo distribuido: {str(e)}")

# ==================== ENDPOINTS DE CONSULTA ====================

@router.get("/jobs", response_model=JobListResponse)
async def get_jobs(
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|name|status|priority|progress)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """Obtener lista paginada de trabajos"""
    
    # Filtrar trabajos
    jobs = list(jobs_db.values())
    
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    if user_id:
        jobs = [j for j in jobs if j.get("user_id") == user_id]
    
    # Ordenar
    reverse = sort_order == "desc"
    jobs.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
    
    # Paginar
    total = len(jobs)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_jobs = jobs[start_idx:end_idx]
    
    total_pages = (total + page_size - 1) // page_size
    
    return JobListResponse(
        jobs=page_jobs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_details(job_id: str):
    """Obtener detalles de un trabajo específico"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    return job

@router.post("/jobs/search", response_model=JobListResponse)
async def search_jobs_endpoint(search_params: JobSearch):
    """Buscar trabajos con filtros avanzados"""
    
    # Aplicar filtros
    filters = {}
    if search_params.filters:
        if search_params.filters.status:
            filters["status"] = search_params.filters.status[0]  # Simplificado por ahora
        if search_params.filters.render_engine:
            filters["render_engine"] = search_params.filters.render_engine[0]
        if search_params.filters.user_id:
            filters["user_id"] = search_params.filters.user_id
    
    # Buscar
    results = search_jobs(search_params.query or "", filters)
    
    # Ordenar y paginar
    reverse = search_params.sort_order == "desc"
    results.sort(key=lambda x: x.get(search_params.sort_by, ""), reverse=reverse)
    
    total = len(results)
    start_idx = (search_params.page - 1) * search_params.page_size
    end_idx = start_idx + search_params.page_size
    page_jobs = results[start_idx:end_idx]
    
    total_pages = (total + search_params.page_size - 1) // search_params.page_size
    
    return JobListResponse(
        jobs=page_jobs,
        total=total,
        page=search_params.page,
        page_size=search_params.page_size,
        total_pages=total_pages,
        has_next=search_params.page < total_pages,
        has_prev=search_params.page > 1
    )

# ==================== ENDPOINTS DE GESTIÓN ====================

@router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job_endpoint(job_id: str, job_update: JobUpdate):
    """Actualizar trabajo existente"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    # Preparar actualizaciones
    updates = job_update.dict(exclude_unset=True)
    
    # Validar transiciones de estado
    if "status" in updates:
        current_status = job["status"]
        new_status = updates["status"]
        
        # Definir transiciones válidas
        valid_transitions = {
            "pending": ["processing", "cancelled"],
            "processing": ["completed", "failed", "cancelled", "paused"],
            "paused": ["processing", "cancelled"],
            "completed": [],  # Estados finales
            "failed": [],
            "cancelled": []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            raise HTTPException(
                status_code=400, 
                detail=f"Transición inválida: {current_status} -> {new_status}"
            )
    
    # Aplicar actualizaciones
    success = update_job(job_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="Error actualizando trabajo")
    
    return get_job(job_id)

@router.delete("/jobs/{job_id}")
async def delete_job_endpoint(job_id: str):
    """Eliminar un trabajo"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    # Cancelar si está activo
    if job["status"] in ["pending", "processing"]:
        render_service.cancel_job(job_id)
    
    # Eliminar
    success = delete_job(job_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error eliminando trabajo")
    
    return {"message": f"Trabajo {job_id} eliminado exitosamente"}

@router.post("/jobs/{job_id}/cancel")
async def cancel_job_endpoint(job_id: str):
    """Cancelar un trabajo en progreso"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] not in ["pending", "processing", "paused"]:
        raise HTTPException(status_code=400, detail="El trabajo no se puede cancelar")
    
    success = render_service.cancel_job(job_id)
    if success:
        return {"message": f"Trabajo {job_id} cancelado exitosamente"}
    else:
        # Actualizar estado manualmente si no estaba renderizando activamente
        update_job(job_id, {"status": "cancelled", "completed_at": datetime.now()})
        return {"message": f"Trabajo {job_id} marcado como cancelado"}

@router.post("/jobs/{job_id}/resume")
async def resume_job_endpoint(job_id: str, background_tasks: BackgroundTasks):
    """Reanudar un trabajo pausado"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] != "paused":
        raise HTTPException(status_code=400, detail="Solo se pueden reanudar trabajos pausados")
    
    # Cambiar estado a pending para que sea recogido por el sistema
    success = update_job(job_id, {"status": "pending"})
    if success:
        # Si es local, iniciar render directamente
        if job.get("distribution_type") == "local":
            background_tasks.add_task(render_service.render_job_background, job_id)
        else:
            # Si es distribuido, añadir a cola
            from app.core.database import add_job_to_queue
            add_job_to_queue(job_id, job.get("priority", "normal"))
        
        return {"message": f"Trabajo {job_id} reanudado"}
    else:
        raise HTTPException(status_code=500, detail="Error reanudando trabajo")

# ==================== ENDPOINTS DE DESCARGA ====================

@router.get("/jobs/{job_id}/download")
async def download_result(job_id: str, frame: Optional[int] = Query(None)):
    """Descargar resultado del render - frame específico o primer frame"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job.get("output_path"):
        raise HTTPException(status_code=404, detail="No se encontró resultado")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Directorio de salida no encontrado")
    
    # Extensiones soportadas
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    image_files = []
    
    for ext in extensions:
        image_files.extend(list(output_dir.glob(ext)))
        image_files.extend(list(output_dir.glob(f"**/{ext}")))  # Búsqueda recursiva
    
    image_files = sorted(image_files)
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Si se especifica un frame, buscar ese frame específico
    if frame is not None:
        frame_file = None
        for img_file in image_files:
            # Buscar diferentes patrones de numeración
            frame_patterns = [
                rf'{frame:04d}',  # 0001
                rf'{frame:03d}',  # 001
                rf'{frame:02d}',  # 01
                rf'{frame}',      # 1
            ]
            
            for pattern in frame_patterns:
                if pattern in img_file.name:
                    frame_file = img_file
                    break
            if frame_file:
                break
        
        if not frame_file:
            raise HTTPException(status_code=404, detail=f"Frame {frame} no encontrado")
        
        return FileResponse(
            path=str(frame_file),
            filename=f"render_{job_id}_frame_{frame:04d}{frame_file.suffix}",
            media_type=f"image/{frame_file.suffix[1:]}" if frame_file.suffix else "image/png"
        )
    
    # Si no se especifica frame, devolver el primer frame
    first_file = image_files[0]
    return FileResponse(
        path=str(first_file),
        filename=f"render_{job_id}_preview{first_file.suffix}",
        media_type=f"image/{first_file.suffix[1:]}" if first_file.suffix else "image/png"
    )

@router.get("/jobs/{job_id}/download-all")
async def download_all_frames(job_id: str):
    """Descargar todos los frames como ZIP"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="El trabajo no está completado")
    
    if not job.get("output_path"):
        raise HTTPException(status_code=404, detail="No se encontró resultado")
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    image_files = []
    
    for ext in extensions:
        image_files.extend(list(output_dir.glob(ext)))
        image_files.extend(list(output_dir.glob(f"**/{ext}")))
    
    if not image_files:
        raise HTTPException(status_code=404, detail="No se encontraron imágenes renderizadas")
    
    # Crear ZIP en memoria
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for img_file in sorted(image_files):
            # Usar path relativo al directorio de output
            arcname = os.path.relpath(str(img_file), str(output_dir))
            zip_file.write(img_file, arcname)
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        BytesIO(zip_buffer.read()),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=render_{job_id}_all_frames.zip"}
    )

@router.get("/jobs/{job_id}/frames")
async def get_job_frames(job_id: str):
    """Obtener lista de todos los frames renderizados"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] != "completed":
        return {
            "has_frames": False,
            "status": job["status"],
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    if not job.get("output_path"):
        return {
            "has_frames": False,
            "message": "No se encontró directorio de salida"
        }
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.exr", "*.tiff", "*.tif"]
    image_files = []
    
    for ext in extensions:
        image_files.extend(list(output_dir.glob(ext)))
        image_files.extend(list(output_dir.glob(f"**/{ext}")))
    
    image_files = sorted(image_files)
    
    if not image_files:
        return {
            "has_frames": False,
            "message": "No se encontraron imágenes renderizadas"
        }
    
    # Extraer números de frame
    import re
    frames = []
    for img_file in image_files:
        try:
            # Extraer número de frame del nombre del archivo
            frame_matches = re.findall(r'(\d+)', img_file.stem)
            if frame_matches:
                # Tomar el número más largo (probablemente el frame number)
                frame_num = max(frame_matches, key=len)
                frame_num = int(frame_num)
                
                frames.append({
                    "frame_number": frame_num,
                    "filename": img_file.name,
                    "file_size": img_file.stat().st_size,
                    "download_url": f"/api/v1/jobs/{job_id}/download?frame={frame_num}",
                    "full_path": str(img_file)
                })
        except:
            continue
    
    # Ordenar por número de frame
    frames.sort(key=lambda x: x["frame_number"])
    
    return {
        "has_frames": True,
        "total_frames": len(frames),
        "frame_start": job.get("frame_start", 1),
        "frame_end": job.get("frame_end", 1),
        "frames": frames,
        "output_dir": str(output_dir),
        "preview_url": f"/api/v1/jobs/{job_id}/download"
    }

@router.get("/jobs/{job_id}/preview")
async def get_job_preview(job_id: str):
    """Obtener preview del render (para mostrar en la interfaz)"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    if job["status"] != "completed":
        return {
            "has_preview": False,
            "status": job["status"],
            "message": f"Trabajo en estado: {job['status']}"
        }
    
    if not job.get("output_path"):
        return {
            "has_preview": False,
            "message": "No se encontró directorio de salida"
        }
    
    # Buscar archivos de imagen
    output_dir = Path(job["output_path"])
    image_files = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg")) + list(output_dir.glob("*.exr"))
    
    if not image_files:
        return {
            "has_preview": False,
            "message": "No se encontraron imágenes renderizadas"
        }
    
    # Devolver información del primer archivo
    first_image = sorted(image_files)[0]
    return {
        "has_preview": True,
        "preview_url": f"/api/v1/jobs/{job_id}/download",
        "filename": first_image.name,
        "file_size": first_image.stat().st_size,
        "total_frames": len(image_files),
        "output_dir": str(output_dir)
    }

# ==================== ENDPOINTS DE ANÁLISIS ====================

@router.post("/blend/analyze", response_model=BlendFileAnalysis)
async def analyze_blend_file(file: UploadFile = File(...)):
    """Analizar archivo .blend y extraer información de frames"""
    
    if not file.filename.endswith('.blend'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .blend")
    
    # Guardar archivo temporal
    temp_file_path = settings.TEMP_DIR / f"temp_{uuid.uuid4()}_{file.filename}"
    
    try:
        # Guardar archivo
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Analizar archivo
        blend_info = blender_service.get_blend_file_info(str(temp_file_path))
        
        if "error" in blend_info:
            raise HTTPException(status_code=400, detail=blend_info["error"])
        
        # Validar archivo
        validation = blender_service.validate_blend_file(str(temp_file_path))
        
        # Obtener configuraciones recomendadas
        recommended_settings = blender_service.get_recommended_settings(blend_info)
        
        return BlendFileAnalysis(
            filename=file.filename,
            file_size=temp_file_path.stat().st_size,
            blend_info=blend_info,
            recommended_settings=recommended_settings,
            estimated_render_time=blender_service.estimate_render_time(blend_info),
            complexity_score=blend_info.get("complexity_score", 1.0),
            warnings=validation.get("warnings", []),
            suggestions=blend_info.get("recommendations", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando archivo: {str(e)}")
    finally:
        # Limpiar archivo temporal
        if temp_file_path.exists():
            os.remove(temp_file_path)

# ==================== ENDPOINTS DE ESTADÍSTICAS ====================

@router.get("/queue/status")
async def get_queue_status():
    """Obtener estado general de la cola"""
    return get_queue_statistics()

@router.get("/jobs/statistics")
async def get_jobs_statistics():
    """Obtener estadísticas detalladas de trabajos"""
    stats = render_service.get_render_statistics()
    
    # Añadir estadísticas adicionales
    jobs = list(jobs_db.values())
    
    # Trabajos por motor de render
    engines = {}
    for job in jobs:
        engine = job.get("render_engine", "UNKNOWN")
        engines[engine] = engines.get(engine, 0) + 1
    
    # Trabajos por estado en las últimas 24 horas
    from datetime import timedelta
    recent_cutoff = datetime.now() - timedelta(hours=24)
    recent_jobs = [j for j in jobs if j.get("created_at", datetime.min) > recent_cutoff]
    
    recent_by_status = {}
    for job in recent_jobs:
        status = job["status"]
        recent_by_status[status] = recent_by_status.get(status, 0) + 1
    
    stats.update({
        "engines_usage": engines,
        "recent_jobs_24h": len(recent_jobs),
        "recent_by_status": recent_by_status,
        "queue_length": len([j for j in jobs if j["status"] == "pending"]),
        "average_frames_per_job": sum(j.get("frames_total", 0) for j in jobs) / len(jobs) if jobs else 0
    })
    
    return stats

@router.get("/jobs/{job_id}/logs")
async def get_job_logs(job_id: str):
    """Obtener logs de un trabajo específico"""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado")
    
    # Por ahora devolvemos información básica
    # TODO: Implementar sistema de logs más detallado
    logs = []
    
    if job.get("created_at"):
        logs.append({
            "timestamp": job["created_at"],
            "level": "INFO",
            "message": f"Trabajo '{job['name']}' creado"
        })
    
    if job.get("started_at"):
        logs.append({
            "timestamp": job["started_at"],
            "level": "INFO",
            "message": "Render iniciado"
        })
    
    if job.get("completed_at"):
        level = "INFO" if job["status"] == "completed" else "ERROR"
        message = f"Render {'completado' if job['status'] == 'completed' else 'falló'}"
        if job.get("error_message"):
            message += f": {job['error_message']}"
        
        logs.append({
            "timestamp": job["completed_at"],
            "level": level,
            "message": message
        })
    
    return {
        "job_id": job_id,
        "logs": logs,
        "total_logs": len(logs)
    }

# ==================== ENDPOINTS DE EXPORT/IMPORT ====================

@router.post("/jobs/export")
async def export_jobs(export_config: JobExport):
    """Exportar trabajos en diferentes formatos"""
    
    # Obtener trabajos especificados
    jobs_to_export = []
    for job_id in export_config.job_ids:
        job = get_job(job_id)
        if job:
            jobs_to_export.append(job)
    
    if not jobs_to_export:
        raise HTTPException(status_code=404, detail="No se encontraron trabajos para exportar")
    
    if export_config.export_format == "json":
        # Exportar como JSON
        import json
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_jobs": len(jobs_to_export),
            "jobs": jobs_to_export
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        return StreamingResponse(
            BytesIO(json_data.encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=jobs_export.json"}
        )
    
    elif export_config.export_format == "csv":
        # Exportar como CSV
        import csv
        from io import StringIO
        
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        
        # Headers
        headers = [
            "id", "name", "status", "created_at", "started_at", "completed_at",
            "render_engine", "frame_start", "frame_end", "frames_total",
            "frames_rendered", "progress", "render_time", "file_size"
        ]
        writer.writerow(headers)
        
        # Data
        for job in jobs_to_export:
            row = [
                job.get("id", ""),
                job.get("name", ""),
                job.get("status", ""),
                job.get("created_at", ""),
                job.get("started_at", ""),
                job.get("completed_at", ""),
                job.get("render_engine", ""),
                job.get("frame_start", ""),
                job.get("frame_end", ""),
                job.get("frames_total", ""),
                job.get("frames_rendered", ""),
                job.get("progress", ""),
                job.get("render_time", ""),
                job.get("file_size", "")
            ]
            writer.writerow(row)
        
        csv_data = csv_buffer.getvalue()
        
        return StreamingResponse(
            BytesIO(csv_data.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=jobs_export.csv"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Formato de exportación no soportado")

# ==================== ENDPOINTS DE MANTENIMIENTO ====================

@router.post("/jobs/cleanup")
async def cleanup_old_jobs(days: int = Query(7, ge=1, le=365)):
    """Limpiar trabajos antiguos completados/fallidos"""
    
    from app.core.database import cleanup_old_jobs
    
    cleaned_count = cleanup_old_jobs(days)
    render_cleaned = render_service.cleanup_old_renders(days)
    
    return {
        "message": "Limpieza completada",
        "jobs_cleaned": cleaned_count,
        "render_directories_cleaned": render_cleaned,
        "days_threshold": days
    }

@router.get("/jobs/health")
async def get_jobs_health():
    """Verificar salud del sistema de trabajos"""
    
    from app.core.database import validate_database_integrity
    
    # Validar integridad de la base de datos
    integrity_check = validate_database_integrity()
    
    # Estadísticas del sistema
    stats = render_service.get_render_statistics()
    
    # Verificar Blender
    blender_path = blender_service.get_current_blender_path()
    blender_ok = blender_path is not None
    
    # Verificar directorios
    dirs_ok = (
        settings.UPLOAD_DIR.exists() and 
        settings.OUTPUT_DIR.exists() and 
        settings.TEMP_DIR.exists()
    )
    
    overall_health = "healthy"
    if not integrity_check["valid"] or not blender_ok or not dirs_ok:
        overall_health = "critical"
    elif integrity_check["warnings"] or stats["failed_jobs"] > stats["total_jobs"] * 0.2:
        overall_health = "warning"
    
    return {
        "overall_health": overall_health,
        "blender_available": blender_ok,
        "blender_path": blender_path,
        "directories_ok": dirs_ok,
        "database_integrity": integrity_check,
        "render_statistics": stats,
        "active_jobs": len(render_service.get_active_jobs()),
        "recommendations": [] if overall_health == "healthy" else [
            "Verificar configuración de Blender" if not blender_ok else None,
            "Revisar integridad de base de datos" if not integrity_check["valid"] else None,
            "Alta tasa de fallos en renders" if stats["failed_jobs"] > stats["total_jobs"] * 0.2 else None
        ]
    }