<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <h1 class="text-3xl font-bold text-white mb-6">⚙️ Gestión de Trabajos</h1>
      
      <div class="bg-gray-800 rounded-lg p-6">
        <p class="text-gray-400 mb-4">Gestiona todos tus trabajos de render desde aquí.</p>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <router-link to="/dashboard" class="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg text-center transition-colors">
            ➕ Crear Nuevo Trabajo
          </router-link>
          <router-link to="/queue" class="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg text-center transition-colors">
            📋 Ver Cola
          </router-link>
          <router-link to="/history" class="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg text-center transition-colors">
            📊 Ver Historial
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Jobs'
}
</script>