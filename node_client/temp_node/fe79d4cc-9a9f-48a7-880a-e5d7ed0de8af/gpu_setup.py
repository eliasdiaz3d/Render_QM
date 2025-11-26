
import bpy
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
try:
    if hasattr(bpy.context.preferences.addons.get("cycles"), "preferences"):
        cycles_prefs = bpy.context.preferences.addons["cycles"].preferences
        cycles_prefs.compute_device_type = 'CUDA'
        for device in cycles_prefs.devices:
            if device.type in {'CUDA', 'OPENCL'}:
                device.use = True
    scene.cycles.device = 'GPU'
    print("✓ GPU configurado correctamente")
except Exception as e:
    print(f"⚠ Fallo GPU: {e}")
