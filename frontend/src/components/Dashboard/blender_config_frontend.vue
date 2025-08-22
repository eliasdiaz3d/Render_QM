<template>
  <div class="bg-gray-800 rounded-lg shadow-xl p-6">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-semibold text-white flex items-center">
        <svg class="w-6 h-6 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
        Configuración de Blender
      </h3>
      
      <div class="flex space-x-2">
        <button
          @click="scanForBlender"
          :disabled="scanning"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center"
        >
          <svg v-if="scanning" class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ scanning ? 'Escaneando...' : '🔍 Auto-detectar' }}
        </button>
        
        <button
          @click="resetConfig"
          class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
        >
          🔄 Reset
        </button>
      </div>
    </div>

    <!-- Estado Actual -->
    <div class="mb-6 p-4 rounded-lg" :class="currentStatus.class">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="font-medium" :class="currentStatus.textClass">
            {{ currentStatus.icon }} {{ currentStatus.title }}
          </h4>
          <p class="text-sm mt-1" :class="currentStatus.descClass">
            {{ currentStatus.description }}
          </p>
          <p v-if="config.current_path" class="text-xs mt-1 font-mono" :class="currentStatus.descClass">
            {{ config.current_path }}
          </p>
        </div>
        
        <button
          v-if="config.current_path"
          @click="verifyCurrentPath"
          :disabled="verifying"
          class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-3 py-2 rounded text-sm transition-colors"
        >
          {{ verifying ? '⏳' : '🔍' }} Verificar
        </button>
      </div>
    </div>

    <!-- Configuración Manual -->
    <div class="space-y-6">
      <!-- Auto-detección -->
      <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
        <div>
          <h4 class="text-white font-medium">Auto-detección de Blender</h4>
          <p class="text-gray-400 text-sm">Buscar automáticamente Blender en ubicaciones comunes</p>
        </div>
        <label class="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            v-model="formData.autoDetect"
            @change="updateAutoDetect"
            class="sr-only peer"
          />
          <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>
      </div>

      <!-- Path Manual -->
      <div class="space-y-4">
        <h4 class="text-white font-medium">Configuración Manual</h4>
        
        <div class="flex space-x-3">
          <div class="flex-1">
            <input
              v-model="formData.customPath"
              type="text"
              placeholder="Ruta al ejecutable de Blender (ej: C:\Program Files\Blender Foundation\Blender 4.0\blender.exe)"
              class="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all"
            />
          </div>
          
          <button
            @click="browseForBlender"
            class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-3 rounded-lg transition-colors"
            title="Buscar archivo"
          >
            📁
          </button>
          
          <button
            @click="verifyPath"
            :disabled="!formData.customPath || verifying"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-3 rounded-lg transition-colors"
          >
            {{ verifying ? '⏳' : '✅' }}
          </button>
        </div>
      </div>

      <!-- Instalaciones Encontradas -->
      <div v-if="installations.length > 0" class="space-y-4">
        <h4 class="text-white font-medium">Instalaciones Encontradas</h4>
        
        <div class="space-y-2">
          <div
            v-for="(installation, index) in installations"
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-700 rounded-lg"
          >
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <span class="text-lg">{{ installation.working ? '✅' : '❌' }}</span>
                <div>
                  <p class="text-white text-sm font-medium">
                    Blender {{ installation.version }}
                  </p>
                  <p class="text-gray-400 text-xs font-mono">{{ installation.path }}</p>
                </div>
              </div>
            </div>
            
            <button
              v-if="installation.working"
              @click="selectInstallation(installation)"
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded text-sm transition-colors"
            >
              Usar Esta
            </button>
          </div>
        </div>
      </div>

      <!-- Botones de Acción -->
      <div class="flex space-x-4 pt-4 border-t border-gray-700">
        <button
          @click="saveConfiguration"
          :disabled="saving || (!formData.customPath && !formData.autoDetect)"
          class="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center"
        >
          <svg v-if="saving" class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ saving ? 'Guardando...' : '💾 Guardar Configuración' }}
        </button>
        
        <button
          @click="testConfiguration"
          :disabled="testing || (!formData.customPath && !config.current_path)"
          class="bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white py-3 px-6 rounded-lg font-medium transition-colors"
        >
          {{ testing ? '🧪 Probando...' : '🧪 Probar Render' }}
        </button>
      </div>
    </div>

    <!-- Información del Sistema -->
    <div class="mt-6 pt-6 border-t border-gray-700">
      <h4 class="text-white font-medium mb-3">Información del Sistema</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        <div class="bg-gray-700 p-3 rounded">
          <span class="text-gray-400">SO:</span>
          <span class="text-white ml-2">{{ systemInfo.os }}</span>
        </div>
        <div class="bg-gray-700 p-3 rounded">
          <span class="text-gray-400">Arch:</span>
          <span class="text-white ml-2">{{ systemInfo.arch }}</span>
        </div>
        <div class="bg-gray-700 p-3 rounded">
          <span class="text-gray-400">Instalaciones:</span>
          <span class="text-white ml-2">{{ installations.filter(i => i.working).length }}/{{ installations.length }}</span>
        </div>
      </div>
    </div>

    <!-- Log de Actividad -->
    <div v-if="activityLog.length > 0" class="mt-6 pt-6 border-t border-gray-700">
      <h4 class="text-white font-medium mb-3">Actividad Reciente</h4>
      <div class="space-y-2 max-h-32 overflow-y-auto">
        <div
          v-for="(log, index) in activityLog.slice(-5)"
          :key="index"
          class="text-sm p-2 bg-gray-700 rounded"
        >
          <span class="text-gray-400">{{ formatTime(log.timestamp) }}</span>
          <span class="text-white ml-2">{{ log.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BlenderConfig',
  
  data() {
    return {
      config: {
        current_config: {},
        current_path: null,
        is_working: false,
        verification: null
      },
      
      formData: {
        autoDetect: true,
        customPath: ''
      },
      
      installations: [],
      
      // Estados de carga
      loading: false,
      scanning: false,
      verifying: false,
      saving: false,
      testing: false,
      
      // Sistema
      systemInfo: {
        os: 'Detectando...',
        arch: 'Detectando...'
      },
      
      // Log de actividad
      activityLog: []
    }
  },
  
  computed: {
    currentStatus() {
      if (this.config.is_working && this.config.verification?.valid) {
        return {
          class: 'bg-green-900 border border-green-700',
          textClass: 'text-green-300',
          descClass: 'text-green-400',
          icon: '✅',
          title: 'Blender Configurado Correctamente',
          description: `Versión ${this.config.verification.version} - Listo para renderizar`
        }
      } else if (this.config.current_path) {
        return {
          class: 'bg-yellow-900 border border-yellow-700',
          textClass: 'text-yellow-300',
          descClass: 'text-yellow-400',
          icon: '⚠️',
          title: 'Blender Encontrado - Verificación Pendiente',
          description: 'Se encontró un ejecutable pero no se ha verificado'
        }
      } else {
        return {
          class: 'bg-red-900 border border-red-700',
          textClass: 'text-red-300',
          descClass: 'text-red-400',
          icon: '❌',
          title: 'Blender No Configurado',
          description: 'Configure la ruta de Blender para habilitar el renderizado'
        }
      }
    }
  },
  
  async mounted() {
    await this.loadCurrentConfig()
    this.detectSystemInfo()
  },
  
  methods: {
    async loadCurrentConfig() {
      this.loading = true
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/blender')
        if (response.ok) {
          this.config = await response.json()
          
          // Actualizar form data
          this.formData.autoDetect = this.config.current_config?.auto_detect ?? true
          this.formData.customPath = this.config.current_config?.custom_path || ''
          
          this.addLog('Configuración cargada correctamente')
        } else {
          this.addLog('Error cargando configuración', 'error')
        }
      } catch (error) {
        console.error('Error verifying:', error)
        this.addLog('Error de conexión durante la verificación', 'error')
      } finally {
        this.verifying = false
      }
    },
    
    async verifyCurrentPath() {
      if (!this.config.current_path) return
      
      this.verifying = true
      try {
        const formData = new FormData()
        formData.append('path', this.config.current_path)
        
        const response = await fetch('http://localhost:8000/api/v1/config/blender/verify', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          const data = await response.json()
          this.config.verification = data.verification
          await this.loadCurrentConfig() // Recargar configuración completa
        }
      } catch (error) {
        console.error('Error verifying current path:', error)
      } finally {
        this.verifying = false
      }
    },
    
    async saveConfiguration() {
      this.saving = true
      this.addLog('Guardando configuración...')
      
      try {
        const formData = new FormData()
        if (this.formData.customPath) {
          formData.append('path', this.formData.customPath)
        }
        formData.append('auto_detect', this.formData.autoDetect)
        formData.append('save_as_default', 'true')
        
        const response = await fetch('http://localhost:8000/api/v1/config/blender/set', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          const data = await response.json()
          this.addLog('✅ Configuración guardada exitosamente')
          
          // Recargar configuración
          await this.loadCurrentConfig()
          
          // Emitir evento para actualizar el dashboard principal
          this.$emit('config-updated', data)
          
          // Mostrar notificación de éxito
          this.showSuccess('Configuración de Blender guardada correctamente')
        } else {
          const errorData = await response.json()
          this.addLog(`❌ Error guardando: ${errorData.detail}`, 'error')
          this.showError(`Error: ${errorData.detail}`)
        }
      } catch (error) {
        console.error('Error saving config:', error)
        this.addLog('Error de conexión al guardar', 'error')
        this.showError('Error de conexión al guardar la configuración')
      } finally {
        this.saving = false
      }
    },
    
    async testConfiguration() {
      this.testing = true
      this.addLog('Iniciando prueba de render...')
      
      try {
        // Crear un trabajo de prueba simple
        const testJobData = new FormData()
        
        // Crear un archivo .blend mínimo (solo para prueba)
        const testBlendContent = new Blob(['test'], { type: 'application/octet-stream' })
        testJobData.append('file', testBlendContent, 'test.blend')
        testJobData.append('name', 'Prueba de Configuración')
        testJobData.append('frame_start', '1')
        testJobData.append('frame_end', '1')
        testJobData.append('render_engine', 'CYCLES')
        
        const response = await fetch('http://localhost:8000/api/v1/jobs/upload', {
          method: 'POST',
          body: testJobData
        })
        
        if (response.ok) {
          const data = await response.json()
          this.addLog('✅ Prueba de render iniciada correctamente')
          this.showSuccess('Prueba de configuración exitosa. Blender está funcionando correctamente.')
        } else {
          const errorData = await response.json()
          this.addLog(`❌ Error en prueba: ${errorData.detail}`, 'error')
          this.showError(`Error en la prueba: ${errorData.detail}`)
        }
      } catch (error) {
        console.error('Error testing:', error)
        this.addLog('Error de conexión durante la prueba', 'error')
        this.showError('Error de conexión durante la prueba')
      } finally {
        this.testing = false
      }
    },
    
    async resetConfig() {
      if (confirm('¿Resetear la configuración de Blender a valores por defecto?')) {
        this.addLog('Reseteando configuración...')
        
        try {
          const response = await fetch('http://localhost:8000/api/v1/config/blender/reset')
          
          if (response.ok) {
            this.addLog('✅ Configuración reseteada')
            await this.loadCurrentConfig()
            this.installations = []
            this.formData.customPath = ''
            this.formData.autoDetect = true
            this.showSuccess('Configuración reseteada correctamente')
          } else {
            this.addLog('❌ Error reseteando configuración', 'error')
          }
        } catch (error) {
          console.error('Error resetting:', error)
          this.addLog('Error de conexión al resetear', 'error')
        }
      }
    },
    
    selectInstallation(installation) {
      this.formData.customPath = installation.path
      this.addLog(`Seleccionada instalación: Blender ${installation.version}`)
    },
    
    browseForBlender() {
      // En una aplicación real, esto abriría un file picker
      // Por ahora, mostrar un prompt
      const path = prompt('Introduce la ruta completa al ejecutable de Blender:')
      if (path) {
        this.formData.customPath = path
        this.addLog(`Ruta manual introducida: ${path}`)
      }
    },
    
    async updateAutoDetect() {
      if (this.formData.autoDetect && this.installations.length === 0) {
        // Auto-escanear cuando se active la auto-detección
        await this.scanForBlender()
      }
    },
    
    detectSystemInfo() {
      // Detectar información básica del sistema desde el navegador
      this.systemInfo.arch = navigator.platform || 'Desconocido'
      
      if (navigator.userAgent.includes('Windows')) {
        this.systemInfo.os = 'Windows'
      } else if (navigator.userAgent.includes('Mac')) {
        this.systemInfo.os = 'macOS'
      } else if (navigator.userAgent.includes('Linux')) {
        this.systemInfo.os = 'Linux'
      } else {
        this.systemInfo.os = 'Desconocido'
      }
    },
    
    addLog(message, type = 'info') {
      this.activityLog.push({
        timestamp: new Date(),
        message,
        type
      })
      
      // Mantener solo los últimos 20 logs
      if (this.activityLog.length > 20) {
        this.activityLog = this.activityLog.slice(-20)
      }
    },
    
    formatTime(timestamp) {
      return timestamp.toLocaleTimeString('es-ES', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
    },
    
    showSuccess(message) {
      // En una aplicación real, usarías un sistema de notificaciones
      alert(`✅ ${message}`)
    },
    
    showError(message) {
      alert(`❌ ${message}`)
    }
  }
}
</script>

<style scoped>
/* Estilos para scrollbar personalizado */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #6B7280;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #9CA3AF;
}

