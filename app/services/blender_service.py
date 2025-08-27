# app/services/blender_service.py - Servicio de gestión de Blender
import subprocess
import platform
import os
import re
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

class BlenderService:
    """Servicio para gestión de Blender y análisis de archivos .blend"""
    
    def __init__(self):
        self.settings = settings
        self._blender_cache = {}  # Cache para paths verificados
    
    def scan_for_blender(self) -> List[Dict]:
        """Escanear sistema buscando instalaciones de Blender"""
        logger.info("🔍 Escaneando instalaciones de Blender...")
        
        found_installations = []
        system = platform.system()
        possible_paths = []
        
        if system == "Windows":
            base_paths = [
                r"C:\Program Files\Blender Foundation",
                r"C:\Program Files (x86)\Blender Foundation",
                r"C:\Blender",
                os.path.expanduser(r"~\AppData\Local\Programs\Blender Foundation"),
                os.path.expanduser(r"~\Desktop")
            ]
            
            for base_path in base_paths:
                if os.path.exists(base_path):
                    try:
                        for item in os.listdir(base_path):
                            if "blender" in item.lower():
                                blender_exe = os.path.join(base_path, item, "blender.exe")
                                if os.path.exists(blender_exe):
                                    possible_paths.append(blender_exe)
                    except PermissionError:
                        logger.warning(f"⚠️ Sin permisos para acceder a: {base_path}")
                        continue
            
            # Rutas específicas adicionales
            specific_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.5\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.4\blender.exe",
                r"C:\Program Files (x86)\Blender Foundation\Blender 4.4\blender.exe",
                r"C:\Program Files (x86)\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files (x86)\Blender Foundation\Blender 3.6\blender.exe"
            ]
            possible_paths.extend(specific_paths)
            
        elif system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "/usr/local/bin/blender",
                os.path.expanduser("~/Applications/Blender.app/Contents/MacOS/Blender")
            ]
        elif system == "Linux":
            possible_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender", 
                "/opt/blender/blender",
                "/snap/bin/blender",
                os.path.expanduser("~/blender/blender")
            ]
        
        # Verificar cada path
        for path in set(possible_paths):  # set para eliminar duplicados
            if os.path.exists(path):
                verification = self._verify_blender_installation(path)
                found_installations.append({
                    "path": path,
                    "version": verification.get("version", "Desconocida"),
                    "full_version_info": verification.get("full_version", ""),
                    "working": verification.get("valid", False),
                    "valid": verification.get("valid", False),
                    "error": verification.get("error"),
                    "render_capable": verification.get("render_capable", False)
                })
        
        logger.info(f"✅ Encontradas {len(found_installations)} instalaciones de Blender")
        return found_installations
    
    def _verify_blender_installation(self, path: str) -> Dict:
        """Verificar una instalación específica de Blender"""
        if path in self._blender_cache:
            return self._blender_cache[path]
        
        try:
            cmd = [path, "--version"]
            if platform.system() == "Windows":
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=10,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version_line = result.stdout.strip().split('\n')[0] if result.stdout else ""
                version = "Desconocida"
                
                # Extraer versión con regex
                version_match = re.search(r'Blender (\d+\.\d+\.\d+)', version_line)
                if version_match:
                    version = version_match.group(1)
                
                verification = {
                    "valid": True,
                    "version": version,
                    "full_version": version_line,
                    "render_capable": True,
                    "error": None
                }
            else:
                verification = {
                    "valid": False,
                    "version": "Error",
                    "error": f"Error ejecutando: {result.stderr[:100] if result.stderr else 'Código de error: ' + str(result.returncode)}"
                }
        
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            verification = {
                "valid": False,
                "version": "Error",
                "error": f"Error: {str(e)[:100]}"
            }
        
        # Cachear resultado
        self._blender_cache[path] = verification
        return verification
    
    def get_current_blender_path(self) -> Optional[str]:
        """Obtener el path actual de Blender según configuración"""
        blender_config = self.settings.get_blender_config()
        
        if blender_config["custom_path"] and os.path.exists(blender_config["custom_path"]):
            return blender_config["custom_path"]
        elif blender_config["path"] and os.path.exists(blender_config["path"]):
            return blender_config["path"]
        elif blender_config["auto_detect"]:
            installations = self.scan_for_blender()
            if installations:
                working_installations = [inst for inst in installations if inst["working"]]
                if working_installations:
                    # Ordenar por versión y tomar la más reciente
                    working_installations.sort(key=lambda x: x.get("version", "0"), reverse=True)
                    return working_installations[0]["path"]
        
        return None
    
    def verify_blender_path(self, path: str) -> Dict:
        """Verificar que un path de Blender funciona completamente"""
        if not path or not os.path.exists(path):
            return {
                "valid": False,
                "error": "El archivo no existe",
                "version": None,
                "render_capable": False
            }
        
        try:
            # Verificar versión básica
            basic_verification = self._verify_blender_installation(path)
            if not basic_verification["valid"]:
                return basic_verification
            
            # Verificar capacidades de render más profundas
            test_cmd = [
                path, "--background", "--python-expr", 
                """
import bpy
import sys
try:
    # Verificar que puede crear escena básica
    bpy.ops.mesh.primitive_cube_add()
    
    # Verificar motores de render
    engines = []
    if hasattr(bpy.context.scene.render, 'engine'):
        bpy.context.scene.render.engine = 'CYCLES'
        engines.append('CYCLES')
        
        try:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE'
            engines.append('EEVEE')
        except:
            pass
    
    print(f"RENDER_ENGINES:{','.join(engines)}")
    print("RENDER_TEST_SUCCESS")
    
except Exception as e:
    print(f"RENDER_TEST_ERROR:{str(e)}")
    sys.exit(1)
"""
            ]
            
            if platform.system() == "Windows":
                test_result = subprocess.run(
                    test_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
            
            render_capable = "RENDER_TEST_SUCCESS" in test_result.stdout
            
            # Extraer motores soportados
            supported_engines = []
            for line in test_result.stdout.split('\n'):
                if line.startswith("RENDER_ENGINES:"):
                    supported_engines = line.split(':')[1].split(',') if ':' in line else []
            
            return {
                "valid": True,
                "version": basic_verification["version"],
                "full_version": basic_verification["full_version"],
                "render_capable": render_capable,
                "supported_engines": supported_engines,
                "error": None if render_capable else "Blender responde pero no puede renderizar correctamente"
            }
            
        except subprocess.TimeoutExpired:
            return {
                "valid": False,
                "error": "Timeout al verificar capacidades de render",
                "version": None,
                "render_capable": False
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error verificando capacidades: {str(e)}",
                "version": None,
                "render_capable": False
            }
    
    def get_blend_file_info(self, blend_file_path: str) -> Dict:
        """Extraer información del archivo .blend usando Blender"""
        if not os.path.exists(blend_file_path):
            return {"error": "Archivo .blend no encontrado"}
        
        current_blender = self.get_current_blender_path()
        if not current_blender:
            return {"error": "Blender no está configurado"}
        
        try:
            # Script Python para extraer información de la escena
            python_script = '''
import bpy
import json
import sys
import os

try:
    # Obtener información de la escena
    scene = bpy.context.scene
    
    # Obtener configuración de output
    render = scene.render
    output_path = render.filepath
    
    # Si el path es relativo, convertirlo a absoluto basado en el archivo .blend
    if output_path.startswith('//'):
        blend_dir = os.path.dirname(bpy.data.filepath)
        output_path = os.path.join(blend_dir, output_path[2:])
        output_path = os.path.normpath(output_path)
    
    # Obtener información de samples según el motor
    samples = 128  # valor por defecto
    if scene.render.engine == 'CYCLES':
        samples = scene.cycles.samples if hasattr(scene, 'cycles') else 128
    elif scene.render.engine == 'BLENDER_EEVEE':
        samples = scene.eevee.taa_render_samples if hasattr(scene, 'eevee') else 64
    
    # Obtener información de objetos y complejidad
    total_objects = len(bpy.data.objects)
    total_meshes = len(bpy.data.meshes)
    total_materials = len(bpy.data.materials)
    total_textures = len(bpy.data.textures)
    total_lights = len([obj for obj in bpy.data.objects if obj.type == 'LIGHT'])
    
    # Calcular complejidad de la escena
    complexity_score = min(10.0, (total_objects * 0.01 + total_materials * 0.05 + total_textures * 0.02 + samples / 50))
    
    info = {
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_current": scene.frame_current,
        "fps": scene.render.fps,
        "fps_base": scene.render.fps_base,
        "render_engine": scene.render.engine,
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "resolution_percentage": scene.render.resolution_percentage,
        "file_format": scene.render.image_settings.file_format.lower(),
        "samples": samples,
        "scene_name": scene.name,
        "total_frames": (scene.frame_end - scene.frame_start) + 1,
        "output_path": output_path,
        "output_format": render.image_settings.file_format,
        "color_mode": render.image_settings.color_mode,
        "color_depth": render.image_settings.color_depth,
        "compression": getattr(render.image_settings, 'compression', 15),
        "quality": getattr(render.image_settings, 'quality', 90),
        
        # Información adicional de la escena
        "total_objects": total_objects,
        "total_meshes": total_meshes,
        "total_materials": total_materials,
        "total_textures": total_textures,
        "total_lights": total_lights,
        "complexity_score": complexity_score,
        
        # Configuraciones específicas del motor
        "engine_settings": {},
        
        # Información de assets externos
        "external_assets": [],
        "missing_assets": [],
        
        # Warnings y recomendaciones
        "warnings": [],
        "recommendations": []
    }
    
    # Configuraciones específicas según motor
    if scene.render.engine == 'CYCLES':
        info["engine_settings"] = {
            "samples": samples,
            "use_denoising": getattr(scene.cycles, 'use_denoising', False),
            "max_bounces": getattr(scene.cycles, 'max_bounces', 12),
            "diffuse_bounces": getattr(scene.cycles, 'diffuse_bounces', 4),
            "glossy_bounces": getattr(scene.cycles, 'glossy_bounces', 4),
            "transmission_bounces": getattr(scene.cycles, 'transmission_bounces', 12),
            "volume_bounces": getattr(scene.cycles, 'volume_bounces', 0),
            "caustics_reflective": getattr(scene.cycles, 'caustics_reflective', True),
            "caustics_refractive": getattr(scene.cycles, 'caustics_refractive', True)
        }
    elif scene.render.engine == 'BLENDER_EEVEE':
        info["engine_settings"] = {
            "taa_render_samples": samples,
            "use_bloom": getattr(scene.eevee, 'use_bloom', False),
            "use_ssr": getattr(scene.eevee, 'use_ssr', True),
            "use_motion_blur": getattr(scene.eevee, 'use_motion_blur', False),
            "volumetric_samples": getattr(scene.eevee, 'volumetric_samples', 64)
        }
    
    # Detectar assets externos
    for img in bpy.data.images:
        if img.source == 'FILE' and img.filepath:
            filepath = bpy.path.abspath(img.filepath)
            info["external_assets"].append({
                "name": img.name,
                "filepath": filepath,
                "type": "image",
                "exists": os.path.exists(filepath)
            })
            if not os.path.exists(filepath):
                info["missing_assets"].append(filepath)
                info["warnings"].append(f"Textura faltante: {img.name}")
    
    # Generar warnings y recomendaciones
    if samples > 1000:
        info["warnings"].append(f"Samples muy alto ({samples}), puede ser lento")
    
    if info["total_frames"] > 500:
        info["recommendations"].append("Considere dividir la animación en lotes más pequeños")
    
    if resolution_x * resolution_y > 1920 * 1080:
        info["recommendations"].append("Resolución alta detectada, considere render en resolución menor para pruebas")
    
    if len(info["missing_assets"]) > 0:
        info["warnings"].append(f"{len(info['missing_assets'])} assets faltantes detectados")
    
    print("BLEND_INFO_START")
    print(json.dumps(info, indent=2))
    print("BLEND_INFO_END")
    
except Exception as e:
    print(f"ERROR_EXTRACTING_INFO: {str(e)}")
'''
            
            # Comando para ejecutar Blender con el script
            cmd = [
                current_blender,
                "-b",  # Background mode
                blend_file_path,
                "--python-expr", python_script
            ]
            
            logger.info(f"🔍 Extrayendo información de: {blend_file_path}")
            
            # Ejecutar comando
            if platform.system() == "Windows":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=45,  # Aumentado timeout para archivos complejos
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            if result.returncode != 0:
                return {"error": f"Error ejecutando Blender: {result.stderr}"}
            
            # Extraer información del output
            output = result.stdout
            
            # Buscar la información entre los marcadores
            start_marker = "BLEND_INFO_START"
            end_marker = "BLEND_INFO_END"
            
            if start_marker in output and end_marker in output:
                start_idx = output.find(start_marker) + len(start_marker)
                end_idx = output.find(end_marker)
                json_str = output[start_idx:end_idx].strip()
                
                try:
                    info = json.loads(json_str)
                    logger.info(f"📊 Información extraída: {info['total_frames']} frames ({info['frame_start']}-{info['frame_end']})")
                    logger.info(f"🎨 Motor: {info['render_engine']}, Samples: {info['samples']}")
                    logger.info(f"📁 Output configurado: {info.get('output_path', 'Default')}")
                    
                    if info.get('warnings'):
                        logger.warning(f"⚠️ Warnings: {', '.join(info['warnings'])}")
                    
                    return info
                except json.JSONDecodeError as e:
                    return {"error": f"Error parseando información: {str(e)}"}
            else:
                return {"error": "No se pudo extraer información del archivo"}
                
        except subprocess.TimeoutExpired:
            return {"error": "Timeout extrayendo información del archivo (archivo muy complejo o Blender lento)"}
        except Exception as e:
            logger.error(f"Error analizando archivo .blend: {e}")
            return {"error": f"Error inesperado: {str(e)}"}
    
    def estimate_render_time(self, blend_info: Dict) -> str:
        """Estimar tiempo de render basado en configuración"""
        total_frames = blend_info.get("total_frames", 1)
        samples = blend_info.get("samples", 128)
        resolution_x = blend_info.get("resolution_x", 1920)
        resolution_y = blend_info.get("resolution_y", 1080)
        render_engine = blend_info.get("render_engine", "CYCLES")
        complexity_score = blend_info.get("complexity_score", 1.0)
        
        # Tiempo base por frame en segundos
        base_time_per_frame = 30
        
        # Ajustar según motor de render
        if render_engine == "CYCLES":
            # Cycles es más lento, depende mucho de samples
            engine_multiplier = 1.0
            samples_factor = samples / 128
            base_time_per_frame *= engine_multiplier * samples_factor
        elif render_engine in ["BLENDER_EEVEE", "EEVEE"]:
            # Eevee es mucho más rápido
            engine_multiplier = 0.2
            base_time_per_frame *= engine_multiplier
        elif render_engine == "WORKBENCH":
            # Workbench es muy rápido
            engine_multiplier = 0.05
            base_time_per_frame *= engine_multiplier
        else:
            # Otros motores (Arnold, V-Ray, etc.)
            engine_multiplier = 1.5
            base_time_per_frame *= engine_multiplier
        
        # Ajustar según resolución
        resolution_factor = (resolution_x * resolution_y) / (1920 * 1080)
        base_time_per_frame *= resolution_factor
        
        # Ajustar según complejidad de la escena
        complexity_factor = min(3.0, complexity_score)
        base_time_per_frame *= complexity_factor
        
        # Calcular tiempo total
        total_seconds = total_frames * base_time_per_frame
        
        # Formatear tiempo legible
        return self._format_time_duration(total_seconds)
    
    def _format_time_duration(self, seconds: float) -> str:
        """Formatear duración en formato legible"""
        if seconds < 60:
            return f"~{int(seconds)} segundos"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"~{minutes} minutos"
        elif seconds < 86400:  # menos de 1 día
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            if minutes > 0:
                return f"~{hours}h {minutes}m"
            else:
                return f"~{hours} horas"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            if hours > 0:
                return f"~{days}d {hours}h"
            else:
                return f"~{days} días"
    
    def validate_blend_file(self, blend_file_path: str) -> Dict:
        """Validar archivo .blend antes de enviarlo a render"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        # Verificar que el archivo existe
        if not os.path.exists(blend_file_path):
            validation_result["valid"] = False
            validation_result["errors"].append("Archivo .blend no encontrado")
            return validation_result
        
        # Verificar tamaño del archivo
        file_size = os.path.getsize(blend_file_path)
        if file_size > 500 * 1024 * 1024:  # 500MB
            validation_result["warnings"].append(f"Archivo muy grande ({file_size // (1024*1024)}MB)")
        
        # Intentar extraer información
        blend_info = self.get_blend_file_info(blend_file_path)
        
        if "error" in blend_info:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Error analizando archivo: {blend_info['error']}")
            return validation_result
        
        validation_result["info"] = blend_info
        
        # Validaciones específicas
        total_frames = blend_info.get("total_frames", 1)
        if total_frames > 1000:
            validation_result["warnings"].append(f"Muchos frames ({total_frames}). Considere dividir en lotes.")
        
        # Verificar assets faltantes
        missing_assets = blend_info.get("missing_assets", [])
        if missing_assets:
            validation_result["warnings"].append(f"{len(missing_assets)} assets faltantes")
            validation_result["missing_assets"] = missing_assets
        
        # Verificar configuración de output
        if not blend_info.get("output_path"):
            validation_result["warnings"].append("No se configuró directorio de salida en el archivo .blend")
        
        # Agregar warnings del análisis
        if blend_info.get("warnings"):
            validation_result["warnings"].extend(blend_info["warnings"])
        
        return validation_result
    
    def get_recommended_settings(self, blend_info: Dict) -> Dict:
        """Obtener configuraciones recomendadas basadas en el archivo .blend"""
        recommendations = {
            "frame_start": blend_info.get("frame_start", 1),
            "frame_end": blend_info.get("frame_end", 1),
            "render_engine": blend_info.get("render_engine", "CYCLES"),
            "total_frames": blend_info.get("total_frames", 1),
            "estimated_time": self.estimate_render_time(blend_info),
            "priority": "normal",
            "distribution_type": "local"
        }
        
        # Ajustar prioridad según complejidad
        complexity = blend_info.get("complexity_score", 1.0)
        total_frames = blend_info.get("total_frames", 1)
        
        if complexity > 5.0 or total_frames > 250:
            recommendations["distribution_type"] = "distributed"
            recommendations["priority"] = "normal"
        elif total_frames > 100:
            recommendations["distribution_type"] = "distributed"
        
        # Recomendar configuración según motor
        render_engine = blend_info.get("render_engine", "CYCLES")
        if render_engine == "CYCLES":
            samples = blend_info.get("samples", 128)
            if samples > 512:
                recommendations["priority"] = "low"  # Samples muy altos = prioridad baja
        
        return recommendations
    
    def auto_detect_and_configure(self) -> bool:
        """Auto-detectar y configurar Blender automáticamente"""
        logger.info("🔄 Auto-detectando y configurando Blender...")
        
        installations = self.scan_for_blender()
        working_installations = [inst for inst in installations if inst["valid"]]
        
        if not working_installations:
            logger.error("❌ No se encontraron instalaciones válidas de Blender")
            return False
        
        # Seleccionar la mejor instalación (más reciente)
        best_installation = max(working_installations, key=lambda x: x.get("version", "0"))
        
        # Actualizar configuración
        blender_config = self.settings.get_blender_config()
        blender_config.update({
            "path": best_installation["path"],
            "version": best_installation["version"],
            "auto_detect": True,
            "last_verified": datetime.now().isoformat()
        })
        
        success = self.settings.update_blender_config(blender_config)
        
        if success:
            logger.info(f"✅ Blender configurado: {best_installation['path']} (v{best_installation['version']})")
        else:
            logger.error("❌ Error guardando configuración de Blender")
        
        return success
    
    def test_render_capability(self, blender_path: str) -> Dict:
        """Probar capacidades de render de una instalación de Blender"""
        test_result = {
            "success": False,
            "render_engines": [],
            "gpu_support": False,
            "test_time": 0.0,
            "errors": []
        }
        
        if not os.path.exists(blender_path):
            test_result["errors"].append("Blender no encontrado")
            return test_result
        
        try:
            import time
            start_time = time.time()
            
            # Script de prueba más completo
            test_script = '''
import bpy
import time
import sys

start_time = time.time()
test_results = {
    "engines": [],
    "gpu_support": False,
    "errors": []
}

try:
    # Limpiar escena por defecto
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Crear objeto de prueba
    bpy.ops.mesh.primitive_cube_add()
    
    # Probar Cycles
    try:
        bpy.context.scene.render.engine = 'CYCLES'
        test_results["engines"].append("CYCLES")
        
        # Verificar soporte GPU
        import addon_utils
        addon_utils.enable("cycles")
        
        if hasattr(bpy.context.scene.cycles, 'device'):
            test_results["gpu_support"] = True
            
    except Exception as e:
        test_results["errors"].append(f"Cycles error: {str(e)}")
    
    # Probar Eevee
    try:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
        test_results["engines"].append("EEVEE")
    except Exception as e:
        test_results["errors"].append(f"Eevee error: {str(e)}")
    
    # Probar Workbench
    try:
        bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
        test_results["engines"].append("WORKBENCH")
    except Exception as e:
        test_results["errors"].append(f"Workbench error: {str(e)}")
    
    # Prueba básica de render (1 frame)
    bpy.context.scene.render.resolution_x = 64
    bpy.context.scene.render.resolution_y = 64
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'  # Más rápido para prueba
    
    # No hacer render real, solo verificar que se puede configurar
    print("TEST_SUCCESS")
    
except Exception as e:
    test_results["errors"].append(f"General error: {str(e)}")
    print(f"TEST_ERROR: {str(e)}")

end_time = time.time()
test_duration = end_time - start_time

print(f"ENGINES:{','.join(test_results['engines'])}")
print(f"GPU_SUPPORT:{test_results['gpu_support']}")
print(f"TEST_TIME:{test_duration:.2f}")
if test_results["errors"]:
    print(f"ERRORS:{';'.join(test_results['errors'])}")
'''
            
            cmd = [blender_path, "--background", "--python-expr", test_script]
            
            if platform.system() == "Windows":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            test_result["test_time"] = time.time() - start_time
            
            if result.returncode == 0 and "TEST_SUCCESS" in result.stdout:
                test_result["success"] = True
                
                # Extraer información del output
                for line in result.stdout.split('\n'):
                    if line.startswith("ENGINES:"):
                        engines_str = line.split(':')[1] if ':' in line else ""
                        test_result["render_engines"] = engines_str.split(',') if engines_str else []
                    elif line.startswith("GPU_SUPPORT:"):
                        test_result["gpu_support"] = line.split(':')[1].strip().lower() == 'true'
                    elif line.startswith("ERRORS:"):
                        errors_str = line.split(':', 1)[1] if ':' in line else ""
                        test_result["errors"] = errors_str.split(';') if errors_str else []
            else:
                test_result["errors"].append(f"Test failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            test_result["errors"].append("Test timeout - Blender muy lento")
        except Exception as e:
            test_result["errors"].append(f"Test error: {str(e)}")
        
        return test_result
    
    def clear_cache(self):
        """Limpiar cache de verificaciones de Blender"""
        self._blender_cache.clear()
        logger.info("🧹 Cache de Blender limpiado")

# Instancia singleton del servicio
blender_service = BlenderService()