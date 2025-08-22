# ========== backend/app/services/render_engine.py ==========
"""
Interfaz con Blender y motores de render
"""
import subprocess
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.config import settings

class BlenderRenderer:
    def __init__(self, blender_path: str = None):
        self.blender_path = blender_path or settings.blender_path
        self.temp_dir = Path(settings.temp_dir)
        self.output_dir = Path(settings.output_dir)
        
        # Crear directorios si no existen
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    async def render_frame(self, scene_path: str, frame: int, output_path: str, render_settings: Dict[str, Any] = None):
        """Renderizar un frame específico"""
        cmd = [
            self.blender_path,
            "-b",  # background mode
            scene_path,
            "-f", str(frame),  # render frame
            "-o", output_path
        ]
        
        # Agregar configuraciones de render si se especifican
        if render_settings:
            cmd.extend(self._build_render_args(render_settings))
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def render_animation(self, scene_path: str, start_frame: int, end_frame: int, output_path: str, render_settings: Dict[str, Any] = None):
        """Renderizar animación completa"""
        cmd = [
            self.blender_path,
            "-b",
            scene_path,
            "-s", str(start_frame),  # start frame
            "-e", str(end_frame),    # end frame
            "-a",                    # render animation
            "-o", output_path
        ]
        
        if render_settings:
            cmd.extend(self._build_render_args(render_settings))
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # TODO: Monitorear progreso en tiempo real
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_render_args(self, render_settings: Dict[str, Any]) -> list:
        """Construir argumentos de render basados en configuraciones"""
        args = []
        
        # Motor de render
        if render_settings.get('engine'):
            args.extend(["-E", render_settings['engine']])
        
        # Resolución
        if render_settings.get('resolution_x') and render_settings.get('resolution_y'):
            script = f"""
import bpy
bpy.context.scene.render.resolution_x = {render_settings['resolution_x']}
bpy.context.scene.render.resolution_y = {render_settings['resolution_y']}
"""
            args.extend(["-P", self._create_temp_script(script)])
        
        # Samples (para Cycles)
        if render_settings.get('samples'):
            script = f"""
import bpy
if bpy.context.scene.render.engine == 'CYCLES':
    bpy.context.scene.cycles.samples = {render_settings['samples']}
"""
            args.extend(["-P", self._create_temp_script(script)])
        
        return args
    
    def _create_temp_script(self, script_content: str) -> str:
        """Crear script temporal de Python para Blender"""
        script_path = self.temp_dir / f"temp_script_{os.getpid()}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        return str(script_path)
    
    async def get_scene_info(self, scene_path: str) -> Dict[str, Any]:
        """Obtener información de una escena de Blender"""
        script = """
import bpy
import json

# Obtener información de la escena
scene = bpy.context.scene
info = {
    'name': scene.name,
    'frame_start': scene.frame_start,
    'frame_end': scene.frame_end,
    'frame_current': scene.frame_current,
    'render_engine': scene.render.engine,
    'resolution_x': scene.render.resolution_x,
    'resolution_y': scene.render.resolution_y,
    'fps': scene.render.fps,
    'objects_count': len(bpy.data.objects),
    'materials_count': len(bpy.data.materials),
    'textures_count': len(bpy.data.textures)
}

if scene.render.engine == 'CYCLES':
    info['samples'] = scene.cycles.samples

print(json.dumps(info))
"""
        
        script_path = self._create_temp_script(script)
        
        cmd = [
            self.blender_path,
            "-b",
            scene_path,
            "-P", script_path
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Limpiar script temporal
            os.unlink(script_path)
            
            if process.returncode == 0:
                # Extraer JSON del output
                lines = stdout.decode('utf-8').strip().split('\n')
                for line in lines:
                    try:
                        return json.loads(line)
                    except json.JSONDecodeError:
                        continue
            
            return {"error": "No se pudo obtener información de la escena"}
            
        except Exception as e:
            return {"error": str(e)}

# Instancia global del renderer
blender_renderer = BlenderRenderer()