/* Animaciones para estados de carga */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
        console.error('Error loading config:', error)
        this.addLog('Error de conexión al cargar configuración', 'error')
      } finally {
        this.loading = false
      }
    },
    
    async scanForBlender() {
      this.scanning = true
      this.addLog('Iniciando escaneo automático...')
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/blender/scan', {
          method: 'POST'
        })
        
        if (response.ok) {
          const data = await response.json()
          this.installations = data.installations
          this.systemInfo.os = data.system
          
          this.addLog(`Escaneo completado: ${data.working_count}/${data.count} instalaciones válidas`)
          
          // Auto-seleccionar la primera instalación válida
          const workingInstallations = data.installations.filter(i => i.working)
          if (workingInstallations.length > 0) {
            this.formData.customPath = workingInstallations[0].path
            this.addLog(`Auto-seleccionada: Blender ${workingInstallations[0].version}`)
          }
        } else {
          this.addLog('Error en el escaneo automático', 'error')
        }
      } catch (error) {
        console.error('Error scanning:', error)
        this.addLog('Error de conexión durante el escaneo', 'error')
      } finally {
        this.scanning = false
      }
    },
    
    async verifyPath() {
      if (!this.formData.customPath) return
      
      this.verifying = true
      this.addLog(`Verificando: ${this.formData.customPath}`)
      
      try {
        const formData = new FormData()
        formData.append('path', this.formData.customPath)
        
        const response = await fetch('http://localhost:8000/api/v1/config/blender/verify', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          const data = await response.json()
          const verification = data.verification
          
          if (verification.valid) {
            this.addLog(`✅ Verificación exitosa: Blender ${verification.version}`)
          } else {
            this.addLog(`❌ Verificación fallida: ${verification.error}`, 'error')
          }
        } else {
          this.addLog('Error en la verificación', 'error')
        }
      } catch (error) {