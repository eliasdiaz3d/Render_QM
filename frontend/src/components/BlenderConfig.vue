<template>
  <div class="space-y-6">
    <div class="bg-gray-800 rounded-lg p-6">
      <h3 class="text-xl font-semibold text-white mb-4">🎨 Configuración de Blender</h3>

      <div class="mb-6 p-4 bg-gray-700 rounded-lg">
        <h4 class="text-lg font-medium text-white mb-3">Estado Actual</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-400 mb-1">Ruta Configurada</label>
            <div class="text-white font-mono text-sm break-all">
              {{ currentBlenderPath || 'No configurado' }}
            </div>
          </div>
          <div>
            <label class="block text-sm text-gray-400 mb-1">Versión</label>
            <div class="text-white">
              {{ currentBlenderVersion || 'No detectada' }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="statusMessage" 
           :class="{'bg-green-500 text-white': statusMessage.type === 'success', 
                    'bg-red-500 text-white': statusMessage.type === 'error',
                    'bg-yellow-500 text-gray-900': statusMessage.type === 'warning'}"
           class="p-3 rounded-lg text-sm mb-4 transition-all duration-300">
        {{ statusMessage.text }}
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <button
          @click="autoDetectBlender"
          :disabled="isLoading"
          class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors flex items-center justify-center"
        >
          <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span v-else>Auto-detectar Blender</span>
        </button>
        
        <button
          @click="showManualPathModal = true"
          :disabled="isLoading"
          class="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
        >
          Ruta Manual
        </button>
        
        <button
          @click="clearConfig"
          :disabled="isLoading"
          class="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white font-bold py-2 px-4 rounded transition-colors"
        >
          Limpiar Config.
        </button>
      </div>

      <div v-if="detectedInstallations.length > 0" class="mt-6 p-4 bg-gray-700 rounded-lg">
        <h4 class="text-lg font-medium text-white mb-3">Instalaciones Detectadas:</h4>
        <div class="space-y-3">
          <div
            v-for="(installation, index) in detectedInstallations"
            :key="installation.path || index"
            class="p-3 border rounded-lg flex items-center justify-between"
            :class="{
              'bg-green-900 border-green-600': installation.working,
              'bg-gray-900 border-gray-600': !installation.working
            }"
          >
            <div class="flex-grow">
              <p class="text-sm font-mono text-white break-all">{{ installation.path }}</p>
              <p :class="{'text-green-400': installation.working, 'text-gray-400': !installation.working}" class="text-sm font-semibold">
                Versión: {{ installation.version }} ({{ installation.working ? 'Operativa' : 'FALLA' }})
              </p>
            </div>
            
            <button
              @click="selectInstallation(installation)"
              :disabled="currentBlenderPath === installation.path"
              class="ml-4 py-1 px-3 text-sm rounded transition-colors"
              :class="{
                'bg-gray-600 text-white hover:bg-gray-500 disabled:bg-gray-700': currentBlenderPath !== installation.path,
                'bg-green-600 text-white disabled:bg-green-700': currentBlenderPath === installation.path
              }"
            >
              {{ currentBlenderPath === installation.path ? 'Seleccionada' : 'Seleccionar' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="showManualPathModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div class="bg-gray-800 p-8 rounded-lg w-full max-w-lg">
          <h4 class="text-xl text-white mb-4">Ingresar Ruta Manual</h4>
          <input 
            v-model="manualBlenderPath"
            type="text"
            placeholder="Ej: C:\Program Files\Blender Foundation\Blender 5.0\blender.exe"
            class="w-full p-3 mb-4 bg-gray-700 text-white border border-gray-600 rounded"
          >
          <div class="flex justify-end space-x-4">
            <button @click="showManualPathModal = false" class="bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded">
              Cancelar
            </button>
            <button @click="saveBlenderPath({})" class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded">
              Guardar y Verificar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const API_BASE_URL = 'http://localhost:8000/api/v1' 

export default {
  props: {
    initialPath: {
      type: String,
      default: ''
    },
    initialVersion: {
      type: String,
      default: ''
    }
  },
  
  data () {
    return {
      currentBlenderPath: this.initialPath,
      currentBlenderVersion: this.initialVersion,
      manualBlenderPath: '',
      showManualPathModal: false,
      isLoading: false,
      statusMessage: null,
      // Usamos una lista vacía para inicializar
      detectedInstallations: [] 
    }
  },

  methods: {
    async fetchStatus() {
      try {
        const response = await fetch(`${API_BASE_URL}/config/blender/status`)
        if (response.ok) {
          const data = await response.json()
          if (data.is_configured) {
            this.currentBlenderPath = data.path
            this.currentBlenderVersion = data.version
          }
        }
      } catch (error) {
        console.warn('Could not fetch initial Blender status:', error)
      }
    },

    async autoDetectBlender () {
      this.isLoading = true
      this.detectedInstallations = [] // Limpiar antes de la llamada
      this.statusMessage = null

      try {
        const response = await fetch(`${API_BASE_URL}/config/blender/auto-detect`, {
          method: 'POST'
        })
        
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || `Error HTTP: ${response.status}`)
        }

        const data = await response.json()
        console.log('Respuesta de Detección (Consola JS):', data)

        // Verificación de datos más estricta:
        if (data.success && Array.isArray(data.installations) && data.installations.length > 0) {
          // 🚨 Asignación: usamos Object.assign para asegurar la reactividad en casos de Vue 2/3.
          this.detectedInstallations = Object.assign([], data.installations)

          this.statusMessage = {
            type: 'success',
            text: data.message || `✓ Se detectaron ${data.installations.length} instalación(es) de Blender`
          }
          
          // Auto-seleccionar la primera instalación funcional
          const workingInstallations = data.installations.filter(i => i.working)
          if (workingInstallations.length > 0) {
            this.selectInstallation(workingInstallations[0])
          } else if (data.installations.length > 0) {
            this.selectInstallation(data.installations[0])
          }

        } else {
          this.statusMessage = {
            type: 'warning',
            text: data.message || 'No se encontraron instalaciones de Blender válidas'
          }
        }

      } catch (error) {
        console.error('Error auto-detectando:', error)
        this.statusMessage = {
          type: 'error',
          text: `Error de red o servidor: ${error.message}`
        }
      } finally {
        this.isLoading = false
      }
    },

    selectInstallation (installation) {
      this.currentBlenderPath = installation.path
      this.currentBlenderVersion = installation.version
      
      this.saveBlenderPath({ blender_path: installation.path, version: installation.version })
    },
    
    async saveBlenderPath (configData) {
      this.isLoading = true
      this.statusMessage = null
      
      const pathToSend = configData.blender_path || this.manualBlenderPath
      
      if (!pathToSend) {
        this.statusMessage = {
          type: 'error',
          text: 'Por favor ingresa una ruta válida'
        }
        this.isLoading = false
        return
      }

      try {
        const response = await fetch(`${API_BASE_URL}/config/blender`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ blender_path: pathToSend, auto_detect: false })
        })

        const data = await response.json()

        if (response.ok && data.success) {
          this.currentBlenderPath = pathToSend
          this.currentBlenderVersion = data.version || configData.version || 'Desconocida'
          this.showManualPathModal = false
          this.manualBlenderPath = ''

          this.$emit('config-updated', {
            path: this.currentBlenderPath,
            version: this.currentBlenderVersion
          })

          this.statusMessage = {
            type: 'success',
            text: data.message || '✓ Ruta de Blender guardada'
          }
        } else {
          this.statusMessage = {
            type: 'error',
            text: data.detail || data.message || 'Error al guardar la configuración'
          }
        }
      } catch (error) {
        console.error('Error guardando ruta:', error)
        this.statusMessage = {
          type: 'error',
          text: 'Error de red al guardar la configuración'
        }
      } finally {
        this.isLoading = false
      }
    },
    
    clearConfig() {
      this.currentBlenderPath = ''
      this.currentBlenderVersion = ''
      this.detectedInstallations = []
      this.statusMessage = {
        type: 'warning',
        text: 'Configuración de Blender limpiada'
      }
      this.$emit('config-updated', { path: '', version: '' })
    }
  },

  mounted() {
    this.fetchStatus()
  }
}
</script>