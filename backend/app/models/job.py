# app/models/job.py - Modelos de datos para trabajos de render
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class JobStatus(str, Enum):
    """Estados posibles de un trabajo de render"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class RenderEngine(str, Enum):
    """Motores de render soportados"""
    CYCLES = "CYCLES"
    EEVEE = "EEVEE"
    WORKBENCH = "WORKBENCH"
    ARNOLD = "ARNOLD"
    VRAY = "VRAY"

class JobPriority(str, Enum):
    """Niveles de prioridad de trabajos"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class DistributionType(str, Enum):
    """Tipos de distribución de trabajos"""
    LOCAL = "local"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"

# ==================== MODELOS BASE ====================

class JobCreate(BaseModel):
    """Modelo para crear un nuevo trabajo"""
    name: str = Field(..., min_length=1, max_length=200, description="Nombre del trabajo")
    frame_start: int = Field(1, ge=1, le=9999, description="Frame inicial")
    frame_end: int = Field(1, ge=1, le=9999, description="Frame final")
    render_engine: RenderEngine = Field(RenderEngine.CYCLES, description="Motor de render")
    priority: JobPriority = Field(JobPriority.NORMAL, description="Prioridad del trabajo")
    distribution_type: DistributionType = Field(DistributionType.LOCAL, description="Tipo de distribución")
    tags: List[str] = Field(default_factory=list, description="Tags del trabajo")
    render_settings: Dict[str, Any] = Field(default_factory=dict, description="Configuraciones específicas")
    
    @validator('frame_end')
    def validate_frame_range(cls, v, values):
        """Validar que frame_end >= frame_start"""
        if 'frame_start' in values and v < values['frame_start']:
            raise ValueError('frame_end debe ser mayor o igual a frame_start')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validar tags"""
        if len(v) > 10:
            raise ValueError('Máximo 10 tags permitidos')
        return [tag.strip().lower() for tag in v if tag.strip()]

class JobUpdate(BaseModel):
    """Modelo para actualizar un trabajo existente"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[JobStatus] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    priority: Optional[JobPriority] = None
    error_message: Optional[str] = None
    frames_rendered: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    render_settings: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    """Modelo de respuesta para trabajos"""
    id: str
    name: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: str
    original_filename: str
    output_path: Optional[str] = None
    frame_start: int
    frame_end: int
    frames_total: int
    frames_rendered: int = 0
    render_engine: RenderEngine
    estimated_time: Optional[str] = None
    actual_render_time: Optional[str] = None
    error_message: Optional[str] = None
    file_size: int = 0
    distribution_type: DistributionType
    priority: JobPriority
    tags: List[str] = Field(default_factory=list)
    user_id: str = "default"
    render_settings: Dict[str, Any] = Field(default_factory=dict)
    output_files: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

# ==================== MODELOS ESPECÍFICOS ====================

class JobStatistics(BaseModel):
    """Estadísticas de un trabajo"""
    job_id: str
    render_time_seconds: Optional[float] = None
    average_frame_time: Optional[float] = None
    peak_memory_usage: Optional[int] = None
    cpu_usage_avg: Optional[float] = None
    gpu_usage_avg: Optional[float] = None
    frames_per_hour: Optional[float] = None
    efficiency_score: Optional[float] = None

class JobProgress(BaseModel):
    """Progreso detallado de un trabajo"""
    job_id: str
    status: JobStatus
    progress_percent: int = Field(ge=0, le=100)
    current_frame: int = 0
    total_frames: int
    frames_completed: int = 0
    estimated_remaining_time: Optional[str] = None
    current_operation: Optional[str] = None
    node_id: Optional[str] = None
    render_stats: Optional[Dict[str, Any]] = None

class JobQueue(BaseModel):
    """Información de posición en cola"""
    job_id: str
    position: int = Field(ge=0, description="Posición en cola (0 = siguiente)")
    priority: JobPriority
    estimated_start_time: Optional[datetime] = None
    depends_on: Optional[List[str]] = Field(default_factory=list, description="IDs de trabajos dependientes")

# ==================== MODELOS DE CONFIGURACIÓN DE RENDER ====================

class CyclesSettings(BaseModel):
    """Configuraciones específicas para Cycles"""
    samples: int = Field(128, ge=1, le=10000)
    use_gpu: bool = True
    tile_size: int = Field(256, ge=64, le=2048)
    use_denoising: bool = True
    light_bounces_max: int = Field(12, ge=0, le=128)
    diffuse_bounces: int = Field(4, ge=0, le=128)
    glossy_bounces: int = Field(4, ge=0, le=128)
    transmission_bounces: int = Field(12, ge=0, le=128)
    volume_bounces: int = Field(0, ge=0, le=128)

class EeveeSettings(BaseModel):
    """Configuraciones específicas para Eevee"""
    taa_render_samples: int = Field(64, ge=1, le=1024)
    use_bloom: bool = False
    use_ssr: bool = True
    use_motion_blur: bool = False
    volumetric_samples: int = Field(64, ge=1, le=512)

