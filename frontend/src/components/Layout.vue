<template>
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
</script>