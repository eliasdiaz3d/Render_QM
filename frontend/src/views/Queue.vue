<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold text-white flex items-center">
          📋 Cola de Trabajos
        </h1>
        <button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
          ➕ Nuevo Trabajo
        </button>
      </div>
      
      <!-- Estadísticas de la Cola -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-yellow-400">12</div>
          <div class="text-gray-400">En Cola</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-blue-400">4</div>
          <div class="text-gray-400">Procesando</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-green-400">28</div>
          <div class="text-gray-400">Completados</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-red-400">2</div>
          <div class="text-gray-400">Fallidos</div>
        </div>
      </div>

      <!-- Lista de Trabajos -->
      <div class="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
        <div class="p-6 border-b border-gray-700">
          <h3 class="text-xl font-semibold text-white">Trabajos en Cola</h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-750">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Trabajo</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Estado</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Progreso</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Tiempo</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              <tr v-for="job in jobs" :key="job.id" class="hover:bg-gray-750">
                <td class="px-6 py-4">
                  <div class="text-white font-medium">{{ job.name }}</div>
                  <div class="text-gray-400 text-sm">{{ job.file }}</div>
                </td>
                <td class="px-6 py-4">
                  <span class="px-2 py-1 rounded-full text-xs font-medium"
                        :class="getStatusClass(job.status)">
                    {{ job.status }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <div class="text-white">{{ job.progress }}%</div>
                  <div class="w-full bg-gray-700 rounded-full h-2 mt-1">
                    <div class="bg-blue-500 h-2 rounded-full" :style="`width: ${job.progress}%`"></div>
                  </div>
                </td>
                <td class="px-6 py-4 text-gray-300">{{ job.estimatedTime }}</td>
                <td class="px-6 py-4">
                  <button class="text-blue-400 hover:text-blue-300 mr-3">▶️</button>
                  <button class="text-red-400 hover:text-red-300">⏹️</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Queue',
  data() {
    return {
      jobs: [
        {
          id: 1,
          name: 'Escena Arquitectónica',
          file: 'arquitectura_v2.blend',
          status: 'Procesando',
          progress: 65,
          estimatedTime: '2h 15m'
        },
        {
          id: 2,
          name: 'Animación Personaje',
          file: 'character_walk.blend',
          status: 'En Cola',
          progress: 0,
          estimatedTime: '4h 30m'
        },
        {
          id: 3,
          name: 'Producto 3D',
          file: 'product_render.blend',
          status: 'En Cola',
          progress: 0,
          estimatedTime: '1h 45m'
        }
      ]
    }
  },
  methods: {
    getStatusClass(status) {
      const classes = {
        'Procesando': 'bg-blue-100 text-blue-800',
        'En Cola': 'bg-yellow-100 text-yellow-800',
        'Completado': 'bg-green-100 text-green-800',
        'Fallido': 'bg-red-100 text-red-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}
</style>