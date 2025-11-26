
import bpy
try:
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.compute_device_type = 'CUDA'
    
    for device in cprefs.devices:
        if device.type in {'CUDA', 'OPTIX'}:
            device.use = True
except: pass
