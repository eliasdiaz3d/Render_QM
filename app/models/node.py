# app/models/node.py - Modelos de datos para nodos de render
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# ==================== ENUMS ====================

class NodeStatus(str, Enum):
    """Estados posibles de un nodo"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class NodePlatform(str, Enum):
    """Plataformas soportadas"""
    WINDOWS = "Windows"
    LINUX = "Linux" 
    MACOS = "Darwin"

class NodeCapabilityType(str, Enum):
    """Tipos de capacidades de nodo"""
    CPU = "cpu"
    GPU = "gpu"
    HYBRID = "hybrid"

class GPUType(str, Enum):
    """Tipos de GPU soportadas"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    UNKNOWN = "unknown"

# ==================== MODELOS DE SISTEMA ====================

class SystemStats(BaseModel):
    """Estadísticas del sistema del nodo"""
    cpu_percent: float = Field(ge=0.0, le=100.0)
    memory_percent: float = Field(ge=0.0, le=100.0)
    memory_available_gb: float = Field(ge=0.0)
    memory_total_gb: float = Field(ge=0.0)
    disk_free_gb: float = Field(ge=0.0)
    disk_total_gb: float = Field(ge=0.0)
    gpu_count: int = Field(ge=0)
    gpu_memory_total_mb: int = Field(default=0, ge=0)
    gpu_memory_used_mb: int = Field(default=0, ge=0)
    temperature: Dict[str, float] = Field(default_factory=dict)
    load_average: float = Field(default=0.0, ge=0.0)
    network_io: Dict[str, int] = Field(default_factory=dict)
    disk_io: Dict[str, int] = Field(default_factory=dict)

class NodeInfo(BaseModel):
    """Información estática del nodo"""
    hostname: str
    platform: NodePlatform
    platform_version: str
    architecture: str
    processor: str
    cpu_cores_physical: int = Field(ge=1)
    cpu_cores_logical: int = Field(ge=1)
    python_version: str
    node_agent_version: str = "1.0.0"
    blender_version: Optional[str] = None
    blender_path: Optional[str] = None
    
    @validator('cpu_cores_logical')
    def logical_cores_gte_physical(cls, v, values):
        """Validar que cores lógicos >= físicos"""
        if 'cpu_cores_physical' in values and v < values['cpu_cores_physical']:
            raise ValueError('cpu_cores_logical debe ser >= cpu_cores_physical')
        return v

class NodeCapabilities(BaseModel):
    """Capacidades del nodo"""
    concurrent_jobs: int = Field(1, ge=1, le=10)
    gpu_rendering: bool = False
    cpu_rendering: bool = True
    max_memory_gb: int = Field(8, ge=1)
    blender_available: bool = False
    supported_engines: List[str] = Field(default_factory=lambda: ["CYCLES", "EEVEE"])
    gpu_info: List[Dict[str, Any]] = Field(default_factory=list)
    network_speed_mbps: Optional[float] = None
    storage_speed_mbps: Optional[float] = None
    
    @validator('supported_engines')
    def validate_engines(cls, v):
        """Validar motores soportados"""
        valid_engines = ["CYCLES", "EEVEE", "WORKBENCH", "ARNOLD", "VRAY"]
        return [engine for engine in v if engine in valid_engines]

# ==================== MODELOS PRINCIPALES ====================