class RenderSettings(BaseModel):
    """Configuraciones generales de render"""
    resolution_x: int = Field(1920, ge=1, le=8192)
    resolution_y: int = Field(1080, ge=1, le=8192)
    resolution_percentage: int = Field(100, ge=1, le=100)
    frame_rate: float = Field(24.0, ge=1.0, le=120.0)
    output_format: str = Field("PNG", pattern="^(PNG|JPEG|EXR|TIFF|BMP)$")
    color_mode: str = Field("RGBA", pattern="^(BW|RGB|RGBA)$")
    color_depth: str = Field("8", pattern="^(8|16|32)$")
    compression: int = Field(15, ge=0, le=100)
    quality: int = Field(90, ge=0, le=100)
    
    # Configuraciones específicas del motor
    cycles_settings: Optional[CyclesSettings] = None
    eevee_settings: Optional[EeveeSettings] = None

# ==================== MODELOS DE FILTROS Y BÚSQUEDA ====================

class JobFilter(BaseModel):
    """Filtros para búsqueda de trabajos"""
    status: Optional[List[JobStatus]] = None
    render_engine: Optional[List[RenderEngine]] = None
    priority: Optional[List[JobPriority]] = None
    user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    min_frames: Optional[int] = Field(None, ge=1)
    max_frames: Optional[int] = Field(None, ge=1)

class JobSearch(BaseModel):
    """Parámetros de búsqueda de trabajos"""
    query: Optional[str] = Field(None, max_length=100, description="Búsqueda por texto")
    filters: Optional[JobFilter] = None
    sort_by: str = Field("created_at", pattern="^(created_at|name|status|priority|progress|frames_total)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

# ==================== MODELOS DE RESPUESTA PAGINADA ====================

class JobListResponse(BaseModel):
    """Respuesta paginada de lista de trabajos"""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# ==================== MODELOS DE ANÁLISIS DE ARCHIVOS ====================

class BlendFileInfo(BaseModel):
    """Información extraída de un archivo .blend"""
    frame_start: int
    frame_end: int
    frame_current: int
    fps: float
    fps_base: float
    render_engine: str
    resolution_x: int
    resolution_y: int
    resolution_percentage: int
    file_format: str
    samples: Optional[int] = None
    scene_name: str
    total_frames: int
    output_path: Optional[str] = None
    output_format: str
    color_mode: str
    color_depth: str
    compression: int = 15
    quality: int = 90

class BlendFileAnalysis(BaseModel):
    """Análisis completo de un archivo .blend"""
    filename: str
    file_size: int
    blend_info: BlendFileInfo
    recommended_settings: Dict[str, Any]
    estimated_render_time: str
    complexity_score: float = Field(ge=0.0, le=10.0, description="Puntuación de complejidad (0-10)")
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

# ==================== MODELOS DE NOTIFICACIONES ====================

class JobNotification(BaseModel):
    """Notificación de estado de trabajo"""
    job_id: str
    job_name: str
    status: JobStatus
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    channels: List[str] = Field(default_factory=list)  # ["email", "whatsapp", "slack"]
    attachments: List[str] = Field(default_factory=list)
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")

# ==================== MODELOS DE EXPORTS ====================

class JobExport(BaseModel):
    """Configuración para exportar trabajos"""
    job_ids: List[str] = Field(..., min_items=1)
    export_format: str = Field("json", pattern="^(json|csv|excel)$")
    include_files: bool = False
    include_previews: bool = False
    compression: bool = True

class JobImport(BaseModel):
    """Configuración para importar trabajos"""
    import_format: str = Field("json", pattern="^(json|csv)$")
    overwrite_existing: bool = False
    validate_files: bool = True
    auto_start: bool = False

# ==================== FUNCIONES DE VALIDACIÓN ====================

def validate_job_data(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validar datos de trabajo antes de crear"""
    errors = []
    warnings = []
    
    # Validar campos obligatorios
    required_fields = ["name", "file_path"]
    for field in required_fields:
        if not job_data.get(field):
            errors.append(f"Campo obligatorio faltante: {field}")
    
    # Validar rango de frames
    frame_start = job_data.get("frame_start", 1)
    frame_end = job_data.get("frame_end", 1)
    
    if frame_end < frame_start:
        errors.append("frame_end debe ser mayor o igual a frame_start")
    
    total_frames = frame_end - frame_start + 1
    if total_frames > 1000:
        warnings.append(f"Trabajo con muchos frames ({total_frames}). Considere dividir en lotes.")
    
    # Validar archivo
    file_path = job_data.get("file_path", "")
    if file_path and not file_path.endswith('.blend'):
        errors.append("El archivo debe ser un archivo .blend válido")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def estimate_job_complexity(job_data: Dict[str, Any]) -> float:
    """Estimar complejidad de un trabajo (0-10)"""
    complexity = 1.0  # Base
    
    # Factor por número de frames
    total_frames = job_data.get("frames_total", 1)
    if total_frames > 100:
        complexity += min(2.0, total_frames / 100)
    
    # Factor por resolución
    resolution_x = job_data.get("resolution_x", 1920)
    resolution_y = job_data.get("resolution_y", 1080)
    resolution_factor = (resolution_x * resolution_y) / (1920 * 1080)
    complexity += min(2.0, resolution_factor)
    
    # Factor por motor de render
    render_engine = job_data.get("render_engine", "CYCLES")
    if render_engine == "CYCLES":
        samples = job_data.get("samples", 128)
        complexity += min(2.0, samples / 128)
    
    # Factor por tamaño de archivo
    file_size = job_data.get("file_size", 0)
    if file_size > 100 * 1024 * 1024:  # > 100MB
        complexity += min(1.0, file_size / (500 * 1024 * 1024))
    
    return min(10.0, complexity)