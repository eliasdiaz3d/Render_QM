<template>
  <div class="bg-gray-800 rounded-lg p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-semibold text-white flex items-center">
        🔔 Sistema de Notificaciones
      </h2>
      <button 
        @click="addTestNotification"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
      >
        Prueba Notificación
      </button>
    </div>

    <!-- Lista de Notificaciones -->
    <div class="space-y-3 max-h-96 overflow-y-auto">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="flex items-start p-4 rounded-lg border transition-all duration-200"
        :class="notification.read ? 'border-gray-600 bg-gray-800' : 'border-blue-500 bg-gray-750'"
      >
        <!-- Ícono -->
        <div class="flex-shrink-0 p-2 rounded-lg mr-4 bg-blue-500 bg-opacity-20">
          <span class="text-blue-400">🔔</span>
        </div>
        
        <!-- Contenido -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between mb-1">
            <h4 class="text-white font-medium">{{ notification.title }}</h4>
            <span class="text-gray-400 text-xs">
              {{ formatTime(notification.timestamp) }}
            </span>
          </div>
          <p class="text-gray-300 text-sm">{{ notification.message }}</p>
        </div>
        
        <!-- Indicador no leído -->
        <div v-if="!notification.read" class="flex-shrink-0 w-3 h-3 bg-blue-500 rounded-full ml-2"></div>
      </div>
    </div>

    <!-- Estado vacío -->
    <div v-if="notifications.length === 0" class="text-center py-12">
      <span class="text-6xl">🔔</span>
      <h3 class="mt-2 text-sm font-medium text-gray-300">No hay notificaciones</h3>
      <p class="mt-1 text-sm text-gray-500">Las notificaciones aparecerán aquí.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationSystem',
  data() {
    return {
      notifications: [
        {
          id: 1,
          title: 'Trabajo Completado',
          message: 'El trabajo "Escena Arquitectónica" se completó exitosamente.',
          read: false,
          timestamp: new Date(Date.now() - 300000)
        },
        {
          id: 2,
          title: 'Nodo Desconectado',
          message: 'El nodo "Render-Server" se desconectó.',
          read: true,
          timestamp: new Date(Date.now() - 900000)
        }
      ]
    }
  },
  methods: {
    addTestNotification() {
      const testNotification = {
        id: Date.now(),
        title: 'Notificación de Prueba',
        message: 'Esta es una notificación de prueba generada automáticamente.',
        read: false,
        timestamp: new Date()
      }
      this.notifications.unshift(testNotification)
    },
    
    formatTime(timestamp) {
      const now = new Date()
      const diff = now - timestamp
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Ahora mismo'
      if (minutes < 60) return `Hace ${minutes} min`
      
      const hours = Math.floor(minutes / 60)
      if (hours < 24) return `Hace ${hours}h`
      
      const days = Math.floor(hours / 24)
      return `Hace ${days}d`
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}
</style>