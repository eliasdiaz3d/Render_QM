import asyncio
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Callable, Dict

logger = logging.getLogger("RenderExecutor")

class RenderExecutor:
    def __init__(self, blender_executable: str):
        self.blender_executable = blender_executable
        self.process: Optional[asyncio.subprocess.Process] = None
        self._stop_event = asyncio.Event()

    async def execute_render(
        self,
        blend_file: str,
        output_path: str,
        start_frame: int,
        end_frame: int,
        gpu_script: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> bool:
        """
        Ejecuta el render manejando el flujo de stdout/stderr de forma asíncrona
        para evitar bloqueos por buffer lleno (Deadlocks).
        """
        self._stop_event.clear()

        # 1. Construir el comando
        # Nota: Usamos frames individuales (-f) o rango (-s -e -a) según sea necesario.
        # Para simplificar y asegurar control, aquí usamos formato de rango básico.
        
        cmd = [
            self.blender_executable,
            "-b", blend_file,
        ]

        # Agregar script de GPU si existe
        if gpu_script and os.path.exists(gpu_script):
            cmd.extend(["-P", gpu_script])
        
        # Configurar salida
        # Blender espera #### para el número de frame
        output_pattern = os.path.join(output_path, "frame_####")
        cmd.extend(["-o", output_pattern])
        
        # Configurar motor (opcional, generalmente ya está en el archivo, 
        # pero forzamos CYCLES/EEVEE si fuera necesario, aquí confiamos en el .blend)
        
        # Configurar frames
        # Usamos -s y -e con -a (animación) para el rango
        cmd.extend(["-s", str(start_frame), "-e", str(end_frame), "-a"])

        logger.info(f"🚀 Ejecutando comando: {' '.join(cmd)}")

        try:
            # 2. Iniciar el subproceso
            # IMPORTANTE: stdout y stderr deben ser PIPEs para leerlos asíncronamente
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            # 3. Leer la salida en tiempo real sin bloquear
            # Creamos tareas para leer stdout y stderr simultáneamente
            await asyncio.gather(
                self._read_stream(self.process.stdout, "STDOUT", progress_callback),
                self._read_stream(self.process.stderr, "STDERR", None)
            )

            # 4. Esperar a que termine
            return_code = await self.process.wait()
            
            if return_code == 0:
                logger.info("✅ Render finalizado correctamente.")
                return True
            else:
                logger.error(f"❌ Blender terminó con código de error: {return_code}")
                return False

        except asyncio.CancelledError:
            logger.warning("⚠️ Render cancelado por el usuario.")
            await self.cancel_render()
            return False
        except Exception as e:
            logger.error(f"❌ Error crítico ejecutando Blender: {e}")
            return False
        finally:
            self.process = None

    async def _read_stream(self, stream, label, callback):
        """
        Lee el flujo línea por línea. VERSIÓN DEBUG: Muestra más actividad.
        """
        if stream is None:
            return

        # Regex para capturar progreso
        progress_regex = re.compile(r"Fra:(\d+).*Sample\s+(\d+)/(\d+)")

        while True:
            line_bytes = await stream.readline()
            if not line_bytes:
                break
            
            line = line_bytes.decode('utf-8', errors='replace').strip()
            if not line:
                continue

            # --- FILTRO RELAJADO ---
            # Solo ocultamos lo verdaderamente inútil
            if "register_class" in line or "AttributeError" in line:
                continue
            
            # IMPRIMIR TODO LO DEMÁS (Para ver si Blender vive)
            # Esto nos dirá si está cargando kernels, texturas, etc.
            print(f"[{label}] {line}")

            # --- DETECCIÓN DE PROGRESO ---
            if line.startswith("Fra:"):
                match = progress_regex.search(line)
                if match and callback:
                    frame = int(match.group(1))
                    sample = int(match.group(2))
                    total = int(match.group(3))
                    percent = (sample / total) * 100
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(percent, f"Frame {frame}: {sample}/{total}")
                        else:
                            callback(percent, f"Frame {frame}: {sample}/{total}")
                    except:
                        pass

    async def cancel_render(self):
        """Mata el proceso de Blender si está corriendo."""
        if self.process:
            logger.info("🛑 Enviando señal de terminación a Blender...")
            try:
                self.process.terminate()
                # Darle 5 segundos para cerrar
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("💀 Blender no cerró, forzando kill...")
                    self.process.kill()
            except ProcessLookupError:
                pass
            logger.info("Render detenido.")

    def create_gpu_script(self, script_path: str, devices_config: Dict):
        """
        Genera el script de Python que configura la GPU dentro de Blender.
        (Mantenemos la lógica que ya tenías o una versión segura)
        """
        # Esta lógica suele estar en NodeAgent, pero si se requiere aquí, 
        # asegúrate de que quien llame a execute_render ya haya creado el script.
        pass