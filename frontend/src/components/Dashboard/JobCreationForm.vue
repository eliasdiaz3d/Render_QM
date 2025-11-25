<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gray-800 rounded-lg p-6">
      <h2 class="text-2xl font-bold text-white mb-2">➕ Crear Nuevo Trabajo</h2>
      <p class="text-gray-400">Sube un archivo .blend y configura tu trabajo de render</p>
    </div>

    <!-- Formulario de creación -->
    <div class="bg-gray-800 rounded-lg p-6">
      <form @submit.prevent="createJob" class="space-y-6">
        <!-- Información básica -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Nombre del Trabajo
            </label>
            <input
              v-model="jobForm.name"
              type="text"
              placeholder="Mi proyecto de render"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Motor de Render
            </label>
            <select
              v-model="jobForm.render_engine"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="CYCLES">Cycles</option>
              <option value="EEVEE">Eevee</option>
              <option value="WORKBENCH">Workbench</option>
            </select>
          </div>
        </div>

        <!-- Configuración de frames -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Frame Inicial
            </label>
            <input
              v-model.number="jobForm.frame_start"
              type="number"
              min="1"
              max="9999"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Frame Final
            </label>
            <input
              v-model.number="jobForm.frame_end"
              type="number"
              min="1"
              max="9999"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Total de Frames
            </label>
            <div class="w-full px-3 py-2 bg-gray-600 border border-gray-600 rounded-md text-gray-300">
              {{ totalFrames }} frame{{ totalFrames !== 1 ? 's' : '' }}
            </div>
          </div>
        </div>

        <!-- ====================================================== -->
        <!-- === 1. AÑADIDO: Campo de Email para Notificaciones === -->
        <!-- ====================================================== -->
        <div>
          <label for="notification-email" class="block text-sm font-medium text-gray-300 mb-2">
            ✉️ Email para Notificación (Opcional)
          </label>
          <input
            type="email"
            id="notification-email"
            v-model="jobForm.notification_email"
            placeholder="tu_correo@ejemplo.com"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- Información de tiempo estimado -->
        <div v-if="blendInfo" class="bg-green-900/30 border border-green-500/30 rounded-lg p-4">
          <div class="flex items-start space-x-3">
            <span class="text-green-400 text-xl">🎯</span>
            <div>
              <h4 class="text-green-300 font-medium">Configuración Detectada Automáticamente</h4>
              <div class="text-sm text-green-200 mt-1 space-y-1">
                <p>• <strong>{{ totalFrames }} frames</strong> detectados en el archivo ({{ jobForm.frame_start }}-{{ jobForm.frame_end }})</p>
                <p>• <strong>Motor de render:</strong> {{ blendInfo.render_engine }}</p>
                <p>• <strong>Resolución:</strong> {{ blendInfo.resolution_x }}x{{ blendInfo.resolution_y }}</p>
                <p>• <strong>Formato de salida:</strong> {{ blendInfo.output_format || blendInfo.file_format }}</p>
                <p v-if="blendInfo.output_path">• <strong>Directorio de salida:</strong> Configurado en el archivo .blend</p>
                <p v-else>• <strong>Directorio de salida:</strong> Se usará el directorio por defecto del sistema</p>
                <p>• <strong>Tiempo estimado:</strong> {{ estimatedRenderTime }}</p>
                <p v-if="blendInfo.samples && blendInfo.render_engine === 'CYCLES'">• <strong>Samples:</strong> {{ blendInfo.samples }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="!selectedFile" class="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
          <div class="flex items-start space-x-3">
            <span class="text-blue-400 text-xl">ℹ️</span>
            <div>
              <h4 class="text-blue-300 font-medium">Información de Render</h4>
              <div class="text-sm text-blue-200 mt-1 space-y-1">
                <p>• Se renderizarán <strong>{{ totalFrames }} frames</strong> ({{ jobForm.frame_start }}-{{ jobForm.frame_end }})</p>
                <p v-if="totalFrames > 1">• Tiempo estimado: <strong>{{ estimatedTime }}</strong></p>
                <p v-if="totalFrames > 50">• ⚠️ Render largo detectado - asegúrate de que es correcto</p>
                <p>• Motor: <strong>{{ jobForm.render_engine }}</strong></p>
              </div>
            </div>
          </div>
        </div>

        <!-- Presets rápidos para animaciones -->
        <div v-if="!blendInfo">
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Presets Rápidos (Solo si no hay archivo .blend cargado)
          </label>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
            <button
              type="button"
              @click="setFrameRange(1, 1)"
              class="px-3 py-2 bg-gray-600 text-white rounded hover:bg-gray-500 transition-colors text-sm"
            >
              Frame único
            </button>
            <button
              type="button"
              @click="setFrameRange(1, 50)"
              class="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-500 transition-colors text-sm"
            >
              Prueba (1-50)
            </button>
            <button
              type="button"
              @click="setFrameRange(1, 120)"
              class="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-500 transition-colors text-sm"
            >
              Animación corta (1-120)
            </button>
            <button
              type="button"
              @click="setFrameRange(1, 250)"
              class="px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-500 transition-colors text-sm"
            >
              Animación larga (1-250)
            </button>
          </div>
        </div>

        <div v-else class="bg-yellow-900/30 border border-yellow-500/30 rounded-lg p-3">
          <p class="text-yellow-200 text-sm">
            🎯 Los frames se han configurado automáticamente según tu archivo .blend. 
            Puedes modificarlos manualmente si necesitas renderizar un rango específico.
          </p>
        </div>

        <!-- Upload de archivo con análisis automático -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Archivo .blend
          </label>
          <div class="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-gray-500 transition-colors">
            <input
              ref="fileInput"
              type="file"
              accept=".blend"
              @change="handleFileSelect"
              class="hidden"
            />
            
            <div v-if="!selectedFile" @click="$refs.fileInput.click()" class="cursor-pointer">
              <div class="text-4xl text-gray-400 mb-2">📁</div>
              <p class="text-gray-300 mb-1">Haz clic para seleccionar archivo .blend</p>
              <p class="text-sm text-gray-400">Se detectarán automáticamente los frames de la animación</p>
            </div>
            
            <div v-else-if="isAnalyzing" class="space-y-2">
              <div class="text-4xl text-blue-400 mb-2">🔍</div>
              <div class="flex items-center justify-center space-x-2">
                <svg class="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-blue-300">Analizando archivo .blend...</span>
              </div>
              <p class="text-sm text-gray-400">Extrayendo información de frames y configuración</p>
            </div>
            
            <div v-else class="space-y-3">
              <div class="text-4xl text-green-400 mb-2">✅</div>
              <p class="text-white font-medium">{{ selectedFile.name }}</p>
              <p class="text-sm text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
              
              <!-- Información del archivo .blend -->
              <div v-if="blendInfo" class="mt-4 p-4 bg-blue-900/30 border border-blue-500/30 rounded-lg">
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-blue-300 font-medium">Frames:</span>
                    <span class="text-white ml-2">{{ blendInfo.frame_start }}-{{ blendInfo.frame_end }}</span>
                  </div>
                  <div>
                    <span class="text-blue-300 font-medium">Total:</span>
                    <span class="text-white ml-2">{{ blendInfo.total_frames }} frames</span>
                  </div>
                  <div>
                    <span class="text-blue-300 font-medium">Motor:</span>
                    <span class="text-white ml-2">{{ blendInfo.render_engine }}</span>
                  </div>
                  <div>
                    <span class="text-blue-300 font-medium">Resolución:</span>
                    <span class="text-white ml-2">{{ blendInfo.resolution_x }}x{{ blendInfo.resolution_y }}</span>
                  </div>
                  <div>
                    <span class="text-blue-300 font-medium">Formato:</span>
                    <span class="text-white ml-2">{{ blendInfo.output_format || blendInfo.file_format }}</span>
                  </div>
                  <div v-if="blendInfo.samples && blendInfo.render_engine === 'CYCLES'">
                    <span class="text-blue-300 font-medium">Samples:</span>
                    <span class="text-white ml-2">{{ blendInfo.samples }}</span>
                  </div>
                </div>
                
                <!-- Información de output path -->
                <div v-if="blendInfo.output_path" class="mt-3 pt-3 border-t border-blue-500/20">
                  <div class="flex items-start space-x-2">
                    <span class="text-blue-300 font-medium text-sm">📁 Output:</span>
                    <div class="flex-1">
                      <span class="text-white text-sm font-mono break-all">{{ blendInfo.output_path }}</span>
                      <p class="text-blue-200 text-xs mt-1">Los frames se guardarán según la configuración del archivo .blend</p>
                    </div>
                  </div>
                </div>
                
                <div class="mt-2 pt-2 border-t border-blue-500/20">
                  <span class="text-blue-300 font-medium">Tiempo estimado:</span>
                  <span class="text-white ml-2">{{ estimatedRenderTime }}</span>
                </div>
              </div>
              
              <button
                type="button"
                @click="clearFile"
                class="mt-2 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Cambiar archivo
              </button>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="flex space-x-4">
          <button
            type="submit"
            :disabled="!selectedFile || isUploading"
            class="flex-1 py-3 px-6 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isUploading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Subiendo...
            </span>
            <span v-else>🚀 Crear y Renderizar</span>
          </button>
          
          <button
            type="button"
            @click="resetForm"
            class="px-6 py-3 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
          >
            🔄 Limpiar
          </button>
        </div>

        <!-- Progress bar durante upload -->
        <div v-if="uploadProgress > 0" class="w-full bg-gray-700 rounded-full h-2">
          <div 
            class="bg-blue-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: uploadProgress + '%' }"
          ></div>
          <p class="text-sm text-gray-400 mt-1">{{ uploadProgress }}% completado</p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JobCreationForm',
  emits: ['job-created', 'view-job'],
  data() {
    return {
      jobForm: {
        name: '',
        render_engine: 'CYCLES',
        frame_start: 1,
        frame_end: 50,
        // --- CAMBIO 2: Variable para el email en el formulario ---
        notification_email: '' 
      },
      selectedFile: null,
      isUploading: false,
      isAnalyzing: false,
      uploadProgress: 0,
      blendInfo: null,
      estimatedRenderTime: ''
    }
  },
  computed: {
    totalFrames() {
      if (this.jobForm.frame_end < this.jobForm.frame_start) {
        return 0;
      }
      return (this.jobForm.frame_end - this.jobForm.frame_start) + 1;
    },
    estimatedTime() {
      const frames = this.totalFrames;
      if (frames <= 1) return '~1-2 minutos';
      if (frames <= 10) return '~5-10 minutos';
      if (frames <= 50) return '~15-30 minutos';
      if (frames <= 120) return '~45-90 minutos';
      return '~2+ horas';
    }
  },
  methods: {
    async handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.blend')) {
        this.selectedFile = file;
        
        // Auto-completar nombre si está vacío
        if (!this.jobForm.name) {
          this.jobForm.name = file.name.replace('.blend', '');
        }
        
        // Analizar archivo .blend automáticamente
        await this.analyzeBlendFile(file);
        
      } else {
        alert('Por favor selecciona un archivo .blend válido');
        this.clearFile();
      }
    },
    
    async analyzeBlendFile(file) {
      this.isAnalyzing = true;
      this.blendInfo = null;
      this.estimatedRenderTime = '';
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('http://localhost:8000/api/v1/blend/analyze', {
          method: 'POST',
          body: formData
        });
        
        if (response.ok) {
          const result = await response.json();
          this.blendInfo = result.blend_info;
          this.estimatedRenderTime = result.recommended_settings.estimated_time;
          
          // Aplicar configuración recomendada automáticamente
          this.jobForm.frame_start = result.recommended_settings.frame_start;
          this.jobForm.frame_end = result.recommended_settings.frame_end;
          this.jobForm.render_engine = result.recommended_settings.render_engine;
          
          console.log('✅ Archivo analizado:', result);
          
        } else {
          const error = await response.json();
          console.error('Error analizando archivo:', error);
          alert(`No se pudo analizar el archivo: ${error.detail}`);
        }
        
      } catch (error) {
        console.error('Error analizando archivo:', error);
        alert('Error de conexión al analizar el archivo');
      } finally {
        this.isAnalyzing = false;
      }
    },
    
    clearFile() {
      this.selectedFile = null;
      this.blendInfo = null;
      this.estimatedRenderTime = '';
      this.isAnalyzing = false;
      this.$refs.fileInput.value = '';
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    setFrameRange(start, end) {
      this.jobForm.frame_start = start;
      this.jobForm.frame_end = end;
    },
    
    resetForm() {
      this.jobForm = {
        name: '',
        render_engine: 'CYCLES',
        frame_start: 1,
        frame_end: 50,
        // --- AÑADIDO: Limpiar el email al resetear ---
        notification_email: ''
      };
      this.clearFile();
      this.uploadProgress = 0;
    },
    
    async createJob() {
      if (!this.selectedFile) {
        alert('Por favor selecciona un archivo .blend');
        return;
      }
      
      if (!this.jobForm.name.trim()) {
        alert('Por favor ingresa un nombre para el trabajo');
        return;
      }
      
      if (this.jobForm.frame_end < this.jobForm.frame_start) {
        alert('El frame final debe ser mayor o igual al frame inicial');
        return;
      }
      
      if (this.totalFrames > 500) {
        if (!confirm(`¿Estás seguro de renderizar ${this.totalFrames} frames? Esto puede tomar mucho tiempo.`)) {
          return;
        }
      }
      
      this.isUploading = true;
      this.uploadProgress = 0;
      
      try {
        // Simular progreso de upload
        const progressInterval = setInterval(() => {
          if (this.uploadProgress < 90) {
            this.uploadProgress += Math.random() * 15;
          }
        }, 200);
        
        // Crear FormData para envío
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('name', this.jobForm.name);
        formData.append('frame_start', this.jobForm.frame_start);
        formData.append('frame_end', this.jobForm.frame_end);
        formData.append('render_engine', this.jobForm.render_engine);
        
        // --- CAMBIO 3: Lógica para añadir el email al envío ---
        if (this.jobForm.notification_email) {
          formData.append('notification_email', this.jobForm.notification_email);
        }

        // Enviar al backend
        const response = await fetch('http://localhost:8000/api/v1/jobs/upload', {
          method: 'POST',
          body: formData
        });
        
        clearInterval(progressInterval);
        this.uploadProgress = 100;
        
        if (response.ok) {
          const result = await response.json();
          
          // Emitir evento de trabajo creado
          this.$emit('job-created', result.job);
          
          // Mostrar mensaje de éxito
          alert(`¡Trabajo "${this.jobForm.name}" creado exitosamente! 🎉`);
          
          // Resetear formulario
          this.resetForm();
          
          // Opcional: cambiar a vista de trabajos
          setTimeout(() => {
            this.$emit('view-job', result.job_id);
          }, 1000);
          
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Error al crear trabajo');
        }
        
      } catch (error) {
        console.error('Error creating job:', error);
        alert(`Error al crear trabajo: ${error.message}`);
        this.uploadProgress = 0;
      } finally {
        this.isUploading = false;
      }
    }
  }
}
</script>

<style scoped>
/* Animaciones para el componente */
.transition-all {
  transition: all 0.3s ease;
}

/* Hover effects */
.hover\:bg-blue-700:hover {
  background-color: #1d4ed8;
}

.hover\:bg-gray-700:hover {
  background-color: #374151;
}

.hover\:border-gray-500:hover {
  border-color: #6b7280;
}
</style>
