import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('auth_token') || null,
    loading: false,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    username: (state) => state.user?.username || 'Usuario'
  },

  actions: {
    async login(credentials) {
      this.loading = true
      this.error = null

      try {
        // Crear FormData para el login
        const formData = new FormData()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)

        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Error de autenticación')
        }

        const data = await response.json()
        
        this.token = data.access_token
        localStorage.setItem('auth_token', data.access_token)

        // Obtener perfil del usuario
        await this.fetchProfile()

        return true
      } catch (error) {
        this.error = error.message
        return false
      } finally {
        this.loading = false
      }
    },

    async fetchProfile() {
      try {
        const response = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        if (response.ok) {
          this.user = await response.json()
        }
      } catch (error) {
        console.error('Error obteniendo perfil:', error)
      }
    },

    logout() {
      this.user = null
      this.token = null
      this.error = null
      localStorage.removeItem('auth_token')
    },

    clearError() {
      this.error = null
    }
  }
})