class NodeRegistration(BaseModel):
    """Datos para registrar un nuevo nodo"""
    node_name: Optional[str] = None
    system_stats: SystemStats
    node_info: NodeInfo
    capabilities: NodeCapabilities
    tags: List[str] = Field(default_factory=list, max_items=10)
    config: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validar tags del nodo"""
        return [tag.strip().lower() for tag in v if tag.strip()]

class NodeHeartbeat(BaseModel):
    """Datos del heartbeat de un nodo"""
    status: NodeStatus
    system_stats: SystemStats
    active_jobs: int = Field(0, ge=0)
    job_statuses: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    last_job_completed: Optional[str] = None
    uptime_seconds: float = Field(0.0, ge=0.0)

class NodeResponse(BaseModel):
    """Respuesta completa de información del nodo"""
    node_id: str
    node_name: str
    status: NodeStatus
    last_seen: datetime
    registered_at: datetime
    system_stats: SystemStats
    node_info: NodeInfo
    capabilities: NodeCapabilities
    active_jobs: int = 0
    total_jobs_completed: int = 0
    total_jobs_failed: int = 0
    total_render_time_seconds: float = 0.0
    tags: List[str] = Field(default_factory=list)
    assigned_jobs: List[str] = Field(default_factory=list)
    uptime_seconds: float = 0.0
    efficiency_score: float = Field(default=100.0, ge=0.0, le=100.0)
    
    class Config:
        from_attributes = True

# ==================== MODELOS DE ASIGNACIÓN ====================

class JobAssignment(BaseModel):
    """Asignación de trabajo a nodo"""
    job_id: str
    node_id: str
    assigned_at: datetime
    status: str = "assigned"  # assigned, downloading, rendering, uploading, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = Field(0, ge=0, le=100)
    current_frame: int = 0
    estimated_completion: Optional[datetime] = None

class NodeWorkload(BaseModel):
    """Carga de trabajo actual del nodo"""
    node_id: str
    current_load: float = Field(ge=0.0, le=100.0)
    active_assignments: List[JobAssignment]
    queue_position: int = Field(0, ge=0)
    estimated_available_at: Optional[datetime] = None
    resource_usage: Dict[str, float] = Field(default_factory=dict)

# ==================== MODELOS DE CONFIGURACIÓN ====================

class NodeConfig(BaseModel):
    """Configuración de un nodo"""
    node_name: str = ""
    master_url: str = "http://localhost:8000"
    node_port: int = Field(8001, ge=1024, le=65535)
    max_concurrent_jobs: int = Field(1, ge=1, le=10)
    temp_dir: str = "./temp"
    output_dir: str = "./renders"
    blender_path: str = ""
    heartbeat_interval: int = Field(10, ge=5, le=300)
    auto_start: bool = True
    gpu_enabled: bool = True
    cpu_cores: int = -1  # -1 = usar todos
    max_memory_gb: int = Field(8, ge=1)
    priority_weight: float = Field(1.0, ge=0.1, le=10.0)
    tags: List[str] = Field(default_factory=list)
    network_timeout: int = Field(30, ge=5, le=300)
    retry_attempts: int = Field(3, ge=1, le=10)
    cleanup_interval: int = Field(3600, ge=300)  # 1 hora por defecto

class NodeUpdate(BaseModel):
    """Actualización de configuración de nodo"""
    node_name: Optional[str] = None
    status: Optional[NodeStatus] = None
    capabilities: Optional[NodeCapabilities] = None
    tags: Optional[List[str]] = None
    priority_weight: Optional[float] = Field(None, ge=0.1, le=10.0)
    max_concurrent_jobs: Optional[int] = Field(None, ge=1, le=10)

# ==================== MODELOS DE ESTADÍSTICAS ====================

class NodeStatistics(BaseModel):
    """Estadísticas detalladas del nodo"""
    node_id: str
    uptime_seconds: float
    total_jobs_processed: int = 0
    jobs_completed: int = 0
    jobs_failed: int = 0
    total_render_time: float = 0.0
    average_job_time: float = 0.0
    efficiency_score: float = 100.0
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    peak_gpu_usage: float = 0.0
    total_frames_rendered: int = 0
    frames_per_hour: float = 0.0
    errors_last_24h: int = 0
    warnings_last_24h: int = 0

class NodesOverview(BaseModel):
    """Vista general de todos los nodos"""
    total_nodes: int
    online_nodes: int
    busy_nodes: int
    idle_nodes: int
    offline_nodes: int
    error_nodes: int
    maintenance_nodes: int
    total_capacity: int
    current_load: int
    utilization_percent: float
    average_efficiency: float
    
class NodePerformance(BaseModel):
    """Métricas de rendimiento de nodo"""
    node_id: str
    period_start: datetime
    period_end: datetime
    jobs_completed: int = 0
    total_render_time: float = 0.0
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    average_gpu_usage: float = 0.0
    peak_resources: Dict[str, float] = Field(default_factory=dict)
    reliability_score: float = Field(100.0, ge=0.0, le=100.0)
    speed_score: float = Field(100.0, ge=0.0, le=100.0)

# ==================== MODELOS DE FILTROS ====================

class NodeFilter(BaseModel):
    """Filtros para búsqueda de nodos"""
    status: Optional[List[NodeStatus]] = None
    platform: Optional[List[NodePlatform]] = None
    tags: Optional[List[str]] = None
    gpu_available: Optional[bool] = None
    min_cores: Optional[int] = Field(None, ge=1)
    min_memory_gb: Optional[int] = Field(None, ge=1)
    blender_available: Optional[bool] = None
    registered_after: Optional[datetime] = None
    last_seen_after: Optional[datetime] = None

class NodeSearch(BaseModel):
    """Parámetros de búsqueda de nodos"""
    query: Optional[str] = Field(None, max_length=100)
    filters: Optional[NodeFilter] = None
    sort_by: str = Field("last_seen", regex="^(node_name|status|last_seen|efficiency_score|total_jobs_completed)$")
    sort_order: str = Field("desc", regex="^(asc|desc)$")
    include_offline: bool = False

# ==================== MODELOS DE MANTENIMIENTO ====================

class NodeMaintenance(BaseModel):
    """Programar mantenimiento de nodo"""
    node_id: str
    maintenance_type: str = Field(regex="^(update|restart|cleanup|diagnostic)$")
    scheduled_at: datetime
    estimated_duration_minutes: int = Field(30, ge=1, le=1440)  # máximo 24 horas
    description: Optional[str] = None
    allow_job_completion: bool = True
    notify_users: bool = True

class NodeDiagnostic(BaseModel):
    """Diagnóstico de nodo"""
    node_id: str
    timestamp: datetime
    overall_health: str = Field(regex="^(healthy|warning|critical|unknown)$")
    checks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

# ==================== FUNCIONES DE VALIDACIÓN ====================

def validate_node_requirements(node_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validar que un nodo cumple los requisitos mínimos"""
    errors = []
    warnings = []
    
    # Validar recursos mínimos
    memory_gb = node_data.get("system_stats", {}).get("memory_total_gb", 0)
    if memory_gb < 2:
        errors.append("Memoria insuficiente: mínimo 2GB requeridos")
    elif memory_gb < 4:
        warnings.append("Memoria baja: se recomienda al menos 4GB")
    
    cpu_cores = node_data.get("node_info", {}).get("cpu_cores_logical", 0)
    if cpu_cores < 2:
        errors.append("CPU insuficiente: mínimo 2 cores requeridos")
    
    # Validar Blender
    if not node_data.get("capabilities", {}).get("blender_available", False):
        errors.append("Blender no disponible en el nodo")
    
    # Validar conectividad
    disk_free_gb = node_data.get("system_stats", {}).get("disk_free_gb", 0)
    if disk_free_gb < 1:
        errors.append("Espacio en disco insuficiente: mínimo 1GB libre")
    elif disk_free_gb < 5:
        warnings.append("Poco espacio en disco: se recomienda al menos 5GB libre")
    
    return {
        "meets_requirements": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def calculate_node_score(node_stats: NodeStatistics) -> float:
    """Calcular puntuación global del nodo (0-100)"""
    # Factores de puntuación
    uptime_score = min(100.0, (node_stats.uptime_seconds / (24 * 3600)) * 10)  # 10 puntos por día de uptime
    
    # Eficiencia de trabajos
    if node_stats.total_jobs_processed > 0:
        success_rate = (node_stats.jobs_completed / node_stats.total_jobs_processed) * 100
        efficiency_score = (success_rate + node_stats.efficiency_score) / 2
    else:
        efficiency_score = node_stats.efficiency_score
    
    # Velocidad relativa
    speed_factor = 1.0
    if node_stats.average_job_time > 0:
        # Asumir 30 minutos como tiempo promedio base
        base_time = 30 * 60  # 30 minutos en segundos
        speed_factor = min(2.0, base_time / node_stats.average_job_time)
    
    # Estabilidad (menos errores = mejor puntuación)
    stability_score = max(0, 100 - (node_stats.errors_last_24h * 5))
    
    # Puntuación final ponderada
    final_score = (
        uptime_score * 0.2 +
        efficiency_score * 0.4 +
        (speed_factor * 50) * 0.2 +
        stability_score * 0.2
    )
    
    return min(100.0, max(0.0, final_score))

def find_best_node_for_job(available_nodes: List[NodeResponse], job_requirements: Dict[str, Any]) -> Optional[str]:
    """Encontrar el mejor nodo para un trabajo específico"""
    if not available_nodes:
        return None
    
    scored_nodes = []
    
    for node in available_nodes:
        score = 0.0
        
        # Puntuación base por eficiencia
        score += node.efficiency_score * 0.3
        
        # Disponibilidad (menos trabajos activos = mejor)
        capacity = node.capabilities.concurrent_jobs
        load_factor = 1.0 - (node.active_jobs / capacity)
        score += load_factor * 30
        
        # Capacidades específicas
        required_engine = job_requirements.get("render_engine", "CYCLES")
        if required_engine in node.capabilities.supported_engines:
            score += 20
        
        # GPU disponible si el trabajo lo requiere
        if job_requirements.get("gpu_required", False):
            if node.capabilities.gpu_rendering:
                score += 15
            else:
                score -= 20  # Penalizar si GPU es requerida pero no disponible
        
        # Memoria suficiente
        required_memory = job_requirements.get("min_memory_gb", 4)
        if node.system_stats.memory_total_gb >= required_memory:
            score += 10
        else:
            score -= 15
        
        # Tags coincidentes
        job_tags = set(job_requirements.get("tags", []))
        node_tags = set(node.tags)
        matching_tags = len(job_tags.intersection(node_tags))
        score += matching_tags * 5
        
        scored_nodes.append((node.node_id, score))
    
    # Ordenar por puntuación y devolver el mejor
    scored_nodes.sort(key=lambda x: x[1], reverse=True)
    return scored_nodes[0][0] if scored_nodes else None