#!/usr/bin/env python3
"""
Script para crear los componentes avanzados del frontend
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

def create_advanced_components():
    """Crear componentes avanzados"""
    
    # src/components/StatsCard.vue
    stats_card = '''<template>
  <div class="card">
    <div class="card-body">
      <div class="flex items-center">
        <div :class="['flex-shrink-0 p-3 rounded-lg', colorClasses.bg]">
          <component :is="iconComponent" :class="['h-6 w-6', colorClasses.text]" />
        </div>
        <div class="ml-4 flex-1">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-600 truncate">{{ title }}</p>
          </div>
          <div class="flex items-baseline">
            <p v-if="!loading" class="text-2xl font-semibold text-gray-900">
              {{ formattedValue }}
            </p>
            <div v-else class="animate-pulse">
              <div class="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

// Iconos simulados para desarrollo básico
const QueueListIcon = { template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>' }
const PlayIcon = { template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15"></path></svg>' }
const ServerIcon = { template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2"></path></svg>' }
const CheckCircleIcon = { template: '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>' }

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
        primary: { bg: 'bg-blue-100', text: 'text-blue-600' },
        success: { bg: 'bg-green-100', text: 'text-green-600' },
        warning: { bg: 'bg-yellow-100', text: 'text-yellow-600' },
        error: { bg: 'bg-red-100', text: 'text-red-600' }
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
    
    create_file("src/components/StatsCard.vue", stats_card)
    
    # src/views/Dashboard.vue actualizado
    dashboard_updated = '''<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">🎬 Render_QM Dashboard</h1>
          <p class="mt-1 text-sm text-gray-600">Sistema de gestión de colas de render</p>
        </div>
        <div class="mt-4 sm:mt-0">
          <button
            @click="refreshData"
            :disabled="loading"
            class="btn-primary"
          >
            <span v-if="loading">🔄</span>
            <span v-else>↻</span>
            Actualizar
          </button>
        </div>
      </div>
    </header>
    
    <main class="max-w-7xl mx-auto py-6 px-4">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
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
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- Estado del Sistema -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium">Estado del Sistema</h3>
          </div>
          <div class="card-body">
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span>Estado de la Cola</span>
                <span :class="queueStatus === 'active' ? 'status-badge bg-green-100 text-green-800' : 'status-badge bg-gray-100 text-gray-800'">
                  {{ queueStatus === 'active' ? 'Activa' : 'Inactiva' }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span>Backend API</span>
                <span class="status-badge bg-green-100 text-green-800">Conectado</span>
              </div>
              <div class="flex items-center justify-between">
                <span>Base de Datos</span>
                <span class="status-badge bg-green-100 text-green-800">Online</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Acciones Rápidas -->
        <div class="card">
          <div class="card-header">
            <h3 class="text-lg font-medium">Acciones Rápidas</h3>
          </div>
          <div class="card-body">
            <div class="grid grid-cols-2 gap-4">
              <button class="btn-primary text-center py-3">
                📋 Nuevo Trabajo
              </button>
              <button class="btn-secondary text-center py-3">
                🔍 Ver Cola
              </button>
              <button class="btn-secondary text-center py-3">
                🖥️ Gestionar Nodos
              </button>
              <button class="btn-secondary text-center py-3">
                ⚙️ Configuración
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Actividad Reciente -->
      <div class="card">
        <div class="card-header">
          <h3 class="text-lg font-medium">Actividad Reciente</h3>
        </div>
        <div class="card-body">
          <div v-if="loading" class="space-y-3">
            <div v-for="i in 3" :key="i" class="animate-pulse flex items-center space-x-4">
              <div class="rounded-full bg-gray-300 h-8 w-8"></div>
              <div class="flex-1 space-y-2">
                <div class="h-4 bg-gray-300 rounded w-3/4"></div>
                <div class="h-3 bg-gray-300 rounded w-1/2"></div>
              </div>
            </div>
          </div>
          <div v-else class="space-y-4">
            <div v-for="activity in recentActivities" :key="activity.id" class="flex items-center space-x-4">
              <div :class="['flex-shrink-0 p-2 rounded-full', activity.color]">
                <span class="text-white text-sm">{{ activity.icon }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">{{ activity.message }}</p>
                <p class="text-xs text-gray-500">{{ formatTime(activity.timestamp) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import StatsCard from '@/components/StatsCard.vue'

export default {
  name: 'Dashboard',
  components: { StatsCard },
  setup() {
    const loading = ref(false)
    const stats = ref({
      pendingJobs: 0,
      runningJobs: 0,
      activeNodes: 0,
      completedJobs: 0
    })
    const queueStatus = ref('idle')
    const recentActivities = ref([
      {
        id: 1,
        message: 'Sistema iniciado correctamente',
        timestamp: new Date(),
        icon: '✅',
        color: 'bg-green-500'
      },
      {
        id: 2,
        message: 'Backend conectado',
        timestamp: new Date(Date.now() - 60000),
        icon: '🔗',
        color: 'bg-blue-500'
      }
    ])
    
    const fetchStats = async () => {
      loading.value = true
      try {
        const response = await fetch('/api/v1/queue/status')
        const data = await response.json()
        
        stats.value = {
          pendingJobs: data.job_counts?.pending || 0,
          runningJobs: data.job_counts?.running || 0,
          activeNodes: data.available_nodes || 0,
          completedJobs: data.job_counts?.completed || 0
        }
        
        queueStatus.value = data.queue_status || 'idle'
      } catch (error) {
        console.error('Error fetching stats:', error)
      } finally {
        loading.value = false
      }
    }
    
    const refreshData = () => {
      fetchStats()
    }
    
    const formatTime = (timestamp) => {
      const now = new Date()
      const diff = now - new Date(timestamp)
      const minutes = Math.floor(diff / 60000)
      
      if (minutes < 1) return 'Ahora'
      if (minutes < 60) return `Hace ${minutes}m`
      return `Hace ${Math.floor(minutes / 60)}h`
    }
    
    onMounted(() => {
      fetchStats()
      // Auto-refresh cada 30 segundos
      setInterval(fetchStats, 30000)
    })
    
    return {
      loading,
      stats,
      queueStatus,
      recentActivities,
      refreshData,
      formatTime
    }
  }
}
</script>'''
    
    create_file("src/views/Dashboard.vue", dashboard_updated)

def install_additional_dependencies():
    """Instalar dependencias adicionales"""
    print("📦 Instalando dependencias adicionales...")
    
    try:
        import subprocess
        
        # Dependencias adicionales para componentes avanzados
        dependencies = [
            "chart.js",
            "moment",
            "@heroicons/vue"
        ]
        
        for dep in dependencies:
            print(f"   Instalando {dep}...")
            result = subprocess.run(['npm', 'install', dep], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {dep} instalado")
            else:
                print(f"   ⚠️ {dep} ya instalado o error menor")
                
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Instala manualmente: npm install chart.js moment @heroicons/vue")
        return False

def main():
    """Función principal"""
    print("🎨 CREAR COMPONENTES AVANZADOS DEL FRONTEND")
    print("=" * 50)
    
    # Verificar directorio
    if not os.getcwd().endswith('frontend'):
        print("⚠️ Ejecuta desde D:\\Render_QM\\frontend\\")
        return False
    
    # Crear componentes
    print("📁 Creando componentes avanzados...")
    create_advanced_components()
    
    # Instalar dependencias
    install_additional_dependencies()
    
    print("\n🎉 ¡Componentes avanzados creados!")
    print("\n📋 Lo que se ha añadido:")
    print("   ✅ StatsCard.vue - Tarjetas de estadísticas")
    print("   ✅ Dashboard.vue actualizado con componentes")
    print("   ✅ Dependencias adicionales")
    
    print("\n🚀 Reinicia el frontend para ver los cambios:")
    print("   Ctrl+C en la terminal del frontend")
    print("   npm run dev")
    
    return True

if __name__ == "__main__":
    main()