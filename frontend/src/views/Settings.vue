<template>
  <div class="min-h-screen bg-gray-900 p-6">
    <div class="max-w-7xl mx-auto">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-3xl font-bold text-white flex items-center">
          ⚙️ Configuración del Sistema
        </h1>
        <div class="flex space-x-3">
          <button @click="saveAllSettings" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
            💾 Guardar Todo
          </button>
          <button @click="resetToDefaults" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg">
            🔄 Restaurar Defaults
          </button>
        </div>
      </div>

      <!-- Navegación de pestañas -->
      <div class="bg-gray-800 rounded-lg p-1 mb-6">
        <nav class="flex space-x-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all"
            :class="activeTab === tab.id 
              ? 'bg-blue-600 text-white' 
              : 'text-gray-300 hover:text-white hover:bg-gray-700'"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Contenido de las pestañas -->
      <div class="space-y-6">
        
        <!-- Configuración General -->
        <div v-show="activeTab === 'general'" class="space-y-6">
          <div class="bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-semibold text-white mb-4">🔧 Configuración General</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Configuración del Sistema -->
              <div class="space-y-4">
                <h4 class="text-lg font-medium text-white">Sistema</h4>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Nombre del Sistema
                  </label>
                  <input
                    v-model="settings.general.systemName"
                    type="text"
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Puerto del Servidor
                  </label>
                  <input
                    v-model.number="settings.general.serverPort"
                    type="number"
                    min="1000"
                    max="65535"
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Idioma
                  </label>
                  <select
                    v-model="settings.general.language"
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="es">Español</option>
                    <option value="en">English</option>
                    <option value="fr">Français</option>
                  </select>
                </div>
                
                <div class="flex items-center">
                  <input
                    v-model="settings.general.autoStart"
                    type="checkbox"
                    id="autoStart"
                    class="mr-2"
                  />
                  <label for="autoStart" class="text-gray-300">
                    Iniciar automáticamente con el sistema
                  </label>
                </div>
              </div>
              
              <!-- Configuración de Render -->
              <div class="space-y-4">
                <h4 class="text-lg font-medium text-white">Render</h4>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Directorio de Salida por Defecto
                  </label>
                  <div class="flex">
                    <input
                      v-model="settings.general.outputDir"
                      type="text"
                      class="flex-1 bg-gray-700 border border-gray-600 rounded-l-lg px-3 py-2 text-white"
                    />
                    <button class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-r-lg">
                      📁
                    </button>
                  </div>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Motor de Render por Defecto
                  </label>
                  <select
                    v-model="settings.general.defaultEngine"
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  >
                    <option value="cycles">Cycles</option>
                    <option value="eevee">Eevee</option>
                    <option value="workbench">Workbench</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-300 mb-2">
                    Trabajos Simultáneos Máximos
                  </label>
                  <input
                    v-model.number="settings.general.maxJobs"
                    type="number"
                    min="1"
                    max="20"
                    class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                  />
                </div>
                
                <div class="flex items-center">
                  <input
                    v-model="settings.general.autoCleanup"
                    type="checkbox"
                    id="autoCleanup"
                    class="mr-2"
                  />
                  <label for="autoCleanup" class="text-gray-300">
                    Limpiar archivos temporales automáticamente
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Configuración de Blender -->
        <div v-show="activeTab === 'blender'" class="space-y-6">
          <BlenderConfig @config-updated="handleBlenderConfigUpdate" />
        </div>

        <!-- Configuración de Notificaciones -->
        <div v-show="activeTab === 'notifications'" class="space-y-6">
          <!-- ... contenido notificaciones existente ... -->
        </div>

        <!-- Configuración de Notificaciones -->
        <div v-show="activeTab === 'notifications'" class="space-y-6">
          <div class="bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-semibold text-white mb-4">🔔 Configuración de Notificaciones</h3>
            
            <div class="space-y-6">
              <!-- Estado General -->
              <div class="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h4 class="text-lg font-medium text-white">Notificaciones Habilitadas</h4>
                  <p class="text-gray-400">Activar o desactivar todas las notificaciones</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="settings.notifications.enabled"
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
              
              <!-- Tipos de Notificaciones -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  v-for="type in notificationTypes"
                  :key="type.id"
                  class="bg-gray-700 rounded-lg p-4"
                >
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center">
                      <span class="text-2xl mr-3">{{ type.icon }}</span>
                      <div>
                        <h5 class="text-white font-medium">{{ type.name }}</h5>
                        <p class="text-gray-400 text-sm">{{ type.description }}</p>
                      </div>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        v-model="type.enabled"
                        :disabled="!settings.notifications.enabled"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600 peer-disabled:opacity-50"></div>
                    </label>
                  </div>
                  
                  <div v-if="type.enabled && settings.notifications.enabled" class="space-y-2">
                    <div v-if="type.options">
                      <label class="block text-xs text-gray-400 mb-1">{{ type.options.label }}</label>
                      <select
                        v-model="type.options.value"
                        class="w-full bg-gray-600 border border-gray-500 rounded px-2 py-1 text-white text-sm"
                      >
                        <option v-for="opt in type.options.choices" :key="opt.value" :value="opt.value">
                          {{ opt.label }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Configuración de Email -->
              <div class="bg-gray-700 rounded-lg p-4">
                <h4 class="text-lg font-medium text-white mb-4">📧 Notificaciones por Email</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                      Servidor SMTP
                    </label>
                    <input
                      v-model="settings.notifications.email.server"
                      type="text"
                      class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                      placeholder="smtp.gmail.com"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                      Puerto
                    </label>
                    <input
                      v-model.number="settings.notifications.email.port"
                      type="number"
                      class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                      Email
                    </label>
                    <input
                      v-model="settings.notifications.email.username"
                      type="email"
                      class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-300 mb-2">
                      Contraseña
                    </label>
                    <input
                      v-model="settings.notifications.email.password"
                      type="password"
                      class="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gestión de Usuarios -->
        <div v-show="activeTab === 'users'" class="space-y-6">
          <div class="bg-gray-800 rounded-lg p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-xl font-semibold text-white">👥 Gestión de Usuarios</h3>
              <button @click="showAddUserModal = true" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                ➕ Nuevo Usuario
              </button>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-750">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Usuario</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Rol</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Estado</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Último Acceso</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-700">
                  <tr v-for="user in users" :key="user.id" class="hover:bg-gray-750">
                    <td class="px-6 py-4">
                      <div class="flex items-center">
                        <div class="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                          <span class="text-white font-medium">{{ user.name.charAt(0) }}</span>
                        </div>
                        <div class="ml-4">
                          <div class="text-white font-medium">{{ user.name }}</div>
                          <div class="text-gray-400 text-sm">{{ user.email }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <span class="px-2 py-1 rounded-full text-xs font-medium"
                            :class="getRoleClass(user.role)">
                        {{ getRoleText(user.role) }}
                      </span>
                    </td>
                    <td class="px-6 py-4">
                      <span class="px-2 py-1 rounded-full text-xs font-medium"
                            :class="user.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                        {{ user.active ? 'Activo' : 'Inactivo' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 text-gray-300">{{ formatDate(user.lastLogin) }}</td>
                    <td class="px-6 py-4">
                      <div class="flex space-x-2">
                        <button @click="editUser(user)" class="text-blue-400 hover:text-blue-300">✏️</button>
                        <button @click="toggleUser(user)" class="text-yellow-400 hover:text-yellow-300">
                          {{ user.active ? '⏸️' : '▶️' }}
                        </button>
                        <button @click="deleteUser(user)" class="text-red-400 hover:text-red-300">🗑️</button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Sistema -->
        <div v-show="activeTab === 'system'" class="space-y-6">
          <div class="bg-gray-800 rounded-lg p-6">
            <h3 class="text-xl font-semibold text-white mb-4">💻 Información del Sistema</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Estado del Sistema -->
              <div class="space-y-4">
                <h4 class="text-lg font-medium text-white">Estado</h4>
                <div class="space-y-3">
                  <div class="flex justify-between items-center p-3 bg-gray-700 rounded">
                    <span class="text-gray-300">API Backend</span>
                    <span class="px-2 py-1 bg-green-500 text-white rounded text-sm">✅ Online</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-gray-700 rounded">
                    <span class="text-gray-300">Base de Datos</span>
                    <span class="px-2 py-1 bg-green-500 text-white rounded text-sm">✅ Conectada</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-gray-700 rounded">
                    <span class="text-gray-300">Cola de Render</span>
                    <span class="px-2 py-1 bg-green-500 text-white rounded text-sm">✅ Funcionando</span>
                  </div>
                  <div class="flex justify-between items-center p-3 bg-gray-700 rounded">
                    <span class="text-gray-300">Espacio en Disco</span>
                    <span class="px-2 py-1 bg-yellow-500 text-white rounded text-sm">⚠️ 85% Usado</span>
                  </div>
                </div>
              </div>
              
              <!-- Información Técnica -->
              <div class="space-y-4">
                <h4 class="text-lg font-medium text-white">Información Técnica</h4>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-400">Versión:</span>
                    <span class="text-white">{{ systemInfo.version }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Uptime:</span>
                    <span class="text-white">{{ systemInfo.uptime }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">CPU:</span>
                    <span class="text-white">{{ systemInfo.cpu }}%</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">RAM:</span>
                    <span class="text-white">{{ systemInfo.memory }}GB</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-400">Disco:</span>
                    <span class="text-white">{{ systemInfo.disk }}GB</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Acciones del Sistema -->
            <div class="mt-6 pt-6 border-t border-gray-700">
              <h4 class="text-lg font-medium text-white mb-4">Acciones del Sistema</h4>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <button @click="restartSystem" class="bg-yellow-600 hover:bg-yellow-700 text-white p-3 rounded-lg">
                  🔄 Reiniciar Sistema
                </button>
                <button @click="backupSystem" class="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg">
                  💾 Crear Backup
                </button>
                <button @click="updateSystem" class="bg-green-600 hover:bg-green-700 text-white p-3 rounded-lg">
                  ⬆️ Buscar Actualizaciones
                </button>
                <button @click="exportLogs" class="bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-lg">
                  📄 Exportar Logs
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal para Nuevo Usuario -->
      <div v-if="showAddUserModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-white">👤 Nuevo Usuario</h3>
              <button @click="showAddUserModal = false" class="text-gray-400 hover:text-white">✖️</button>
            </div>
            
            <form @submit.prevent="addUser" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Nombre</label>
                <input
                  v-model="newUser.name"
                  type="text"
                  required
                  class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Email</label>
                <input
                  v-model="newUser.email"
                  type="email"
                  required
                  class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">Rol</label>
                <select
                  v-model="newUser.role"
                  class="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white"
                >
                  <option value="viewer">Viewer</option>
                  <option value="operator">Operator</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div class="flex justify-end space-x-3 pt-4">
                <button type="button" @click="showAddUserModal = false" class="px-4 py-2 text-gray-300 hover:text-white">
                  Cancelar
                </button>
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                  Crear Usuario
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      activeTab: 'general',
      showAddUserModal: false,
      
      tabs: [
        { id: 'general', name: 'General', icon: '🔧' },
        { id: 'blender', name: 'Blender', icon: '🎨' },
        { id: 'notifications', name: 'Notificaciones', icon: '🔔' },
        { id: 'users', name: 'Usuarios', icon: '👥' },
        { id: 'system', name: 'Sistema', icon: '💻' }        
      ],
      
      settings: {
        general: {
          systemName: 'Render Queue Manager',
          serverPort: 8000,
          language: 'es',
          autoStart: true,
          outputDir: 'C:\\RenderOutput',
          defaultEngine: 'cycles',
          maxJobs: 5,
          autoCleanup: true
        },
        notifications: {
          enabled: true,
          email: {
            server: 'smtp.gmail.com',
            port: 587,
            username: '',
            password: ''
          }
        }
      },
      
      notificationTypes: [
        {
          id: 'job_complete',
          name: 'Trabajo Completado',
          description: 'Cuando un trabajo se completa',
          icon: '✅',
          enabled: true,
          options: {
            label: 'Prioridad mínima',
            value: 'normal',
            choices: [
              { value: 'low', label: 'Baja' },
              { value: 'normal', label: 'Normal' },
              { value: 'high', label: 'Alta' }
            ]
          }
        },
        {
          id: 'job_failed',
          name: 'Trabajo Fallido',
          description: 'Cuando un trabajo falla',
          icon: '❌',
          enabled: true
        },
        {
          id: 'node_offline',
          name: 'Nodo Desconectado',
          description: 'Cuando un nodo se desconecta',
          icon: '🖥️',
          enabled: true
        },
        {
          id: 'system_alert',
          name: 'Alertas del Sistema',
          description: 'Alertas de recursos y sistema',
          icon: '⚠️',
          enabled: false
        }
      ],
      
      users: [
        {
          id: 1,
          name: 'Admin Principal',
          email: 'admin@renderqueue.com',
          role: 'admin',
          active: true,
          lastLogin: new Date(Date.now() - 3600000)
        },
        {
          id: 2,
          name: 'Operador Render',
          email: 'operator@renderqueue.com',
          role: 'operator',
          active: true,
          lastLogin: new Date(Date.now() - 7200000)
        },
        {
          id: 3,
          name: 'Usuario Viewer',
          email: 'viewer@renderqueue.com',
          role: 'viewer',
          active: false,
          lastLogin: new Date(Date.now() - 86400000)
        }
      ],
      
      newUser: {
        name: '',
        email: '',
        role: 'viewer'
      },
      
      systemInfo: {
        version: '1.0.0',
        uptime: '5d 12h 30m',
        cpu: 45,
        memory: 8.2,
        disk: 125.6
      }
    }
  },
  
  methods: {
    saveAllSettings() {
      alert('⚙️ Configuración guardada exitosamente')
    },
    
    resetToDefaults() {
      if (confirm('¿Restaurar toda la configuración a valores por defecto?')) {
        alert('🔄 Configuración restaurada')
      }
    },
    
    getRoleClass(role) {
      const classes = {
        admin: 'bg-red-100 text-red-800',
        operator: 'bg-blue-100 text-blue-800',
        viewer: 'bg-gray-100 text-gray-800'
      }
      return classes[role] || 'bg-gray-100 text-gray-800'
    },
    
    getRoleText(role) {
      const texts = {
        admin: 'Administrador',
        operator: 'Operador',
        viewer: 'Viewer'
      }
      return texts[role] || role
    },
    
    formatDate(date) {
      return date.toLocaleDateString('es-ES') + ' ' + date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    },
    
    editUser(user) {
      alert(`Editar usuario: ${user.name}`)
    },
    
    toggleUser(user) {
      user.active = !user.active
      alert(`Usuario ${user.name} ${user.active ? 'activado' : 'desactivado'}`)
    },
    
    deleteUser(user) {
      if (confirm(`¿Eliminar usuario ${user.name}?`)) {
        const index = this.users.findIndex(u => u.id === user.id)
        if (index > -1) {
          this.users.splice(index, 1)
        }
      }
    },
    
    addUser() {
      const user = {
        id: Date.now(),
        name: this.newUser.name,
        email: this.newUser.email,
        role: this.newUser.role,
        active: true,
        lastLogin: new Date()
      }
      
      this.users.push(user)
      this.newUser = { name: '', email: '', role: 'viewer' }
      this.showAddUserModal = false
      alert(`Usuario ${user.name} creado exitosamente`)
    },
    
    restartSystem() {
      if (confirm('⚠️ ¿Reiniciar el sistema? Esto detendrá todos los trabajos en progreso.')) {
        alert('🔄 Reiniciando sistema...')
      }
    },
    
    backupSystem() {
      alert('💾 Creando backup del sistema...')
    },
    
    updateSystem() {
      alert('⬆️ Buscando actualizaciones...')
    },
    
    exportLogs() {
      alert('📄 Exportando logs del sistema...')
    },

    // AGREGAR ESTE MÉTODO AQUÍ ↓
    handleBlenderConfigUpdate(configData) {
      console.log('Configuración de Blender actualizada:', configData)
      
      // Emitir evento al dashboard principal
      this.$emit('blender-config-updated', configData)
      
      // Mostrar notificación
      this.showSuccess('Configuración de Blender actualizada correctamente')
    },
    showSuccess(message) {
      alert(`✅ ${message}`)
    }
  }
}
</script>

<style scoped>
.bg-gray-750 {
  background-color: #2a2e3a;
}
</style>