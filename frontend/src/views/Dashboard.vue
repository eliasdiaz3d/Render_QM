<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto space-y-8">
      <!-- Header del Dashboard -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-white mb-2">
          🎬 Render Queue Manager
        </h1>
        <p class="text-gray-400">Panel de control avanzado para gestión de renders</p>
        <div v-if="systemStatus" class="mt-2 text-sm">
          <span :class="systemStatus.blender_available ? 'text-green-400' : 'text-red-400'">
            {{ systemStatus.blender_available ? '✅ Blender disponible' : '❌ Blender no disponible' }}
          </span>
          <span v-if="systemStatus.blender_version" class="ml-2 text-gray-400">
            (v{{ systemStatus.blender_version }})
          </span>
        </div>
      </div>

      <!-- Navegación por pestañas -->
      <div class="bg-gray-800 rounded-lg p-1 mb-6">
        <nav class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click.prevent="changeTab(tab.id)"
            class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all cursor-pointer select-none"
            :class="activeTab === tab.id 
              ? 'bg-blue-600 text-white shadow-lg' 
              : 'text-gray-300 hover:text-white hover:bg-gray-700'"
            :disabled="false"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Contenido de las pestañas -->
      <div class="space-y-6" :key="activeTab">
        <!-- Vista General -->
        <div v-if="activeTab === 'overview'" class="space-y-6">
          <!-- Estadísticas principales con datos reales -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-gray-800 rounded-lg p-6">
              <h3 class="text-xl font-semibold text-white mb-4">📊 Estado de la Cola</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-blue-400">{{ queueStatus.processing_jobs || 0 }}</div>
                  <div class="text-sm text-gray-400">Procesando</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-yellow-400">{{ queueStatus.pending_jobs || 0 }}</div>
                  <div class="text-sm text-gray-400">En Cola</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-green-400">{{ queueStatus.completed_jobs || 0 }}</div>
                  <div class="text-sm text-gray-400">Completados</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-red-400">{{ queueStatus.failed_jobs || 0 }}</div>
                  <div class="text-sm text-gray-400">Fallidos</div>
                </div>
              </div>
            </div>

            <div class="bg-gray-800 rounded-lg p-6">
              <h3 class="text-xl font-semibold text-white mb-4">🖥️ Sistema</h3>
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-green-400">{{ dashboardStats.active_nodes || 1 }}</div>
                  <div class="text-sm text-gray-400">Nodos Activos</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-purple-400">{{ dashboardStats.total_render_time || '0h' }}</div>
                  <div class="text-sm text-gray-400">Tiempo Total</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-indigo-400">{{ dashboardStats.queue_efficiency || 0 }}%</div>
                  <div class="text-sm text-gray-400">Eficiencia</div>
                </div>
                <div class="text-center p-4 bg-gray-700 rounded-lg">
                  <div class="text-2xl font-bold text-cyan-400">{{ queueStatus.total_jobs || 0 }}</div>
                  <div class="text-sm text-gray-400">Total Trabajos</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Estado del sistema -->
          <div class="bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-semibold text-white mb-4">🔧 Estado del Sistema</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div class="flex items-center justify-between p-3 bg-gray-700 rounded">
                <span class="text-gray-300">API Backend</span>
                <span class="px-2 py-1 bg-green-500 text-white rounded text-sm">✅ Online</span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-700 rounded">
                <span class="text-gray-300">Blender Engine</span>
                <span 
                  class="px-2 py-1 rounded text-sm transition-all"
                  :class="systemStatus?.blender_available ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
                >
                  {{ systemStatus?.blender_available ? '✅ Disponible' : '❌ No disponible' }}
                </span>
              </div>
              <div class="flex items-center justify-between p-3 bg-gray-700 rounded">
                <span class="text-gray-300">Cola de Render</span>
                <span 
                  class="px-2 py-1 rounded text-sm"
                  :class="queueStatus.queue_health === 'healthy' ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'"
                >
                  {{ queueStatus.queue_health === 'healthy' ? '✅ Saludable' : '⚠️ Degradada' }}
                </span>
              </div>
            </div>
            
            <!-- Información adicional de Blender -->
            <div v-if="systemStatus?.blender_path && systemStatus?.blender_available" class="mt-4 p-3 bg-gray-700 rounded">
              <div class="text-sm text-gray-300">
                <strong>Ruta de Blender:</strong> {{ systemStatus.blender_path }}
              </div>
              <div v-if="systemStatus.blender_version" class="text-sm text-gray-300 mt-1">
                <strong>Versión:</strong> {{ systemStatus.blender_version }}
              </div>
            </div>
          </div>

          <!-- Accesos rápidos -->
          <div class="bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-semibold text-white mb-4">🚀 Accesos Rápidos</h3>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <button
                @click.prevent="changeTab('create')"
                class="p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg text-white font-medium hover:from-blue-600 hover:to-purple-700 transition-all focus:outline-none focus:ring-2 focus:ring-blue-500"
                :disabled="!systemStatus?.blender_available"
                :class="!systemStatus?.blender_available ? 'opacity-50 cursor-not-allowed' : ''"
              >
                ➕ Nuevo Trabajo
              </button>
              <button
                @click.prevent="changeTab('jobs')"
                class="p-4 bg-gradient-to-r from-green-500 to-teal-600 rounded-lg text-white font-medium hover:from-green-600 hover:to-teal-700 transition-all focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                📋 Ver Cola
              </button>
              <button
                @click.prevent="changeTab('monitoring')"
                class="p-4 bg-gradient-to-r from-orange-500 to-red-600 rounded-lg text-white font-medium hover:from-orange-600 hover:to-red-700 transition-all focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                📊 Monitoreo
              </button>
              <button
                @click.prevent="changeTab('settings')"
                class="p-4 bg-gradient-to-r from-purple-500 to-pink-600 rounded-lg text-white font-medium hover:from-purple-600 hover:to-pink-700 transition-all focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                ⚙️ Configuración
              </button>
            </div>
          </div>
        </div>

        <!-- Crear Trabajo -->
        <div v-if="activeTab === 'create'" class="space-y-6">
          <JobCreationForm 
            @job-created="handleJobCreated" 
            @view-job="viewJob"
          />
        </div>

        <!-- Lista de Trabajos -->
        <div v-if="activeTab === 'jobs'" class="space-y-6">
          <JobsList 
            ref="jobsList"
            @create-job="changeTab('create')"
          />
        </div>

        <!-- Gestión de Nodos -->
        <div v-if="activeTab === 'nodes'" class="space-y-6">
          <NodesManagement />
        </div>

        <!-- Monitoreo en Tiempo Real -->
        <div v-if="activeTab === 'monitoring'" class="space-y-6">
          <RealtimeCharts />
        </div>

        <!-- Configuración del Sistema -->
        <div v-if="activeTab === 'settings'" class="space-y-6">
          <SystemSettings @blender-config-updated="handleBlenderUpdate" />
        </div>

        <!-- Centro de Notificaciones -->
        <div v-if="activeTab === 'notifications'" class="space-y-6">
          <NotificationSystem 
            @new-notification="handleNewNotification"
            @notification-read="handleNotificationRead"
          />
        </div>
      </div>

      <!-- Indicador de conexión mejorado -->
      <div class="fixed bottom-4 right-4 z-50">
        <div
          class="bg-gray-800 rounded-lg shadow-xl p-3 flex items-center space-x-2 border transition-all"
          :class="isConnected ? 'border-green-500' : 'border-red-500'"
        >
          <div
            class="w-3 h-3 rounded-full animate-pulse"
            :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
          ></div>
          <div class="flex flex-col">
            <span class="text-sm text-white">
              {{ isConnected ? 'Backend conectado' : 'Backend desconectado' }}
            </span>
            <div class="text-xs text-gray-400">
              {{ lastUpdate }}
            </div>
          </div>
          <!-- Indicador de estado de Blender -->
          <div v-if="systemStatus" class="ml-2 text-xs">
            <span 
              class="px-2 py-1 rounded text-xs"
              :class="systemStatus.blender_available ? 'bg-green-600 text-white' : 'bg-red-600 text-white'"
            >
              {{ systemStatus.blender_available ? 'B✓' : 'B✗' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Notificación flotante para cambios de configuración -->
      <transition name="notification">
        <div
          v-if="showConfigNotification"
          class="fixed top-4 right-4 z-50 bg-blue-600 text-white p-4 rounded-lg shadow-xl"
        >
          <div class="flex items-center space-x-2">
            <span class="text-xl">⚙️</span>
            <div>
              <div class="font-medium">Configuración Actualizada</div>
              <div class="text-sm opacity-90">{{ configNotificationMessage }}</div>
            </div>
            <button @click="showConfigNotification = false" class="text-white hover:bg-blue-700 rounded p-1">
              ✕
            </button>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import JobCreationForm from '@/components/dashboard/JobCreationForm.vue'
import JobsList from '@/components/dashboard/JobsList.vue'
import NodesManagement from '@/components/dashboard/NodesManagement.vue'
import RealtimeCharts from '@/components/dashboard/RealtimeCharts.vue'
import NotificationSystem from '@/components/dashboard/NotificationSystem.vue'
import SystemSettings from '@/components/dashboard/SystemSettings.vue'

export default {
  name: 'Dashboard',
  components: {
    JobCreationForm,
    JobsList,
    NodesManagement,
    RealtimeCharts,
    NotificationSystem,
    SystemSettings
  },
  
  watch: {
    activeTab(newTab, oldTab) {
      console.log(`Tab cambiado de "${oldTab}" a "${newTab}"`);
      
      // Scroll al inicio cuando cambies de pestaña
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
      // Actualizar título de la página
      const tab = this.tabs.find(t => t.id === newTab);
      if (tab) {
        document.title = `${tab.name} - Render Queue Manager`;
      }
    }
  },
  data() {
    return {
      activeTab: 'overview',
      isConnected: false,
      lastUpdate: 'Nunca',
      updateInterval: null,
      showConfigNotification: false,
      configNotificationMessage: '',
      
      tabs: [
        { id: 'overview', name: 'Vista General', icon: '🏠' },
        { id: 'create', name: 'Crear Trabajo', icon: '➕' },
        { id: 'jobs', name: 'Trabajos', icon: '📋' },
        { id: 'nodes', name: 'Nodos', icon: '🖥️' },
        { id: 'monitoring', name: 'Monitoreo', icon: '📊' },
        { id: 'settings', name: 'Configuración', icon: '⚙️' },
        { id: 'notifications', name: 'Notificaciones', icon: '🔔' }
      ],
      
      // Datos del sistema
      systemStatus: null,
      queueStatus: {
        total_jobs: 0,
        pending_jobs: 0,
        processing_jobs: 0,
        completed_jobs: 0,
        failed_jobs: 0,
        queue_health: 'healthy'
      },
      dashboardStats: {
        total_jobs: 0,
        active_jobs: 0,
        completed_today: 0,
        failed_jobs: 0,
        total_nodes: 1,
        active_nodes: 1,
        total_render_time: '0h',
        queue_efficiency: 0
      }
    }
  },
  
  async mounted() {
    await this.loadInitialData();
    this.startPeriodicUpdates();
  },
  
  beforeUnmount() {
    this.stopPeriodicUpdates();
  },
  
  methods: {
    async loadInitialData() {
      await Promise.all([
        this.checkSystemHealth(),
        this.loadQueueStatus(),
        this.loadDashboardStats()
      ]);
    },

    changeTab(tabId) {
      console.log(`Cambiando a pestaña: ${tabId} (desde: ${this.activeTab})`);
      
      // Prevenir navegación si es la misma pestaña
      if (this.activeTab === tabId) {
        console.log('Ya estás en esta pestaña');
        return;
      }
      
      // Validar que la pestaña existe
      const tabExists = this.tabs.find(tab => tab.id === tabId);
      if (!tabExists) {
        console.error(`Pestaña no encontrada: ${tabId}`);
        return;
      }
      
      // Cambiar pestaña con forzado de reactividad
      this.activeTab = tabId;
      this.$nextTick(() => {
        console.log(`Pestaña cambiada exitosamente a: ${this.activeTab}`);
        // Emitir evento personalizado para debugging
        this.$emit('tab-changed', { from: this.activeTab, to: tabId });
      });
    },
    
    // Método adicional para debugging
    debugState() {
      console.log('Estado actual del Dashboard:', {
        activeTab: this.activeTab,
        tabs: this.tabs.map(t => t.id),
        isConnected: this.isConnected,
        systemStatus: this.systemStatus
      });
    },
    
    handleBlenderUpdate(configData) {
      console.log('Configuración de Blender actualizada:', configData);
      
      // Actualizar estado del sistema inmediatamente
      if (this.systemStatus) {
        this.systemStatus.blender_available = configData.verification?.valid || false;
        this.systemStatus.blender_path = configData.blender_path;
        this.systemStatus.blender_version = configData.verification?.version;
      }
      
      // Mostrar notificación de actualización
      this.showConfigUpdateNotification(configData);
      
      // Actualizar datos completos del sistema
      setTimeout(async () => {
        await this.refreshAllData();
      }, 1000);
    },
    
    showConfigUpdateNotification(configData) {
      const isValid = configData.verification?.valid;
      this.configNotificationMessage = isValid 
        ? `Blender configurado correctamente (${configData.verification.version})`
        : 'Error en la configuración de Blender';
      
      this.showConfigNotification = true;
      
      // Auto-ocultar después de 5 segundos
      setTimeout(() => {
        this.showConfigNotification = false;
      }, 5000);
    },
    
    async checkSystemHealth() {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          this.systemStatus = await response.json();
          this.isConnected = true;
        } else {
          this.isConnected = false;
        }
      } catch (error) {
        console.error('Error checking system health:', error);
        this.isConnected = false;
        this.systemStatus = { blender_available: false };
      }
    },
    
    async loadQueueStatus() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/queue/status');
        if (response.ok) {
          this.queueStatus = await response.json();
        }
      } catch (error) {
        console.error('Error loading queue status:', error);
      }
    },
    
    async loadDashboardStats() {
      try {
        const response = await fetch('http://localhost:8000/api/v1/stats/dashboard');
        if (response.ok) {
          this.dashboardStats = await response.json();
        }
      } catch (error) {
        console.error('Error loading dashboard stats:', error);
      }
    },
    
    startPeriodicUpdates() {
      // Actualizar cada 10 segundos
      this.updateInterval = setInterval(async () => {
        await this.refreshAllData();
      }, 10000);
    },
    
    stopPeriodicUpdates() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
    },
    
    async refreshAllData() {
      await this.loadInitialData();
      this.lastUpdate = new Date().toLocaleTimeString();
      
      // Actualizar lista de trabajos si está visible
      if (this.activeTab === 'jobs' && this.$refs.jobsList) {
        await this.$refs.jobsList.refreshJobs();
      }
    },
    
    handleJobCreated(job) {
      console.log('Nuevo trabajo creado:', job);
      
      // Actualizar estadísticas inmediatamente
      this.queueStatus.total_jobs++;
      this.queueStatus.pending_jobs++;
      this.dashboardStats.total_jobs++;
      this.dashboardStats.active_jobs++;
      
      // Mostrar notificación
      this.showNotification('success', 'Trabajo Creado', `"${job.name}" ha sido añadido a la cola`);
      
      // Actualizar datos completos
      setTimeout(() => {
        this.refreshAllData();
      }, 1000);
    },
    
    viewJob(jobId) {
      // Cambiar a la pestaña de trabajos
      this.changeTab('jobs');
      
      // Buscar el trabajo en la lista (si ya está cargada)
      setTimeout(() => {
        if (this.$refs.jobsList) {
          // Scroll hacia el trabajo específico
          console.log(`Mostrando trabajo: ${jobId}`);
        }
      }, 100);
    },
    
    handleNewNotification(notification) {
      console.log('Nueva notificación:', notification);
    },
    
    handleNotificationRead(notificationId) {
      console.log('Notificación leída:', notificationId);
    },
    
    showNotification(type, title, message) {
      // En una aplicación real, usarías un sistema de notificaciones
      // Por ahora, solo log en consola
      console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
      
      // Mostrar brevemente en la UI
      const notification = { type, title, message, timestamp: new Date() };
      
      // Podrías añadir a una lista de notificaciones temporal
      // y mostrarlas en el componente de notificaciones
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}

/* Transiciones para notificaciones */
.notification-enter-active, .notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from, .notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Animaciones para cambios de estado */
.transition-all {
  transition: all 0.3s ease;
}

/* Pulso para indicadores */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>