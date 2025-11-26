
import bpy

# Configurar motor de render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'

try:
    # Configurar dispositivo de render
    if hasattr(bpy.context.preferences.addons.get("cycles"), "preferences"):
        cycles_prefs = bpy.context.preferences.addons["cycles"].preferences
        cycles_prefs.compute_device_type = 'CUDA'  # o 'OPENCL' según GPU
        
        # Habilitar todos los dispositivos GPU disponibles
        for device in cycles_prefs.devices:
            if device.type in {'CUDA', 'OPENCL'}:
                device.use = True

    # Configurar scene para usar GPU
    scene.cycles.device = 'GPU'
    print("✓ GPU configurado correctamente")
except Exception as e:
    print(f"⚠ No se pudo configurar GPU: {e}")
    print("→ Usando CPU como fallback")
    scene.cycles.device = 'CPU'
