<template>
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
</script>