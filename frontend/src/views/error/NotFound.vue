<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-600">404</h1>
      <h2 class="text-2xl font-bold text-white mt-4">Página No Encontrada</h2>
      <p class="text-gray-400 mt-2">La página que buscas no existe.</p>
      <router-link 
        to="/dashboard" 
        class="mt-6 inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
      >
        Volver al Dashboard
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>