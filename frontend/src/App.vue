<template>
  <div id="app" class="min-h-screen bg-gray-900">
    <router-view />
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()

    onMounted(() => {
      // Si hay token, intentar obtener perfil del usuario
      if (authStore.isAuthenticated) {
        authStore.fetchProfile()
      }
    })

    return {}
  }
}
</script>