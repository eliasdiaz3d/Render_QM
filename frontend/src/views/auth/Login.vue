<template>
  <div class="min-h-screen bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
          🎬 Render Queue Manager
        </h2>
        <p class="mt-2 text-center text-sm text-gray-400">
          Inicia sesión en tu cuenta
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="login">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-300">
              Usuario
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
              placeholder="admin"
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-300">
              Contraseña
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
              placeholder="admin123"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Iniciar Sesión
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      }
    }
  },
  methods: {
    login() {
      // Simulación de login
      if (this.form.username === 'admin' && this.form.password === 'admin123') {
        localStorage.setItem('authToken', 'fake-token')
        localStorage.setItem('userRole', 'admin')
        this.$router.push('/dashboard')
      } else {
        alert('Credenciales incorrectas')
      }
    }
  }
}
</script>