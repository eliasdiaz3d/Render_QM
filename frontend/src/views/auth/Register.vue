<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          🎬 Crear Cuenta
        </h2>
        <p class="mt-2 text-center text-sm text-gray-400">
          Regístrate para usar Render Queue Manager
        </p>
      </div>
      <div class="mt-8 bg-gray-800 rounded-lg p-6">
        <p class="text-center text-gray-400">
          Registro no disponible en modo demo.
        </p>
        <router-link 
          to="/login" 
          class="mt-4 block text-center text-blue-400 hover:text-blue-300 transition-colors"
        >
          Volver al login
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register'
}
</script>