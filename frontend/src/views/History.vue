<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold text-white flex items-center">
          📊 Historial de Renders
        </h1>
        <div class="flex space-x-3">
          <select v-model="filterPeriod" class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
            <option value="today">Hoy</option>
            <option value="week">Última semana</option>
            <option value="month">Último mes</option>
            <option value="all">Todo el historial</option>
          </select>
          <button @click="exportHistory" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
            📥 Exportar
          </button>
        </div>
      </div>

      <!-- Estadísticas del Historial -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-green-400">{{ stats.completed }}</div>
          <div class="text-gray-400">Trabajos Completados</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-red-400">{{ stats.failed }}</div>
          <div class="text-gray-400">Trabajos Fallidos</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-blue-400">{{ stats.totalTime }}</div>
          <div class="text-gray-400">Tiempo Total</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-purple-400">{{ stats.avgTime }}</div>
          <div class="text-gray-400">Tiempo Promedio</div>
        </div>
      </div>

      <!-- Gráfico de Rendimiento -->
      <div class="bg-gray-800 rounded-lg p-6 mb-8">
        <h3 class="text-xl font-semibold text-white mb-4">Rendimiento Semanal</h3>
        <div class="h-64 flex items-end justify-between space-x-2">
          <div v-for="(day, index) in weeklyData" :key="index" class="flex-1 flex flex-col items-center">
            <div 
              class="w-full bg-blue-500 rounded-t transition-all duration-300 hover:bg-blue-400"
              :style="`height: ${(day.jobs / Math.max(...weeklyData.map(d => d.jobs))) * 100}%`"
              :title="`${day.jobs} trabajos`"
            ></div>
            <span class="text-gray-400 text-sm mt-2">{{ day.day }}</span>
          </div>
        </div>
      </div>

      <!-- Lista de Historial -->
      <div class="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div class="p-6 border-b border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-white">Historial Detallado</h3>
            <div class="flex items-center space-x-4">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar trabajos..."
                class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400"
              />
              <select v-model="statusFilter" class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white">
                <option value="">Todos los estados</option>
                <option value="completed">Completados</option>
                <option value="failed">Fallidos</option>
                <option value="cancelled">Cancelados</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-750">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Trabajo</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Estado</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Duración</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Nodo</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Fecha</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              <tr
                v-for="job in filteredJobs"
                :key="job.id"
                class="hover:bg-gray-750 transition-colors"
              >
                <!-- Información del Trabajo -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                        <span class="text-white font-medium">{{ job.name.charAt(0) }}</span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-white">{{ job.name }}</div>
                      <div class="text-sm text-gray-400">{{ job.file }}</div>
                      <div class="text-xs text-gray-500">{{ job.frames }} frames</div>
                    </div>
                  </div>
                </td>

                <!-- Estado -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getStatusClass(job.status)"
                  >
                    <span
                      class="w-2 h-2 rounded-full mr-1.5"
                      :class="getStatusDotClass(job.status)"
                    ></span>
                    {{ getStatusText(job.status) }}
                  </span>
                </td>

                <!-- Duración -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  <div class="flex flex-col">
                    <span>{{ job.duration }}</span>
                    <span class="text-xs text-gray-500">{{ job.framesPerHour }} frames/h</span>
                  </div>
                </td>

                <!-- Nodo -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {{ job.node }}
                </td>

                <!-- Fecha -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  <div class="flex flex-col">
                    <span>{{ formatDate(job.completedAt) }}</span>
                    <span class="text-xs text-gray-500">{{ formatTime(job.completedAt) }}</span>
                  </div>
                </td>

                <!-- Acciones -->
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex space-x-2">
                    <button
                      @click="viewDetails(job)"
                      class="text-blue-400 hover:text-blue-300 transition-colors"
                      title="Ver detalles"
                    >
                      👁️
                    </button>
                    <button
                      v-if="job.status === 'completed'"
                      @click="downloadResult(job)"
                      class="text-green-400 hover:text-green-300 transition-colors"
                      title="Descargar resultado"
                    >
                      📥
                    </button>
                    <button
                      @click="rerunJob(job)"
                      class="text-yellow-400 hover:text-yellow-300 transition-colors"
                      title="Ejecutar de nuevo"
                    >
                      🔄
                    </button>
                    <button
                      @click="deleteJob(job)"
                      class="text-red-400 hover:text-red-300 transition-colors"
                      title="Eliminar del historial"
                    >
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="filteredJobs.length === 0" class="text-center py-12">
          <div class="text-6xl mb-4">📊</div>
          <h3 class="mt-2 text-sm font-medium text-gray-300">No hay trabajos en el historial</h3>
          <p class="mt-1 text-sm text-gray-500">Los trabajos completados aparecerán aquí.</p>
        </div>

        <!-- Paginación -->
        <div v-if="filteredJobs.length > 0" class="bg-gray-750 px-6 py-3 flex items-center justify-between">
          <div class="text-sm text-gray-400">
            Mostrando {{ filteredJobs.length }} de {{ totalJobs }} trabajos
          </div>
          <div class="flex space-x-2">
            <button class="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm">
              Anterior
            </button>
            <button class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm">
              1
            </button>
            <button class="px-3 py-1 bg-gray-600 hover:bg-gray-500 text-white rounded text-sm">
              Siguiente
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History',
  data() {
    return {
      filterPeriod: 'week',
      searchQuery: '',
      statusFilter: '',
      
      stats: {
        completed: 145,
        failed: 8,
        totalTime: '127h',
        avgTime: '2.5h'
      },
      
      weeklyData: [
        { day: 'Lun', jobs: 12 },
        { day: 'Mar', jobs: 18 },
        { day: 'Mié', jobs: 15 },
        { day: 'Jue', jobs: 22 },
        { day: 'Vie', jobs: 25 },
        { day: 'Sáb', jobs: 8 },
        { day: 'Dom', jobs: 5 }
      ],
      
      jobs: [
        {
          id: 1,
          name: 'Escena Arquitectónica Premium',
          file: 'arquitectura_premium_v3.blend',
          frames: 120,
          status: 'completed',
          duration: '2h 15m',
          framesPerHour: 53,
          node: 'Workstation-01',
          completedAt: new Date(Date.now() - 3600000), // 1 hora atrás
          startedAt: new Date(Date.now() - 11700000)   // 3h 15m atrás
        },
        {
          id: 2,
          name: 'Animación Personaje Walk',
          file: 'character_walk_cycle.blend',
          frames: 240,
          status: 'completed',
          duration: '4h 30m',
          framesPerHour: 53,
          node: 'Render-Server',
          completedAt: new Date(Date.now() - 14400000), // 4 horas atrás
          startedAt: new Date(Date.now() - 30600000)    // 8h 30m atrás
        },
        {
          id: 3,
          name: 'Producto Comercial',
          file: 'product_showcase.blend',
          frames: 1,
          status: 'completed',
          duration: '45m',
          framesPerHour: 1,
          node: 'Workstation-02',
          completedAt: new Date(Date.now() - 7200000), // 2 horas atrás
          startedAt: new Date(Date.now() - 9900000)    // 2h 45m atrás
        },
        {
          id: 4,
          name: 'Explosión VFX',
          file: 'explosion_effect.blend',
          frames: 180,
          status: 'failed',
          duration: '1h 12m',
          framesPerHour: 0,
          node: 'Workstation-01',
          completedAt: new Date(Date.now() - 21600000), // 6 horas atrás
          startedAt: new Date(Date.now() - 25920000)    // 7h 12m atrás
        },
        {
          id: 5,
          name: 'Interior Moderno',
          file: 'modern_interior.blend',
          frames: 1,
          status: 'completed',
          duration: '1h 30m',
          framesPerHour: 1,
          node: 'Workstation-02',
          completedAt: new Date(Date.now() - 86400000), // 1 día atrás
          startedAt: new Date(Date.now() - 91800000)    // 1d 1h 30m atrás
        },
        {
          id: 6,
          name: 'Logo Animado',
          file: 'logo_animation.blend',
          frames: 150,
          status: 'completed',
          duration: '2h 45m',
          framesPerHour: 55,
          node: 'Render-Server',
          completedAt: new Date(Date.now() - 172800000), // 2 días atrás
          startedAt: new Date(Date.now() - 182700000)    // 2d 2h 45m atrás
        }
      ]
    }
  },
  
  computed: {
    filteredJobs() {
      let filtered = this.jobs
      
      // Filtrar por búsqueda
      if (this.searchQuery) {
        filtered = filtered.filter(job => 
          job.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          job.file.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      }
      
      // Filtrar por estado
      if (this.statusFilter) {
        filtered = filtered.filter(job => job.status === this.statusFilter)
      }
      
      // Filtrar por período
      if (this.filterPeriod !== 'all') {
        const now = new Date()
        const filterTime = {
          today: 24 * 60 * 60 * 1000,
          week: 7 * 24 * 60 * 60 * 1000,
          month: 30 * 24 * 60 * 60 * 1000
        }[this.filterPeriod]
        
        filtered = filtered.filter(job => 
          now - job.completedAt < filterTime
        )
      }
      
      return filtered.sort((a, b) => b.completedAt - a.completedAt)
    },
    
    totalJobs() {
      return this.jobs.length
    }
  },
  
  methods: {
    getStatusClass(status) {
      const classes = {
        completed: 'bg-green-100 text-green-800',
        failed: 'bg-red-100 text-red-800',
        cancelled: 'bg-gray-100 text-gray-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },
    
    getStatusDotClass(status) {
      const classes = {
        completed: 'bg-green-500',
        failed: 'bg-red-500',
        cancelled: 'bg-gray-500'
      }
      return classes[status] || 'bg-gray-500'
    },
    
    getStatusText(status) {
      const texts = {
        completed: 'Completado',
        failed: 'Fallido',
        cancelled: 'Cancelado'
      }
      return texts[status] || status
    },
    
    formatDate(date) {
      return date.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    },
    
    formatTime(date) {
      return date.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    viewDetails(job) {
      alert(`Ver detalles del trabajo: ${job.name}`)
    },
    
    downloadResult(job) {
      alert(`Descargando resultado de: ${job.name}`)
    },
    
    rerunJob(job) {
      if (confirm(`¿Ejecutar de nuevo el trabajo "${job.name}"?`)) {
        alert(`Trabajo "${job.name}" añadido a la cola`)
      }
    },
    
    deleteJob(job) {
      if (confirm(`¿Eliminar "${job.name}" del historial?`)) {
        const index = this.jobs.findIndex(j => j.id === job.id)
        if (index > -1) {
          this.jobs.splice(index, 1)
        }
      }
    },
    
    exportHistory() {
      alert('Exportando historial...')
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}
</style>