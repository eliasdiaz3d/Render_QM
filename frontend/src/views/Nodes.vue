<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold text-white flex items-center">
          🖥️ Gestión de Nodos
        </h1>
        <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
          ➕ Añadir Nodo
        </button>
      </div>

      <!-- Estadísticas de Nodos -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-green-400">3</div>
          <div class="text-gray-400">Nodos Activos</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-red-400">1</div>
          <div class="text-gray-400">Nodos Inactivos</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-blue-400">48</div>
          <div class="text-gray-400">CPU Cores Total</div>
        </div>
        <div class="bg-gray-800 rounded-lg p-6 text-center">
          <div class="text-3xl font-bold text-purple-400">128GB</div>
          <div class="text-gray-400">RAM Total</div>
        </div>
      </div>

      <!-- Lista de Nodos -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="node in nodes" :key="node.id" class="bg-gray-800 rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-xl font-semibold text-white">{{ node.name }}</h3>
            <span class="px-3 py-1 rounded-full text-sm font-medium"
                  :class="node.status === 'online' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'">
              {{ node.status === 'online' ? '🟢 Online' : '🔴 Offline' }}
            </span>
          </div>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-400">IP:</span>
              <span class="text-white">{{ node.ip }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">CPU:</span>
              <span class="text-white">{{ node.cpu }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">RAM:</span>
              <span class="text-white">{{ node.ram }}</span>
            </div>
            
            <!-- Uso actual -->
            <div v-if="node.status === 'online'">
              <div class="mt-4">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-400">CPU</span>
                  <span class="text-white">{{ node.cpuUsage }}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div class="bg-blue-500 h-2 rounded-full" :style="`width: ${node.cpuUsage}%`"></div>
                </div>
              </div>
              
              <div class="mt-2">
                <div class="flex justify-between text-sm mb-1">
                  <span class="text-gray-400">RAM</span>
                  <span class="text-white">{{ node.ramUsage }}%</span>
                </div>
                <div class="w-full bg-gray-700 rounded-full h-2">
                  <div class="bg-green-500 h-2 rounded-full" :style="`width: ${node.ramUsage}%`"></div>
                </div>
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
  name: 'Nodes',
  data() {
    return {
      nodes: [
        {
          id: 1,
          name: 'Workstation-01',
          ip: '192.168.1.100',
          cpu: '16 cores AMD Ryzen 9',
          ram: '64GB DDR4',
          status: 'online',
          cpuUsage: 85,
          ramUsage: 65
        },
        {
          id: 2,
          name: 'Workstation-02',
          ip: '192.168.1.101',
          cpu: '12 cores Intel i7',
          ram: '32GB DDR4',
          status: 'online',
          cpuUsage: 45,
          ramUsage: 35
        },
        {
          id: 3,
          name: 'Render-Server',
          ip: '192.168.1.200',
          cpu: '32 cores AMD Threadripper',
          ram: '128GB DDR4',
          status: 'offline',
          cpuUsage: 0,
          ramUsage: 0
        }
      ]
    }
  }
}
</script>