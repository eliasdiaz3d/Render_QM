<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gray-800 rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-white mb-2">📋 Lista de Trabajos</h2>
          <p class="text-gray-400">Gestiona y monitorea todos tus trabajos de render</p>
        </div>
        <button
          @click="$emit('create-job')"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          ➕ Nuevo Trabajo
        </button>
      </div>
    </div>

    <!-- Filtros y búsqueda -->
    <div class="bg-gray-800 rounded-lg p-4">
      <div class="flex flex-col md:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar trabajos..."
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <div>
          <select
            v-model="statusFilter"
            class="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Todos los estados</option>
            <option value="pending">Pendiente</option>
            <option value="processing">Procesando</option>
            <option value="completed">Completado</option>
            <option value="failed">Fallido</option>
            <option value="cancelled">Cancelado</option>
          </select>
        </div>
        <button
          @click="refreshJobs"
          class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        >
          🔄 Actualizar
        </button>
      </div>
    </div>

    <!-- Lista de trabajos -->
    <div class="space-y-4">
      <div v-if="isLoading" class="text-center py-8">
        <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-gray-400">Cargando trabajos...</p>
      </div>

      <div v-else-if="filteredJobs.length === 0" class="text-center py-8">
        <div class="text-6xl text-gray-500 mb-4">📭</div>
        <p class="text-gray-400 text-lg">No hay trabajos que coincidan con los filtros</p>
      </div>

      <div v-else>
        <div
          v-for="job in filteredJobs"
          :key="job.id"
          class="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors"
        >
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-4">
              <div class="flex-shrink-0">
                <span class="text-2xl">
                  {{ getStatusIcon(job.status) }}
                </span>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-white">{{ job.name }}</h3>
                <p class="text-sm text-gray-400">{{ job.original_filename || 'archivo.blend' }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span 
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="getStatusClass(job.status)"
              >
                {{ getStatusText(job.status) }}
              </span>
              <div class="flex space-x-1">
                <button
                  v-if="job.status === 'completed'"
                  @click="viewRender(job)"
                  class="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  title="Ver render"
                >
                  👁️
                </button>
                <button
                  v-if="job.status === 'completed'"
                  @click="downloadRender(job)"
                  class="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  title="Descargar render"
                >
                  📥
                </button>
                <button
                  v-if="job.status === 'processing' || job.status === 'pending'"
                  @click="cancelJob(job)"
                  class="p-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                  title="Cancelar trabajo"
                >
                  ⏹️
                </button>
                <button
                  @click="deleteJob(job)"
                  class="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  title="Eliminar trabajo"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>

          <!-- Progress bar para trabajos en progreso -->
          <div v-if="job.status === 'processing'" class="mb-4">
            <div class="flex justify-between text-sm text-gray-400 mb-1">
              <span>Progreso</span>
              <span>{{ job.progress }}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-500"
                :style="{ width: job.progress + '%' }"
              ></div>
            </div>
          </div>

          <!-- Información del trabajo -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="text-gray-400">Creado:</span>
              <p class="text-white">{{ formatDate(job.created_at) }}</p>
            </div>
            <div v-if="job.started_at">
              <span class="text-gray-400">Iniciado:</span>
              <p class="text-white">{{ formatDate(job.started_at) }}</p>
            </div>
            <div v-if="job.completed_at">
              <span class="text-gray-400">Completado:</span>
              <p class="text-white">{{ formatDate(job.completed_at) }}</p>
            </div>
            <div>
              <span class="text-gray-400">Frames:</span>
              <p class="text-white">
                {{ job.frame_start }}-{{ job.frame_end }} 
                <span class="text-gray-400">({{ job.frames_total }} total)</span>
              </p>
            </div>
            <div v-if="job.frames_rendered > 0">
              <span class="text-gray-400">Renderizados:</span>
              <p class="text-white">{{ job.frames_rendered }}/{{ job.frames_total }}</p>
            </div>
            <div>
              <span class="text-gray-400">Motor:</span>
              <p class="text-white">{{ job.render_engine || 'CYCLES' }}</p>
            </div>
            <div v-if="job.render_time">
              <span class="text-gray-400">Tiempo:</span>
              <p class="text-white">{{ job.render_time }}</p>
            </div>
          </div>

          <!-- Error message si falló -->
          <div v-if="job.status === 'failed' && job.error_message" class="mt-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
            <p class="text-red-300 text-sm">
              <strong>Error:</strong> {{ job.error_message }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para mostrar render -->
    <div v-if="showRenderModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="closeRenderModal">
      <div class="max-w-4xl max-h-screen p-4" @click.stop>
        <div class="bg-gray-800 rounded-lg overflow-hidden">
          <div class="flex items-center justify-between p-4 border-b border-gray-700">
            <h3 class="text-xl font-semibold text-white">{{ selectedJob?.name }}</h3>
            <button @click="closeRenderModal" class="text-gray-400 hover:text-white">
              ✕
            </button>
          </div>
          <div class="p-4">
            <img 
              :src="renderImageUrl" 
              :alt="selectedJob?.name"
              class="max-w-full max-h-96 mx-auto rounded-lg"
              @error="onImageError"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'JobsList',
  emits: ['create-job'],
  data() {
    return {
      jobs: [],
      isLoading: false,
      searchQuery: '',
      statusFilter: '',
      showRenderModal: false,
      selectedJob: null,
      renderImageUrl: ''
    }
  },
  computed: {
    filteredJobs() {
      let filtered = this.jobs;
      
      // Filtrar por búsqueda
      if (this.searchQuery) {
        filtered = filtered.filter(job => 
          job.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (job.original_filename && job.original_filename.toLowerCase().includes(this.searchQuery.toLowerCase()))
        );
      }
      
      // Filtrar por estado
      if (this.statusFilter) {
        filtered = filtered.filter(job => job.status === this.statusFilter);
      }
      
      return filtered;
    }
  },
  async mounted() {
    await this.loadJobs();
    
    // Auto-refresh cada 5 segundos
    this.refreshInterval = setInterval(() => {
      this.loadJobs();
    }, 5000);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async loadJobs() {
      if (this.isLoading) return;
      
      try {
        const response = await fetch('http://localhost:8000/api/v1/jobs');
        if (response.ok) {
          this.jobs = await response.json();
        }
      } catch (error) {
        console.error('Error loading jobs:', error);
      }
    },
    
    async refreshJobs() {
      this.isLoading = true;
      await this.loadJobs();
      this.isLoading = false;
    },
    
    getStatusIcon(status) {
      const icons = {
        pending: '⏳',
        processing: '⚙️',
        completed: '✅',
        failed: '❌',
        cancelled: '⏹️'
      };
      return icons[status] || '❓';
    },
    
    getStatusClass(status) {
      const classes = {
        pending: 'bg-yellow-100 text-yellow-800',
        processing: 'bg-blue-100 text-blue-800',
        completed: 'bg-green-100 text-green-800',
        failed: 'bg-red-100 text-red-800',
        cancelled: 'bg-gray-100 text-gray-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    },
    
    getStatusText(status) {
      const texts = {
        pending: 'Pendiente',
        processing: 'Procesando',
        completed: 'Completado',
        failed: 'Fallido',
        cancelled: 'Cancelado'
      };
      return texts[status] || status;
    },
    
    formatDate(dateString) {
      if (!dateString) return '-';
      const date = new Date(dateString);
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    async viewRender(job) {
      this.selectedJob = job;
      this.renderImageUrl = `http://localhost:8000/api/v1/jobs/${job.id}/download`;
      this.showRenderModal = true;
    },
    
    async downloadRender(job) {
      try {
        const link = document.createElement('a');
        link.href = `http://localhost:8000/api/v1/jobs/${job.id}/download`;
        link.download = `render_${job.name}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (error) {
        console.error('Error downloading render:', error);
        alert('Error al descargar el render');
      }
    },
    
    async cancelJob(job) {
      if (!confirm(`¿Estás seguro de que quieres cancelar "${job.name}"?`)) {
        return;
      }
      
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${job.id}/cancel`, {
          method: 'POST'
        });
        
        if (response.ok) {
          await this.loadJobs();
          alert('Trabajo cancelado exitosamente');
        }
      } catch (error) {
        console.error('Error canceling job:', error);
        alert('Error al cancelar el trabajo');
      }
    },
    
    async deleteJob(job) {
      if (!confirm(`¿Estás seguro de que quieres eliminar "${job.name}"? Esta acción no se puede deshacer.`)) {
        return;
      }
      
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${job.id}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          await this.loadJobs();
          alert('Trabajo eliminado exitosamente');
        }
      } catch (error) {
        console.error('Error deleting job:', error);
        alert('Error al eliminar el trabajo');
      }
    },
    
    closeRenderModal() {
      this.showRenderModal = false;
      this.selectedJob = null;
      this.renderImageUrl = '';
    },
    
    onImageError() {
      alert('Error al cargar la imagen del render');
      this.closeRenderModal();
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}

/* Animación para el spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>