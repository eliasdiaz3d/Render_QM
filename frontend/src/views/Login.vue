<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-blue-600 rounded-xl flex items-center justify-center shadow-lg">
          <svg class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          🎬 Render Queue Manager
        </h2>
        <p class="mt-2 text-center text-sm text-gray-400">
          Sistema de gestión de colas de render distribuido
        </p>
      </div>
      
      <div class="bg-gray-800 rounded-lg shadow-xl border border-gray-700 p-8">
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="username" class="label">Usuario</label>
            <input
              id="username"
              name="username"
              type="text"
              required
              v-model="form.username"
              class="input"
              placeholder="Ingresa tu usuario"
              :disabled="authStore.loading"
              autocomplete="username"
            />
          </div>
          
          <div>
            <label for="password" class="label">Contraseña</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              v-model="form.password"
              class="input"
              placeholder="Ingresa tu contraseña"
              :disabled="authStore.loading"
              autocomplete="current-password"
            />
          </div>

          <!-- Error Message -->
          <div v-if="authStore.error" class="rounded-md bg-red-900 border border-red-600 p-4">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-sm text-red-300">
                {{ authStore.error }}
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="authStore.loading"
              class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <span v-if="authStore.loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
                <svg class="animate-spin h-5 w-5 text-blue-300" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ authStore.loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
            </button>
          </div>

          <!-- Credenciales por defecto -->
          <div class="mt-4 p-4 bg-gray-900 border border-gray-600 rounded-lg">
            <p class="text-xs text-gray-400 text-center">
              <strong class="text-gray-300">Credenciales por defecto:</strong><br>
              Usuario: <code class="bg-gray-700 px-2 py-1 rounded text-blue-300">admin</code><br>
              Contraseña: <code class="bg-gray-700 px-2 py-1 rounded text-blue-300">admin123</code>
            </p>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = ref({
      username: 'admin',
      password: 'admin123'
    })

    const handleLogin = async () => {
      authStore.clearError()
      
      const success = await authStore.login(form.value)
      
      if (success) {
        router.push('/')
      }
    }

    return {
      form,
      authStore,
      handleLogin
    }
  }
}
</script>