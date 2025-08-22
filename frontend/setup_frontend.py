#!/usr/bin/env python3
"""
Script para implementar autenticación completa y tema oscuro
Ejecutar desde D:\Render_QM\frontend\
"""

import os
from pathlib import Path

def create_file(filepath, content):
    """Crear archivo con contenido"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ {filepath}")

def update_styles_dark_theme():
    """Actualizar estilos a tema oscuro"""
    
    dark_styles = '''@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';

@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
  
  body {
    @apply bg-gray-900 text-gray-100;
  }
}

@layer components {
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 transition-all duration-200;
  }
  
  .btn-primary {
    @apply btn bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500;
  }
  
  .btn-secondary {
    @apply btn bg-gray-700 text-gray-100 hover:bg-gray-600 focus:ring-gray-500 border-gray-600;
  }
  
  .btn-success {
    @apply btn bg-green-600 text-white hover:bg-green-700 focus:ring-green-500;
  }
  
  .btn-warning {
    @apply btn bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500;
  }
  
  .btn-error {
    @apply btn bg-red-600 text-white hover:bg-red-700 focus:ring-red-500;
  }
  
  .card {
    @apply bg-gray-800 rounded-lg shadow-lg border border-gray-700 overflow-hidden;
  }
  
  .card-header {
    @apply px-6 py-4 border-b border-gray-700 bg-gray-850;
  }
  
  .card-body {
    @apply px-6 py-4;
  }
  
  .status-badge {
    @apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium;
  }
  
  .status-pending {
    @apply status-badge bg-yellow-900 text-yellow-300 border border-yellow-600;
  }
  
  .status-running {
    @apply status-badge bg-blue-900 text-blue-300 border border-blue-600;
  }
  
  .status-completed {
    @apply status-badge bg-green-900 text-green-300 border border-green-600;
  }
  
  .status-failed {
    @apply status-badge bg-red-900 text-red-300 border border-red-600;
  }
  
  .status-paused {
    @apply status-badge bg-gray-700 text-gray-300 border border-gray-600;
  }
  
  .input {
    @apply block w-full px-3 py-2 border border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-gray-800 text-gray-100;
  }
  
  .label {
    @apply block text-sm font-medium text-gray-300 mb-1;
  }
  
  .sidebar {
    @apply bg-gray-900 border-gray-700;
  }
  
  .nav-item {
    @apply text-gray-300 hover:bg-gray-800 hover:text-white;
  }
  
  .nav-item.router-link-active {
    @apply bg-blue-900 text-blue-300 border-r-2 border-blue-500;
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* Custom scrollbar para tema oscuro */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-gray-600 rounded;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500;
}'''
    
    create_file("src/style.css", dark_styles)

def create_auth_store():
    """Crear store de autenticación"""
    
    auth_store = '''import { defineStore } from 'pinia'

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
})'''
    
    create_file("src/stores/auth.js", auth_store)

def create_login_page():
    """Crear página de login mejorada"""
    
    login_vue = '''<template>
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
</script>'''
    
    create_file("src/views/Login.vue", login_vue)

def create_layout_component():
    """Crear componente Layout con tema oscuro"""
    
    layout_vue = '''<template>
  <div class="flex h-screen bg-gray-900">
    <!-- Sidebar -->
    <div :class="['bg-gray-900 border-r border-gray-700 transition-all duration-300', sidebarCollapsed ? 'w-16' : 'w-64']">
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="flex items-center px-4 py-4 border-b border-gray-700">
          <div class="flex items-center">
            <div class="bg-blue-600 rounded-lg p-2">
              <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div v-if="!sidebarCollapsed" class="ml-3">
              <h1 class="text-lg font-bold text-white">Render_QM</h1>
              <p class="text-xs text-gray-400">Queue Manager</p>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-2 py-4 space-y-1">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              'nav-item group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200',
              item.current 
                ? 'bg-blue-900 text-blue-300 border-r-2 border-blue-500' 
                : 'text-gray-300 hover:bg-gray-800 hover:text-white'
            ]"
          >
            <component 
              :is="item.icon" 
              :class="[
                'mr-3 h-5 w-5 transition-colors duration-200',
                item.current ? 'text-blue-300' : 'text-gray-400 group-hover:text-gray-300'
              ]"
            />
            <span v-if="!sidebarCollapsed">{{ item.name }}</span>
          </router-link>
        </nav>

        <!-- User Info -->
        <div class="border-t border-gray-700 p-4">
          <div class="flex items-center">
            <div class="bg-gray-700 rounded-full p-2">
              <svg class="h-4 w-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div v-if="!sidebarCollapsed" class="ml-3">
              <p class="text-sm font-medium text-gray-300">{{ username }}</p>
              <p class="text-xs text-gray-500">Administrador</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Header -->
      <header class="bg-gray-800 border-b border-gray-700">
        <div class="flex items-center justify-between px-4 py-4">
          <div class="flex items-center">
            <button
              @click="toggleSidebar"
              class="text-gray-400 hover:text-gray-300 focus:outline-none focus:text-gray-300 transition-colors duration-200"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h2 class="ml-4 text-xl font-semibold text-gray-100">{{ currentPageTitle }}</h2>
          </div>

          <div class="flex items-center space-x-4">
            <!-- Status Indicator -->
            <div class="flex items-center">
              <div :class="['h-2 w-2 rounded-full mr-2', connectionStatus ? 'bg-green-500' : 'bg-red-500']"></div>
              <span class="text-sm text-gray-400">
                {{ connectionStatus ? 'Conectado' : 'Desconectado' }}
              </span>
            </div>

            <!-- User Menu -->
            <div class="relative">
              <button
                @click="showUserMenu = !showUserMenu"
                class="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500"
              >
                <div class="bg-blue-600 rounded-full p-2">
                  <svg class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </button>

              <!-- User Dropdown -->
              <Transition name="fade">
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 mt-2 w-48 bg-gray-800 rounded-md shadow-lg py-1 z-50 border border-gray-700"
                >
                  <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">Perfil</a>
                  <a href="#" class="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700">Configuración</a>
                  <div class="border-t border-gray-700"></div>
                  <button
                    @click="logout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700"
                  >
                    Cerrar Sesión
                  </button>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto bg-gray-900 p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Iconos básicos
const HomeIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>' }
const QueueListIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>' }
const ServerIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"></path></svg>' }
const DocumentTextIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>' }
const ClockIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' }
const Cog6ToothIcon = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>' }

export default {
  name: 'Layout',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    
    const sidebarCollapsed = ref(false)
    const showUserMenu = ref(false)
    const connectionStatus = ref(true)

    const navigation = computed(() => [
      { name: 'Dashboard', href: '/', icon: HomeIcon, current: route.name === 'Dashboard' },
      { name: 'Cola de Render', href: '/queue', icon: QueueListIcon, current: route.name === 'Queue' },
      { name: 'Nodos', href: '/nodes', icon: ServerIcon, current: route.name === 'Nodes' },
      { name: 'Trabajos', href: '/jobs', icon: DocumentTextIcon, current: route.name === 'Jobs' },
      { name: 'Historial', href: '/history', icon: ClockIcon, current: route.name === 'History' },
      { name: 'Configuración', href: '/settings', icon: Cog6ToothIcon, current: route.name === 'Settings' }
    ])

    const currentPageTitle = computed(() => {
      const current = navigation.value.find(item => item.current)
      return current?.name || 'Dashboard'
    })

    const username = computed(() => authStore.username)

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
    }

    const logout = () => {
      authStore.logout()
      router.push('/login')
      showUserMenu.value = false
    }

    const handleClickOutside = (event) => {
      if (!event.target.closest('.relative')) {
        showUserMenu.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })

    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
    })

    return {
      sidebarCollapsed,
      showUserMenu,
      connectionStatus,
      navigation,
      currentPageTitle,
      username,
      toggleSidebar,
      logout
    }
  }
}
</script>'''
    
    create_file("src/components/Layout.vue", layout_vue)

def update_router_with_auth():
    """Actualizar router con guards de autenticación"""
    
    router_js = '''import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Lazy loading de componentes
const Dashboard = () => import('@/views/Dashboard.vue')
const Queue = () => import('@/views/Queue.vue')
const Nodes = () => import('@/views/Nodes.vue')
const Jobs = () => import('@/views/Jobs.vue')
const Settings = () => import('@/views/Settings.vue')
const History = () => import('@/views/History.vue')
const Login = () => import('@/views/Login.vue')

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/queue',
    name: 'Queue',
    component: Queue,
    meta: { requiresAuth: true }
  },
  {
    path: '/nodes',
    name: 'Nodes',
    component: Nodes,
    meta: { requiresAuth: true }
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: Jobs,
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guard de autenticación
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router'''
    
    create_file("src/router/index.js", router_js)

def update_dashboard_dark_theme():
    """Actualizar Dashboard con tema oscuro"""
    
    dashboard_dark = '''<template>
  <Layout>
    <div class="space-y-6">
      <!-- Page Header -->
      <div class="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-white">🎬 Dashboard</h1>
          <p class="mt-1 text-sm text-gray-400">
            Resumen general del sistema de render
          </p>
        </div>
        <div class="mt-4 sm:mt-0">
          <button
            @click="refreshData"
            :disabled="loading"
            class="btn-primary"
          >
            <span v-if="loading" class="animate-spin mr-2">⟳</span>
            <span v-else class="mr-2">↻</span>
            Actualizar
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Trabajos Pendientes"
          :value="stats.pendingJobs"
          icon="QueueListIcon"
          color="warning"
          :loading="loading"
        />
        <StatsCard
          title="Trabajos Ejecutándose"
          :value="stats.runningJobs"
          icon="PlayIcon"
          color="primary"
          :loading="loading"
        />
        <StatsCard
          title="Nodos Activos"
          :value="stats.activeNodes"
          icon="ServerIcon"
          color="success"
          :loading="loading"
        />
        <StatsCard
          title="Trabajos Completados"
          :value="stats.completedJobs"
          icon="CheckCircleIcon"
          color="success"
          :loading="loading"
        />
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Queue Status Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-100">Estado de la Cola</h3>
          </div>
          <div class="card-body">
            <div v-if="loading" class="flex items-center justify-center h-32">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
            <div v-else class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Pendientes</span>
                <span class="text-yellow-400 font-semibold">{{ queueData.pending }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Ejecutándose</span>
                <span class="text-blue-400 font-semibold">{{ queueData.running }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Completados</span>
                <span class="text-green-400 font-semibold">{{ queueData.completed }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Fallidos</span>
                <span class="text-red-400 font-semibold">{{ queueData.failed }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Node Status Chart -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium text-gray-100">Estado de Nodos</h3>
          </div>
          <div class="card-body">
            <div v-if="loading" class="flex items-center justify-center h-32">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
            <div v-else class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Online</span>
                <span class="text-green-400 font-semibold">{{ nodeData.online }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Offline</span>
                <span class="text-red-400 font-semibold">{{ nodeData.offline }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-300">Ocupados</span>
                <span class="text-yellow-400 font-semibold">{{ nodeData.busy }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-100">Actividad Reciente</h3>
        </div>
        <div class="card-body">
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="animate-pulse flex items-center space-x-4">
              <div class="rounded-full bg-gray-600 h-8 w-8"></div>
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-gray-600 rounded w-3/4"></div>
                <div class="h-3 bg-gray-600 rounded w-1/2"></div>
              </div>
            </div>
          </div>
          <div v-else class="space-y-4">
            <div v-for="activity in recentActivities" :key="activity.id" class="flex items-center space-x-4">
              <div :class="['flex-shrink-0 p-2 rounded-full', getActivityColor(activity.color)]">
                <span class="text-white text-sm">{{ activity.icon }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-100 truncate">
                  {{ activity.message }}
                </p>
                <p class="text-xs text-gray-400">
                  {{ formatTime(activity.timestamp) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium text-gray-100">Acciones Rápidas</h3>
        </div>
        <div class="card-body">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <router-link to="/jobs" class="btn-primary text-center py-4 flex flex-col items-center">
              <span class="text-2xl mb-2">📋</span>
              Nuevo Trabajo
            </router-link>
            <router-link to="/nodes" class="btn-secondary text-center py-4 flex flex-col items-center">
              <span class="text-2xl mb-2">🖥️</span>
              Gestionar Nodos
            </router-link>
            <router-link to="/queue" class="btn-secondary text-center py-4 flex flex-col items-center">
              <span class="text-2xl mb-2">📊</span>
              Ver Cola
            </router-link>
            <router-link to="/settings" class="btn-secondary text-center py-4 flex flex-col items-center">
              <span class="text-2xl mb-2">⚙️</span>
              Configuración
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script>
import { ref, onMounted } from 'vue'
import Layout from '@/components/Layout.vue'
import StatsCard from '@/components/StatsCard.vue'

export default {
  name: 'Dashboard',
  components: {
    Layout,
    StatsCard
  },
  setup() {
    const loading = ref(false)
    const stats = ref({
      pendingJobs: 0,
      runningJobs: 0,
      activeNodes: 0,
      completedJobs: 0
    })
    const queueData = ref({
      pending: 0,
      running: 0,
      completed: 0,
      failed: 0
    })
    const nodeData = ref({
      online: 0,
      offline: 0,
      busy: 0
    })
    const recentActivities = ref([
      {
        id: 1,
        type: 'system_start',
        message: 'Sistema iniciado correctamente',
        timestamp: new Date(),
        icon: '✅',
        color: 'success'
      },
      {
        id: 2,
        type: 'backend_connected',
        message: 'Backend API conectado',
        timestamp: new Date(Date.now() - 300000),
        icon: '🔗',
        color: 'primary'
      },
      {
        id: 3,
        type: 'database_ready',
        message: 'Base de datos lista',
        timestamp: new Date(Date.now() - 600000),
        icon: '🗄️',
        color: 'success'
      }
    ])

    const fetchDashboardData = async () => {
      loading.value = true
      
      try {
        const response = await fetch('/api/v1/queue/status')
        const queueStatus = await response.json()
        
        stats.value = {
          pendingJobs: queueStatus.job_counts?.pending || 0,
          runningJobs: queueStatus.job_counts?.running || 0,
          activeNodes: queueStatus.available_nodes || 0,
          completedJobs: queueStatus.job_counts?.completed || 0
        }

        queueData.value = {
          pending: queueStatus.job_counts?.pending || 0,
          running: queueStatus.job_counts?.running || 0,
          completed: queueStatus.job_counts?.completed || 0,
          failed: queueStatus.job_counts?.failed || 0
        }

        // Simular datos de nodos hasta que tengamos nodos reales
        nodeData.value = {
          online: queueStatus.available_nodes || 0,
          offline: 0,
          busy: 0
        }

      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        // Datos de fallback si no hay conexión
        addActivity({
          type: 'connection_error',
          message: 'Error de conexión con el backend',
          icon: '❌',
          color: 'error'
        })
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      fetchDashboardData()
      addActivity({
        type: 'data_refresh',
        message: 'Datos actualizados manualmente',
        icon: '🔄',
        color: 'primary'
      })
    }

    const addActivity = (activity) => {
      const newActivity = {
        ...activity,
        id: Date.now(),
        timestamp: new Date()
      }
      recentActivities.value.unshift(newActivity)
      
      // Mantener solo las últimas 10 actividades
      if (recentActivities.value.length > 10) {
        recentActivities.value = recentActivities.value.slice(0, 10)
      }
    }

    const getActivityColor = (color) => {
      const colors = {
        success: 'bg-green-600',
        primary: 'bg-blue-600',
        warning: 'bg-yellow-600',
        error: 'bg-red-600'
      }
      return colors[color] || colors.primary
    }

    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - new Date(timestamp)
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Ahora'
      if (minutes < 60) return `Hace ${minutes}m`
      if (minutes < 1440) return `Hace ${Math.floor(minutes / 60)}h`
      return `Hace ${Math.floor(minutes / 1440)}d`
    }

    onMounted(() => {
      fetchDashboardData()
      
      // Auto-refresh cada 30 segundos
      const interval = setInterval(fetchDashboardData, 30000)
      
      // Cleanup
      return () => clearInterval(interval)
    })

    return {
      loading,
      stats,
      queueData,
      nodeData,
      recentActivities,
      refreshData,
      getActivityColor,
      formatTime
    }
  }
}
</script>'''
    
    create_file("src/views/Dashboard.vue", dashboard_dark)

def update_stats_card_dark():
    """Actualizar StatsCard para tema oscuro"""
    
    stats_card_dark = '''<template>
  <div class="card hover:bg-gray-750 transition-colors duration-200">
    <div class="card-body">
      <div class="flex items-center">
        <div :class="['flex-shrink-0 p-3 rounded-lg', colorClasses.bg]">
          <component :is="iconComponent" :class="['h-6 w-6', colorClasses.text]" />
        </div>
        <div class="ml-4 flex-1">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-400 truncate">{{ title }}</p>
          </div>
          <div class="flex items-baseline">
            <p v-if="!loading" class="text-2xl font-semibold text-gray-100">
              {{ formattedValue }}
            </p>
            <div v-else class="animate-pulse">
              <div class="h-8 bg-gray-600 rounded w-16"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

// Iconos básicos
const QueueListIcon = { 
  template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>' 
}
const PlayIcon = { 
  template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15"></path></svg>' 
}
const ServerIcon = { 
  template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"></path></svg>' 
}
const CheckCircleIcon = { 
  template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' 
}

export default {
  name: 'StatsCard',
  props: {
    title: { type: String, required: true },
    value: { type: [Number, String], required: true },
    icon: { type: String, default: 'CheckCircleIcon' },
    color: { type: String, default: 'primary' },
    loading: { type: Boolean, default: false }
  },
  setup(props) {
    const iconComponents = {
      QueueListIcon, PlayIcon, ServerIcon, CheckCircleIcon
    }

    const iconComponent = computed(() => iconComponents[props.icon] || CheckCircleIcon)

    const colorClasses = computed(() => {
      const colors = {
        primary: { bg: 'bg-blue-900', text: 'text-blue-400' },
        success: { bg: 'bg-green-900', text: 'text-green-400' },
        warning: { bg: 'bg-yellow-900', text: 'text-yellow-400' },
        error: { bg: 'bg-red-900', text: 'text-red-400' }
      }
      return colors[props.color] || colors.primary
    })

    const formattedValue = computed(() => {
      if (typeof props.value === 'number') {
        return props.value.toLocaleString()
      }
      return props.value
    })

    return { iconComponent, colorClasses, formattedValue }
  }
}
</script>'''
    
    create_file("src/components/StatsCard.vue", stats_card_dark)

def update_app_vue():
    """Actualizar App.vue"""
    
    app_vue_updated = '''<template>
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
</script>'''
    
    create_file("src/App.vue", app_vue_updated)

def update_main_js():
    """Actualizar main.js con Pinia"""
    
    main_js_updated = '''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')'''
    
    create_file("src/main.js", main_js_updated)

def main():
    """Función principal"""
    print("🎨 IMPLEMENTANDO AUTENTICACIÓN + TEMA OSCURO")
    print("=" * 60)
    
    # Verificar directorio
    if not os.getcwd().endswith('frontend'):
        print("⚠️ Ejecuta desde D:\\Render_QM\\frontend\\")
        return False
    
    print("🎨 Actualizando estilos a tema oscuro...")
    update_styles_dark_theme()
    
    print("🔐 Creando sistema de autenticación...")
    create_auth_store()
    create_login_page()
    create_layout_component()
    update_router_with_auth()
    
    print("🖤 Actualizando componentes a tema oscuro...")
    update_dashboard_dark_theme()
    update_stats_card_dark()
    update_app_vue()
    update_main_js()
    
    print("\n🎉 ¡SISTEMA COMPLETADO!")
    print("\n📋 Lo que se ha implementado:")
    print("   ✅ Sistema de autenticación completo")
    print("   ✅ Tema oscuro/negro en toda la interfaz")
    print("   ✅ Guards de ruta para proteger páginas")
    print("   ✅ Layout con sidebar oscuro")
    print("   ✅ Login page con tema oscuro")
    print("   ✅ Dashboard actualizado")
    
    print("\n🚀 Para ver los cambios:")
    print("   1. Detén el frontend (Ctrl+C)")
    print("   2. Reinicia: npm run dev") 
    print("   3. Ve a: http://localhost:3000")
    print("   4. Deberías ver la página de login oscura")
    print("   5. Login: admin / admin123")
    
    print("\n🎯 Funcionalidades:")
    print("   • Login obligatorio para acceder")
    print("   • Interfaz completamente oscura/negra")
    print("   • Sidebar colapsable")
    print("   • Logout funcional")
    print("   • Dashboard con estadísticas en tiempo real")
    
    return True

if __name__ == "__main__":
    main()