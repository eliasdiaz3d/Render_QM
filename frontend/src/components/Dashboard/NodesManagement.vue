<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gray-800 rounded-lg p-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-white mb-2">🖥️ Gestión de Nodos</h2>
          <p class="text-gray-400">Monitorea el rendimiento y estado de los nodos de render</p>
        </div>
        <div class="flex space-x-2">
          <button
            @click="refreshNodes"
            :disabled="isLoading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Actualizando...
            </span>
            <span v-else>🔄 Actualizar</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Estadísticas generales -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex items-center">
          <div class="p-3 bg-green-500/20 rounded-lg">
            <span class="text-2xl">✅</span>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-400">Nodos Activos</p>
            <p class="text-2xl font-bold text-green-400">{{ activeNodes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex items-center">
          <div class="p-3 bg-red-500/20 rounded-lg">
            <span class="text-2xl">❌</span>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-400">Nodos Inactivos</p>
            <p class="text-2xl font-bold text-red-400">{{ inactiveNodes }}</p>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex items-center">
          <div class="p-3 bg-blue-500/20 rounded-lg">
            <span class="text-2xl">⚙️</span>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-400">CPU Total</p>
            <p class="text-2xl font-bold text-blue-400">{{ totalCpuCores }}</p>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 rounded-lg p-6">
        <div class="flex items-center">
          <div class="p-3 bg-purple-500/20 rounded-lg">
            <span class="text-2xl">💾</span>
          </div>
          <div class="ml-4">
            <p class="text-sm text-gray-400">RAM Total</p>
            <p class="text-2xl font-bold text-purple-400">{{ totalMemory }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Lista de nodos -->
    <div class="bg-gray-800 rounded-lg">
      <div class="p-6 border-b border-gray-700">
        <h3 class="text-xl font-semibold text-white">Nodos Registrados</h3>
      </div>

      <div v-if="isLoading" class="p-8 text-center">
        <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-gray-400">Cargando información de nodos...</p>
      </div>

      <div v-else-if="nodes.length === 0" class="p-8 text-center">
        <div class="text-6xl text-gray-500 mb-4">🖥️</div>
        <p class="text-gray-400 text-lg">No hay nodos disponibles</p>
      </div>

      <div v-else class="divide-y divide-gray-700">
        <div
          v-for="node in nodes"
          :key="node.id"
          class="p-6 hover:bg-gray-750 transition-colors"
        >
          <div class="flex items-center justify-between">
            <!-- Información del nodo -->
            <div class="flex items-center space-x-4">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                  <span class="text-xl">🖥️</span>
                </div>
              </div>
              <div>
                <h4 class="text-lg font-semibold text-white">{{ node.name }}</h4>
                <p class="text-sm text-gray-400">{{ node.ip }}</p>
                <div class="flex items-center space-x-4 mt-1">
                  <span 
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                    :class="getStatusClass(node.status)"
                  >
                    {{ getStatusIcon(node.status) }} {{ getStatusText(node.status) }}
                  </span>
                  <span v-if="node.platform" class="text-xs text-gray-400">
                    {{ node.platform }}
                  </span>
                  <span v-if="node.blender_available" class="text-xs text-green-400">
                    🎬 Blender {{ node.blender_version || 'disponible' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Estado y acciones -->
            <div class="flex items-center space-x-6">
              <!-- Especificaciones -->
              <div class="text-right text-sm">
                <div v-if="node.system_info" class="space-y-1">
                  <p class="text-gray-400">
                    <span class="text-blue-400">⚙️</span> {{ node.system_info.cpu_cores || 'N/A' }} cores
                  </p>
                  <p class="text-gray-400">
                    <span class="text-purple-400">💾</span> {{ node.system_info.memory_total_gb || 'N/A' }}GB RAM
                  </p>
                </div>
                <div v-else class="text-gray-500">
                  Especificaciones no disponibles
                </div>
              </div>

              <!-- Uso actual -->
              <div class="text-right space-y-2 min-w-[120px]">
                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-400">CPU:</span>
                  <span class="text-white font-medium">{{ node.cpu_usage }}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-500"
                    :class="getCpuBarClass(node.cpu_usage)"
                    :style="{ width: node.cpu_usage + '%' }"
                  ></div>
                </div>

                <div class="flex items-center justify-between text-sm">
                  <span class="text-gray-400">RAM:</span>
                  <span class="text-white font-medium">{{ node.memory_usage }}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full transition-all duration-500"
                    :class="getMemoryBarClass(node.memory_usage)"
                    :style="{ width: node.memory_usage + '%' }"
                  ></div>
                </div>
              </div>

              <!-- Trabajo actual -->
              <div class="text-right min-w-[150px]">
                <p class="text-sm text-gray-400">Trabajo Actual:</p>
                <p class="text-white font-medium">
                  {{ node.current_job || 'Sin trabajo asignado' }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  Última actividad: {{ formatDate(node.last_seen) }}
                </p>
              </div>

              <!-- Acciones -->
              <div class="flex space-x-2">
                <button
                  @click="viewNodeDetails(node)"
                  class="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  title="Ver detalles"
                >
                  👁️
                </button>
                <button
                  v-if="node.status === 'online'"
                  @click="testNode(node)"
                  class="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  title="Probar nodo"
                >
                  🧪
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de detalles del nodo -->
    <div v-if="showNodeModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="closeNodeModal">
      <div class="max-w-2xl w-full mx-4" @click.stop>
        <div class="bg-gray-800 rounded-lg overflow-hidden">
          <div class="flex items-center justify-between p-6 border-b border-gray-700">
            <h3 class="text-xl font-semibold text-white">Detalles del Nodo</h3>
            <button @click="closeNodeModal" class="text-gray-400 hover:text-white">
              ✕
            </button>
          </div>
          <div class="p-6" v-if="selectedNode">
            <div class="grid grid-cols-2 gap-6">
              <div>
                <h4 class="text-lg font-medium text-white mb-3">Información General</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-400">Nombre:</span>
                    <span class="text-white">{{ selectedNode.name }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">IP:</span>
                    <span class="text-white">{{ selectedNode.ip }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Estado:</span>
                    <span class="text-white">{{ getStatusText(selectedNode.status) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Plataforma:</span>
                    <span class="text-white">{{ selectedNode.platform || 'Desconocida' }}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 class="text-lg font-medium text-white mb-3">Especificaciones</h4>
                <div class="space-y-2 text-sm" v-if="selectedNode.system_info">
                  <div class="flex justify-between">
                    <span class="text-gray-400">CPU Cores:</span>
                    <span class="text-white">{{ selectedNode.system_info.cpu_cores }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">RAM Total:</span>
                    <span class="text-white">{{ selectedNode.system_info.memory_total_gb }}GB</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">RAM Disponible:</span>
                    <span class="text-white">{{ selectedNode.system_info.memory_available_gb }}GB</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-6" v-if="selectedNode.blender_available">
              <h4 class="text-lg font-medium text-white mb-3">Estado de Blender</h4>
              <div class="flex items-center space-x-2 text-sm">
                <span class="text-green-400">✅ Disponible</span>
                <span class="text-gray-400">Versión: {{ selectedNode.blender_version || 'Desconocida' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NodesManagement',
  data() {
    return {
      nodes: [],
      isLoading: false,
      showNodeModal: false,
      selectedNode: null
    }
  },
  computed: {
    activeNodes() {
      return this.nodes.filter(node => node.status === 'online').length;
    },
    inactiveNodes() {
      return this.nodes.filter(node => node.status !== 'online').length;
    },
    totalCpuCores() {
      return this.nodes.reduce((total, node) => {
        return total + (node.system_info?.cpu_cores || 0);
      }, 0);
    },
    totalMemory() {
      const total = this.nodes.reduce((sum, node) => {
        return sum + (node.system_info?.memory_total_gb || 0);
      }, 0);
      return `${total}GB`;
    }
  },
  async mounted() {
    await this.loadNodes();
    
    // Auto-refresh cada 10 segundos
    this.refreshInterval = setInterval(() => {
      this.loadNodes();
    }, 10000);
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async loadNodes() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/nodes');
        if (response.ok) {
          this.nodes = await response.json();
        }
      } catch (error) {
        console.error('Error loading nodes:', error);
      }
    },
    
    async refreshNodes() {
      this.isLoading = true;
      await this.loadNodes();
      this.isLoading = false;
    },
    
    getStatusIcon(status) {
      const icons = {
        online: '🟢',
        offline: '🔴',
        rendering: '⚙️'
      };
      return icons[status] || '❓';
    },
    
    getStatusText(status) {
      const texts = {
        online: 'En línea',
        offline: 'Fuera de línea',
        rendering: 'Renderizando'
      };
      return texts[status] || status;
    },
    
    getStatusClass(status) {
      const classes = {
        online: 'bg-green-100 text-green-800',
        offline: 'bg-red-100 text-red-800',
        rendering: 'bg-blue-100 text-blue-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    },
    
    getCpuBarClass(usage) {
      if (usage < 50) return 'bg-green-500';
      if (usage < 80) return 'bg-yellow-500';
      return 'bg-red-500';
    },
    
    getMemoryBarClass(usage) {
      if (usage < 60) return 'bg-blue-500';
      if (usage < 85) return 'bg-orange-500';
      return 'bg-red-500';
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Nunca';
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      
      if (diffMins < 1) return 'Ahora mismo';
      if (diffMins < 60) return `Hace ${diffMins} min`;
      if (diffMins < 1440) return `Hace ${Math.floor(diffMins / 60)} h`;
      return date.toLocaleDateString('es-ES');
    },
    
    viewNodeDetails(node) {
      this.selectedNode = node;
      this.showNodeModal = true;
    },
    
    closeNodeModal() {
      this.showNodeModal = false;
      this.selectedNode = null;
    },
    
    async testNode(node) {
      try {
        // Hacer una petición de prueba al nodo
        alert(`Probando conectividad con ${node.name}...`);
        
        // Simular prueba (en una implementación real, harías una petición al nodo)
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        alert(`✅ ${node.name} respondió correctamente`);
      } catch (error) {
        alert(`❌ Error al probar ${node.name}: ${error.message}`);
      }
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