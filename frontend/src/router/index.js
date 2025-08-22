import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'

// Lazy loading solo para las vistas que sabemos que existen
const Queue = () => import('@/views/Queue.vue')
const Nodes = () => import('@/views/Nodes.vue')
const Jobs = () => import('@/views/Jobs.vue')
const History = () => import('@/views/History.vue')
const Settings = () => import('@/views/Settings.vue')

const routes = [
  // Ruta raíz - Redirige al dashboard
  {
    path: '/',
    redirect: '/dashboard'
  },
  // Dashboard Principal
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'Dashboard - Render Queue Manager'
    }
  },
  // Otras rutas básicas
  {
    path: '/queue',
    name: 'Queue',
    component: Queue,
    meta: {
      title: 'Cola de Trabajos'
    }
  },
  {
    path: '/nodes',
    name: 'Nodes',
    component: Nodes,
    meta: {
      title: 'Nodos de Render'
    }
  },
  {
    path: '/jobs',
    name: 'Jobs',
    component: Jobs,
    meta: {
      title: 'Trabajos'
    }
  },
  {
    path: '/history',
    name: 'History',
    component: History,
    meta: {
      title: 'Historial'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: 'Configuración'
    }
  },
  // Catch all para páginas no encontradas
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Actualizar título de la página
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router