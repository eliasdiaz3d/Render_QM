
    import bpy

    # Habilitar GPU para Cycles
    try:
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'

        # Configurar dispositivos
        prefs = bpy.context.preferences
        cprefs = prefs.addons['cycles'].preferences

        # Habilitar todos los dispositivos GPU disponibles
        cprefs.compute_device_type = 'CUDA' # O 'OPTIX', 'HIP', 'METAL'
        for device in cprefs.devices:
            if device.type != 'CPU':
                device.use = True
                print(f"GPU habilitada: {device.name}")
    except Exception as e:
        print(f"No se pudo configurar la GPU: {e}")
    