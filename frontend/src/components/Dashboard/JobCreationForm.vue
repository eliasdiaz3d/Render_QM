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

        <!-- Información de tiempo estimado -->
        <div class="bg-blue-900/30 border border-blue-500/30 rounded-lg p-4">
          <div class="flex items-start space-x-3">
            <span class="text-blue-400 text-xl">ℹ️</span>
            <div>
              <h4 class="text-blue-300 font-medium">Información de Render</h4>
              <div class="text-sm text-blue-200 mt-1 space-y-1">
                <p>• Se renderizarán <strong>{{ totalFrames }} frames</strong> ({{ jobForm.frame_start }}-{{ jobForm.frame_end }})</p>
                <p v-if="totalFrames > 1">• Tiempo estimado: <strong>{{ estimatedTime }}</strong></p>
                <p v-if="totalFrames > 50">• ⚠️ Render largo detectado - considera usar un rango menor para pruebas</p>
                <p>• Motor: <strong>{{ jobForm.render_engine }}</strong></p>
              </div>
            </div>
          </div>
        </div>

        <!-- Presets rápidos para animaciones -->
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Presets Rápidos
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

        <!-- Upload de archivo -->
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
              <p class="text-sm text-gray-400">Máximo 500MB</p>
            </div>
            
            <div v-else class="space-y-2">
              <div class="text-4xl text-blue-400 mb-2">📄</div>
              <p class="text-white font-medium">{{ selectedFile.name }}</p>
              <p class="text-sm text-gray-400">{{ formatFileSize(selectedFile.size) }}</p>
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
        frame_end: 50
      },
  computed: {
    totalFrames() {
      return Math.max(1, (this.jobForm.frame_end - this.jobForm.frame_start) + 1);
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
      selectedFile: null,
      isUploading: false,
      uploadProgress: 0
    }
  },
  methods: {
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith('.blend')) {
        this.selectedFile = file;
        
        // Auto-completar nombre si está vacío
        if (!this.jobForm.name) {
          this.jobForm.name = file.name.replace('.blend', '');
        }
      } else {
        alert('Por favor selecciona un archivo .blend válido');
        this.clearFile();
      }
    },
    
    clearFile() {
      this.selectedFile = null;
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
        frame_end: 50
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