<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-2xl font-bold text-white mb-2">⚙️ Configuración del Sistema</h2>
      <p class="text-gray-400">Gestiona la configuración de Blender y otros parámetros del sistema</p>
    </div>

    <!-- Configuración de Blender -->
    <div class="bg-gray-800 rounded-lg p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-semibold text-white">🎨 Configuración de Blender</h3>
        <div class="flex items-center space-x-2">
          <span 
            class="px-3 py-1 rounded-full text-sm font-medium"
            :class="blenderStatus.available ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
          >
            {{ blenderStatus.available ? '✅ Configurado' : '❌ No configurado' }}
          </span>
        </div>
      </div>

      <!-- Formulario de configuración -->
      <form @submit.prevent="saveBlenderConfig" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Ruta del ejecutable de Blender
          </label>
          <div class="flex space-x-2">
            <input
              v-model="blenderConfig.blender_path"
              type="text"
              placeholder="Ej: C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
              class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="isLoading"
            />
            <button
              type="button"
              @click="browseBlenderPath"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500 transition-colors"
              :disabled="isLoading"
            >
              📁 Explorar
            </button>
          </div>
          <p class="text-xs text-gray-400 mt-1">
            Especifica la ruta completa al ejecutable de Blender
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Tiempo de espera (segundos)
            </label>
            <input
              v-model.number="blenderConfig.timeout"
              type="number"
              min="30"
              max="3600"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="isLoading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Memoria máxima (MB)
            </label>
            <input
              v-model.number="blenderConfig.max_memory_mb"
              type="number"
              min="512"
              max="32768"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="isLoading"
            />
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <label class="flex items-center space-x-2">
            <input
              v-model="blenderConfig.auto_detect"
              type="checkbox"
              class="form-checkbox h-4 w-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
              :disabled="isLoading"
            />
            <span class="text-sm text-gray-300">Auto-detectar Blender en rutas comunes</span>
          </label>
        </div>

        <!-- Botones de acción -->
        <div class="flex space-x-3 pt-4">
          <button
            type="submit"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
            :disabled="isLoading || !blenderConfig.blender_path"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Guardando...
            </span>
            <span v-else>💾 Guardar Configuración</span>
          </button>

          <button
            type="button"
            @click="testBlenderConfig"
            class="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            :disabled="isLoading || !blenderConfig.blender_path"
          >
            <span v-if="isTesting" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Probando...
            </span>
            <span v-else>🧪 Probar Configuración</span>
          </button>

          <button
            type="button"
            @click="autoDetectBlender"
            class="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50"
            :disabled="isLoading"
          >
            🔍 Auto-detectar
          </button>
        </div>
      </form>

      <!-- Información de estado -->
      <div v-if="blenderStatus.version || blenderStatus.error" class="mt-6 p-4 rounded-lg"
           :class="blenderStatus.available ? 'bg-green-900/30 border border-green-500/30' : 'bg-red-900/30 border border-red-500/30'">
        <div v-if="blenderStatus.available" class="text-green-300">
          <h4 class="font-medium">✅ Blender configurado correctamente</h4>
          <p class="text-sm mt-1">Versión: {{ blenderStatus.version }}</p>
          <p class="text-sm break-all">Ruta: {{ blenderStatus.path || blenderConfig.blender_path }}</p>
        </div>
        <div v-else class="text-red-300">
          <h4 class="font-medium">❌ Error en la configuración</h4>
          <p class="text-sm mt-1">{{ blenderStatus.error }}</p>
        </div>
      </div>

      <!-- Detección múltiple de versiones -->
      <div v-if="detectedVersions.length > 0" class="mt-6">
        <h4 class="text-lg font-medium text-white mb-3">🔍 Versiones de Blender Detectadas</h4>
        <div class="space-y-2">
          <div 
            v-for="(version, index) in detectedVersions" 
            :key="index"
            class="flex items-center justify-between p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors"
          >
            <div class="flex-1">
              <div class="text-white font-medium">{{ version.version || 'Versión desconocida' }}</div>
              <div class="text-sm text-gray-400 break-all">{{ version.path }}</div>
            </div>
            <button
              @click="selectBlenderVersion(version)"
              class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              :disabled="isLoading"
            >
              Seleccionar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuración de la Cola de Render -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h3 class="text-xl font-semibold text-white mb-4">🔄 Configuración de la Cola</h3>
      
      <form @submit.prevent="saveQueueConfig" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Trabajos concurrentes máximos
            </label>
            <input
              v-model.number="queueConfig.max_concurrent_jobs"
              type="number"
              min="1"
              max="16"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Reintentos automáticos
            </label>
            <input
              v-model.number="queueConfig.max_retries"
              type="number"
              min="0"
              max="5"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Prioridad por defecto
            </label>
            <select
              v-model="queueConfig.default_priority"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="low">Baja</option>
              <option value="normal">Normal</option>
              <option value="high">Alta</option>
              <option value="urgent">Urgente</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Limpieza automática (días)
            </label>
            <input
              v-model.number="queueConfig.auto_cleanup_days"
              type="number"
              min="1"
              max="365"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div class="pt-4">
          <button
            type="submit"
            class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            :disabled="isLoading"
          >
            💾 Guardar Configuración de Cola
          </button>
        </div>
      </form>
    </div>

    <!-- Información del Sistema -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h3 class="text-xl font-semibold text-white mb-4">📋 Información del Sistema</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-400">Sistema Operativo:</span>
            <span class="text-white">{{ systemInfo.os || 'Cargando...' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Arquitectura:</span>
            <span class="text-white">{{ systemInfo.arch || 'Cargando...' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Memoria Total:</span>
            <span class="text-white">{{ systemInfo.total_memory || 'Cargando...' }}</span>
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-400">Núcleos CPU:</span>
            <span class="text-white">{{ systemInfo.cpu_cores || 'Cargando...' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Versión Python:</span>
            <span class="text-white">{{ systemInfo.python_version || 'Cargando...' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">Espacio en Disco:</span>
            <span class="text-white">{{ systemInfo.disk_space || 'Cargando...' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemSettings',
  emits: ['blender-config-updated'],
  data() {
    return {
      isLoading: false,
      isTesting: false,
      
      blenderConfig: {
        blender_path: '',
        timeout: 300,
        max_memory_mb: 4096,
        auto_detect: true
      },
      
      queueConfig: {
        max_concurrent_jobs: 2,
        max_retries: 3,
        default_priority: 'normal',
        auto_cleanup_days: 30
      },
      
      blenderStatus: {
        available: false,
        version: null,
        path: null,
        error: null
      },
      
      detectedVersions: [],
      
      systemInfo: {
        os: null,
        arch: null,
        total_memory: null,
        cpu_cores: null,
        python_version: null,
        disk_space: null
      }
    }
  },
  
  async mounted() {
    await this.loadCurrentConfig();
    await this.loadSystemInfo();
  },
  
  methods: {
    async loadCurrentConfig() {
      try {
        // Cargar configuración actual de Blender
        const blenderResponse = await fetch('http://localhost:8000/api/v1/config/blender');
        if (blenderResponse.ok) {
          const blenderData = await blenderResponse.json();
          this.blenderConfig = { ...this.blenderConfig, ...blenderData };
          this.blenderStatus = {
            available: blenderData.verification?.valid || false,
            version: blenderData.verification?.version,
            path: blenderData.blender_path,
            error: blenderData.verification?.error
          };
        }
        
        // Cargar configuración de la cola
        const queueResponse = await fetch('http://localhost:8000/api/v1/config/queue');
        if (queueResponse.ok) {
          const queueData = await queueResponse.json();
          this.queueConfig = { ...this.queueConfig, ...queueData };
        }
      } catch (error) {
        console.error('Error loading current config:', error);
      }
    },
    
    async loadSystemInfo() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/system/info');
        if (response.ok) {
          this.systemInfo = await response.json();
        }
      } catch (error) {
        console.error('Error loading system info:', error);
      }
    },
    
    async saveBlenderConfig() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/blender', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.blenderConfig)
        });
        
        if (response.ok) {
          const result = await response.json();
          this.blenderStatus = {
            available: result.verification?.valid || false,
            version: result.verification?.version,
            path: result.blender_path,
            error: result.verification?.error
          };
          
          // Emitir evento para actualizar el dashboard
          this.$emit('blender-config-updated', result);
          
          console.log('Configuración de Blender guardada correctamente');
        } else {
          const error = await response.json();
          console.error('Error saving Blender config:', error);
          this.blenderStatus.error = error.detail || 'Error al guardar configuración';
        }
      } catch (error) {
        console.error('Error saving Blender config:', error);
        this.blenderStatus.error = 'Error de conexión con el servidor';
      } finally {
        this.isLoading = false;
      }
    },
    
    async testBlenderConfig() {
      this.isTesting = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/blender/test', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ blender_path: this.blenderConfig.blender_path })
        });
        
        const result = await response.json();
        
        if (response.ok) {
          this.blenderStatus = {
            available: result.verification?.valid || false,
            version: result.verification?.version,
            path: this.blenderConfig.blender_path,
            error: result.verification?.error
          };
        } else {
          this.blenderStatus.error = result.detail || 'Error al probar configuración';
        }
      } catch (error) {
        console.error('Error testing Blender config:', error);
        this.blenderStatus.error = 'Error de conexión con el servidor';
      } finally {
        this.isTesting = false;
      }
    },
    
    async autoDetectBlender() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/blender/auto-detect', {
          method: 'POST'
        });
        
        if (response.ok) {
          const result = await response.json();
          
          // Si hay múltiples versiones detectadas
          if (result.detected_versions && Array.isArray(result.detected_versions)) {
            this.detectedVersions = result.detected_versions;
            
            // Si solo hay una versión, seleccionarla automáticamente
            if (result.detected_versions.length === 1) {
              this.selectBlenderVersion(result.detected_versions[0]);
            } else if (result.detected_versions.length > 1) {
              console.log(`Se detectaron ${result.detected_versions.length} versiones de Blender`);
            }
          }
          
          // Si se devuelve una ruta única (compatibilidad con versión anterior)
          if (result.blender_path) {
            this.blenderConfig.blender_path = result.blender_path;
            this.blenderStatus = {
              available: result.verification?.valid || false,
              version: result.verification?.version,
              path: result.blender_path,
              error: result.verification?.error
            };
            console.log('Blender detectado automáticamente');
          } else if (!result.detected_versions || result.detected_versions.length === 0) {
            this.blenderStatus.error = 'No se pudo detectar Blender automáticamente';
          }
        }
      } catch (error) {
        console.error('Error auto-detecting Blender:', error);
        this.blenderStatus.error = 'Error al detectar Blender automáticamente';
      } finally {
        this.isLoading = false;
      }
    },
    
    selectBlenderVersion(version) {
      this.blenderConfig.blender_path = version.path;
      this.blenderStatus = {
        available: version.valid || false,
        version: version.version,
        path: version.path,
        error: version.error
      };
      
      // Auto-guardar la configuración seleccionada
      this.saveBlenderConfig();
    },
    
    browseBlenderPath() {
      // En una aplicación real, esto abriría un diálogo de archivo
      // Por ahora, mostrar rutas comunes como sugerencia
      const commonPaths = [
        'C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe',
        'C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe',
        '/usr/bin/blender',
        '/Applications/Blender.app/Contents/MacOS/Blender'
      ];
      
      const suggestion = commonPaths.find(path => 
        navigator.platform.toLowerCase().includes('win') 
          ? path.includes('C:') 
          : path.includes('/usr') || path.includes('/Applications')
      );
      
      if (suggestion && confirm(`¿Quieres usar esta ruta sugerida?\n${suggestion}`)) {
        this.blenderConfig.blender_path = suggestion;
      }
    },
    
    async saveQueueConfig() {
      this.isLoading = true;
      try {
        const response = await fetch('http://localhost:8000/api/v1/config/queue', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.queueConfig)
        });
        
        if (response.ok) {
          console.log('Configuración de cola guardada correctamente');
        } else {
          const error = await response.json();
          console.error('Error saving queue config:', error);
        }
      } catch (error) {
        console.error('Error saving queue config:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.form-checkbox {
  @apply rounded border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-0;
  background-color: #374151;
}
</style>