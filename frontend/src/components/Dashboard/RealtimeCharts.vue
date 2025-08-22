<template>
  <div class="space-y-6">
    <!-- Métricas en Tiempo Real -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Gráfico de Rendimiento del Sistema -->
      <div class="bg-gray-800 rounded-lg shadow-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            Rendimiento del Sistema
          </h3>
          <div class="flex items-center space-x-2">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">CPU</span>
            </div>
            <div class="flex items-center">
              <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">RAM</span>
            </div>
            <div class="flex items-center">
              <div class="w-3 h-3 bg-purple-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">GPU</span>
            </div>
          </div>
        </div>
        
        <div class="h-64">
          <canvas ref="performanceChart" class="w-full h-full"></canvas>
        </div>
        
        <!-- Valores Actuales -->
        <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-700">
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-400">{{ currentMetrics.cpu }}%</div>
            <div class="text-sm text-gray-400">CPU Promedio</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-400">{{ currentMetrics.memory }}%</div>
            <div class="text-sm text-gray-400">RAM Promedio</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-purple-400">{{ currentMetrics.gpu }}%</div>
            <div class="text-sm text-gray-400">GPU Promedio</div>
          </div>
        </div>
      </div>

      <!-- Gráfico de Cola de Trabajos -->
      <div class="bg-gray-800 rounded-lg shadow-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <svg class="w-5 h-5 mr-2 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            Cola de Trabajos
          </h3>
          <div class="flex items-center space-x-2">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">En Cola</span>
            </div>
            <div class="flex items-center">
              <div class="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Procesando</span>
            </div>
            <div class="flex items-center">
              <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Completados</span>
            </div>
          </div>
        </div>
        
        <div class="h-64">
          <canvas ref="queueChart" class="w-full h-full"></canvas>
        </div>
        
        <!-- Estadísticas de Cola -->
        <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-700">
          <div class="text-center">
            <div class="text-2xl font-bold text-yellow-400">{{ queueStats.pending }}</div>
            <div class="text-sm text-gray-400">En Cola</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-400">{{ queueStats.processing }}</div>
            <div class="text-sm text-gray-400">Procesando</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-green-400">{{ queueStats.completed }}</div>
            <div class="text-sm text-gray-400">Completados Hoy</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Gráficos de Análisis Detallado -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <!-- Distribución de Nodos -->
      <div class="bg-gray-800 rounded-lg shadow-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <svg class="w-5 h-5 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
            </svg>
            Estado de Nodos
          </h3>
          <select
            v-model="nodeChartType"
            class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1 text-white text-sm focus:border-blue-500"
          >
            <option value="doughnut">Circular</option>
            <option value="bar">Barras</option>
          </select>
        </div>
        
        <div class="h-64 flex items-center justify-center">
          <canvas ref="nodesChart" class="max-w-full max-h-full"></canvas>
        </div>
        
        <!-- Leyenda de Nodos -->
        <div class="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-700">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Activos</span>
            </div>
            <span class="text-white font-medium">{{ nodeStats.active }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Inactivos</span>
            </div>
            <span class="text-white font-medium">{{ nodeStats.inactive }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Renderizando</span>
            </div>
            <span class="text-white font-medium">{{ nodeStats.rendering }}</span>
          </div>
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-gray-500 rounded-full mr-2"></div>
              <span class="text-sm text-gray-400">Error</span>
            </div>
            <span class="text-white font-medium">{{ nodeStats.error }}</span>
          </div>
        </div>
      </div>

      <!-- Tiempo de Render Promedio -->
      <div class="bg-gray-800 rounded-lg shadow-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-semibold text-white flex items-center">
            <svg class="w-5 h-5 mr-2 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
            Tiempo de Render
          </h3>
          <select
            v-model="renderTimeRange"
            @change="updateRenderTimeChart"
            class="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1 text-white text-sm focus:border-blue-500"
          >
            <option value="24h">Últimas 24h</option>
            <option value="7d">Última semana</option>
            <option value="30d">Último mes</option>
          </select>
        </div>
        
        <div class="h-64">
          <canvas ref="renderTimeChart" class="w-full h-full"></canvas>
        </div>
        
        <!-- Métricas de Tiempo -->
        <div class="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-700">
          <div class="text-center">
            <div class="text-2xl font-bold text-orange-400">{{ renderMetrics.average }}min</div>
            <div class="text-sm text-gray-400">Promedio</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-400">{{ renderMetrics.fastest }}min</div>
            <div class="text-sm text-gray-400">Más Rápido</div>
          </div>
          <div class="text-center">
            <div class="text-2xl font-bold text-red-400">{{ renderMetrics.slowest }}min</div>
            <div class="text-sm text-gray-400">Más Lento</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Throughput y Productividad -->
    <div class="bg-gray-800 rounded-lg shadow-xl p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-xl font-semibold text-white flex items-center">
          <svg class="w-5 h-5 mr-2 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
          </svg>
          Productividad del Sistema
        </h3>
        
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-indigo-500 rounded-full"></div>
            <span class="text-sm text-gray-400">Frames/Hora</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 bg-cyan-500 rounded-full"></div>
            <span class="text-sm text-gray-400">Trabajos/Día</span>
          </div>
          <button
            @click="refreshCharts"
            class="text-gray-400 hover:text-white transition-colors"
            title="Actualizar gráficos"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="h-80">
        <canvas ref="productivityChart" class="w-full h-full"></canvas>
      </div>
      
      <!-- Estadísticas de Productividad -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-6 pt-6 border-t border-gray-700">
        <div class="text-center">
          <div class="text-3xl font-bold text-indigo-400">{{ productivity.framesPerHour }}</div>
          <div class="text-sm text-gray-400">Frames/Hora</div>
          <div class="text-xs text-gray-500 mt-1">↑ 12% vs ayer</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-cyan-400">{{ productivity.jobsPerDay }}</div>
          <div class="text-sm text-gray-400">Trabajos/Día</div>
          <div class="text-xs text-gray-500 mt-1">↑ 8% vs ayer</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-green-400">{{ productivity.efficiency }}%</div>
          <div class="text-sm text-gray-400">Eficiencia</div>
          <div class="text-xs text-gray-500 mt-1">↑ 5% vs ayer</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-yellow-400">{{ productivity.uptime }}%</div>
          <div class="text-sm text-gray-400">Tiempo Activo</div>
          <div class="text-xs text-gray-500 mt-1">↓ 2% vs ayer</div>
        </div>
      </div>
    </div>

    <!-- Estado de Conexión -->
    <div class="fixed bottom-4 right-4 z-50">
      <div
        class="bg-gray-800 rounded-lg shadow-xl p-3 flex items-center space-x-2 border"
        :class="isConnected ? 'border-green-500' : 'border-red-500'"
      >
        <div
          class="w-3 h-3 rounded-full"
          :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
        ></div>
        <span class="text-sm text-white">
          {{ isConnected ? 'Datos en tiempo real' : 'Desconectado' }}
        </span>
        <div v-if="isConnected" class="text-xs text-gray-400">
          {{ lastUpdate }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RealtimeCharts',
  data() {
    return {
      isConnected: true,
      lastUpdate: 'Ahora',
      nodeChartType: 'doughnut',
      renderTimeRange: '24h',
      
      // Chart instances
      performanceChart: null,
      queueChart: null,
      nodesChart: null,
      renderTimeChart: null,
      productivityChart: null,
      
      // Update intervals
      updateInterval: null,
      
      // Current metrics
      currentMetrics: {
        cpu: 72,
        memory: 58,
        gpu: 85
      },
      
      queueStats: {
        pending: 12,
        processing: 4,
        completed: 28
      },
      
      nodeStats: {
        active: 3,
        inactive: 1,
        rendering: 2,
        error: 0
      },
      
      renderMetrics: {
        average: 45,
        fastest: 12,
        slowest: 180
      },
      
      productivity: {
        framesPerHour: 156,
        jobsPerDay: 18,
        efficiency: 87,
        uptime: 94
      },
      
      // Chart data
      performanceData: {
        labels: [],
        datasets: [
          {
            label: 'CPU %',
            data: [],
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true
          },
          {
            label: 'RAM %',
            data: [],
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true
          },
          {
            label: 'GPU %',
            data: [],
            borderColor: '#8B5CF6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            fill: true
          }
        ]
      },
      
      queueData: {
        labels: [],
        datasets: [
          {
            label: 'En Cola',
            data: [],
            borderColor: '#F59E0B',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            fill: true
          },
          {
            label: 'Procesando',
            data: [],
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true
          },
          {
            label: 'Completados',
            data: [],
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true
          }
        ]
      }
    }
  },
  
  mounted() {
    this.initializeCharts();
    this.startRealtimeUpdates();
  },
  
  beforeUnmount() {
    this.stopRealtimeUpdates();
    this.destroyCharts();
  },
  
  methods: {
    async initializeCharts() {
      // Importar Chart.js dinámicamente para evitar SSR issues
      const { Chart, registerables } = await import('chart.js');
      Chart.register(...registerables);
      
      // Configuración común para todos los gráficos
      const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(107, 114, 128, 0.2)'
            },
            ticks: {
              color: '#9CA3AF'
            }
          },
          y: {
            grid: {
              color: 'rgba(107, 114, 128, 0.2)'
            },
            ticks: {
              color: '#9CA3AF'
            }
          }
        }
      };
      
      // Inicializar gráfico de rendimiento
      const performanceCtx = this.$refs.performanceChart.getContext('2d');
      this.performanceChart = new Chart(performanceCtx, {
        type: 'line',
        data: this.performanceData,
        options: {
          ...commonOptions,
          scales: {
            ...commonOptions.scales,
            y: {
              ...commonOptions.scales.y,
              max: 100,
              min: 0
            }
          }
        }
      });
      
      // Inicializar gráfico de cola
      const queueCtx = this.$refs.queueChart.getContext('2d');
      this.queueChart = new Chart(queueCtx, {
        type: 'line',
        data: this.queueData,
        options: commonOptions
      });
      
      // Inicializar gráfico de nodos
      this.initializeNodesChart();
      
      // Inicializar gráfico de tiempo de render
      this.initializeRenderTimeChart();
      
      // Inicializar gráfico de productividad
      this.initializeProductivityChart();
      
      // Llenar con datos iniciales
      this.generateInitialData();
    },
    
    initializeNodesChart() {
      const nodesCtx = this.$refs.nodesChart.getContext('2d');
      this.nodesChart = new Chart(nodesCtx, {
        type: this.nodeChartType,
        data: {
          labels: ['Activos', 'Inactivos', 'Renderizando', 'Error'],
          datasets: [{
            data: [
              this.nodeStats.active,
              this.nodeStats.inactive,
              this.nodeStats.rendering,
              this.nodeStats.error
            ],
            backgroundColor: [
              '#10B981',
              '#EF4444',
              '#F59E0B',
              '#6B7280'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          }
        }
      });
    },
    
    initializeRenderTimeChart() {
      const renderTimeCtx = this.$refs.renderTimeChart.getContext('2d');
      this.renderTimeChart = new Chart(renderTimeCtx, {
        type: 'bar',
        data: {
          labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
          datasets: [{
            label: 'Tiempo Promedio (min)',
            data: [45, 52, 38, 41, 48, 43],
            backgroundColor: 'rgba(251, 146, 60, 0.7)',
            borderColor: '#F97316',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(107, 114, 128, 0.2)'
              },
              ticks: {
                color: '#9CA3AF'
              }
            },
            y: {
              grid: {
                color: 'rgba(107, 114, 128, 0.2)'
              },
              ticks: {
                color: '#9CA3AF'
              }
            }
          }
        }
      });
    },
    
    initializeProductivityChart() {
      const productivityCtx = this.$refs.productivityChart.getContext('2d');
      this.productivityChart = new Chart(productivityCtx, {
        type: 'line',
        data: {
          labels: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'],
          datasets: [
            {
              label: 'Frames/Hora',
              data: [120, 135, 142, 156, 168, 172, 165, 158, 162, 155, 148, 140],
              borderColor: '#6366F1',
              backgroundColor: 'rgba(99, 102, 241, 0.1)',
              fill: true,
              yAxisID: 'y'
            },
            {
              label: 'Trabajos/Día',
              data: [12, 14, 15, 16, 18, 19, 18, 17, 18, 17, 16, 15],
              borderColor: '#06B6D4',
              backgroundColor: 'rgba(6, 182, 212, 0.1)',
              fill: true,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            mode: 'index',
            intersect: false,
          },
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            x: {
              grid: {
                color: 'rgba(107, 114, 128, 0.2)'
              },
              ticks: {
                color: '#9CA3AF'
              }
            },
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              grid: {
                color: 'rgba(107, 114, 128, 0.2)'
              },
              ticks: {
                color: '#9CA3AF'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              grid: {
                drawOnChartArea: false,
              },
              ticks: {
                color: '#9CA3AF'
              }
            }
          }
        }
      });
    },
    
    generateInitialData() {
      const now = new Date();
      
      // Generar datos históricos para los últimos 20 puntos
      for (let i = 19; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 30000); // Cada 30 segundos
        const timeLabel = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        this.performanceData.labels.push(timeLabel);
        this.performanceData.datasets[0].data.push(Math.floor(Math.random() * 40) + 60); // CPU 60-100%
        this.performanceData.datasets[1].data.push(Math.floor(Math.random() * 30) + 40); // RAM 40-70%
        this.performanceData.datasets[2].data.push(Math.floor(Math.random() * 50) + 50); // GPU 50-100%
        
        this.queueData.labels.push(timeLabel);
        this.queueData.datasets[0].data.push(Math.floor(Math.random() * 10) + 5); // En cola
        this.queueData.datasets[1].data.push(Math.floor(Math.random() * 5) + 2); // Procesando
        this.queueData.datasets[2].data.push(Math.floor(Math.random() * 20) + 10); // Completados
      }
      
      this.updateCharts();
    },
    
    startRealtimeUpdates() {
      this.updateInterval = setInterval(() => {
        this.updateRealtimeData();
        this.updateLastUpdateTime();
      }, 5000); // Actualizar cada 5 segundos
    },
    
    stopRealtimeUpdates() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
    },
    
    updateRealtimeData() {
      // Simular nuevos datos en tiempo real
      const now = new Date();
      const timeLabel = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      
      // Actualizar métricas actuales
      this.currentMetrics.cpu = Math.floor(Math.random() * 40) + 60;
      this.currentMetrics.memory = Math.floor(Math.random() * 30) + 40;
      this.currentMetrics.gpu = Math.floor(Math.random() * 50) + 50;
      
      // Actualizar estadísticas de cola
      this.queueStats.pending = Math.floor(Math.random() * 10) + 5;
      this.queueStats.processing = Math.floor(Math.random() * 5) + 2;
      this.queueStats.completed += Math.floor(Math.random() * 3);
      
      // Añadir nuevos puntos de datos
      this.addDataPoint(this.performanceData, timeLabel, [
        this.currentMetrics.cpu,
        this.currentMetrics.memory,
        this.currentMetrics.gpu
      ]);
      
      this.addDataPoint(this.queueData, timeLabel, [
        this.queueStats.pending,
        this.queueStats.processing,
        Math.floor(Math.random() * 5) + 1
      ]);
      
      this.updateCharts();
    },
    
    addDataPoint(dataObj, label, values) {
      dataObj.labels.push(label);
      values.forEach((value, index) => {
        dataObj.datasets[index].data.push(value);
      });
      
      // Mantener solo los últimos 20 puntos
      if (dataObj.labels.length > 20) {
        dataObj.labels.shift();
        dataObj.datasets.forEach(dataset => {
          dataset.data.shift();
        });
      }
    },
    
    updateCharts() {
      if (this.performanceChart) this.performanceChart.update('none');
      if (this.queueChart) this.queueChart.update('none');
    },
    
    updateLastUpdateTime() {
      const now = new Date();
      this.lastUpdate = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    },
    
    updateRenderTimeChart() {
      // Simular actualización basada en el rango seleccionado
      let newData = [];
      let newLabels = [];
      
      switch (this.renderTimeRange) {
        case '24h':
          newLabels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'];
          newData = [45, 52, 38, 41, 48, 43];
          break;
        case '7d':
          newLabels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
          newData = [42, 46, 39, 44, 41, 38, 45];
          break;
        case '30d':
          newLabels = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'];
          newData = [43, 41, 46, 44];
          break;
      }
      
      this.renderTimeChart.data.labels = newLabels;
      this.renderTimeChart.data.datasets[0].data = newData;
      this.renderTimeChart.update();
    },
    
    refreshCharts() {
      // Simular actualización de todos los gráficos
      this.updateRealtimeData();
      
      // Actualizar productividad con valores aleatorios
      this.productivity.framesPerHour = Math.floor(Math.random() * 50) + 130;
      this.productivity.jobsPerDay = Math.floor(Math.random() * 10) + 15;
      this.productivity.efficiency = Math.floor(Math.random() * 20) + 80;
      this.productivity.uptime = Math.floor(Math.random() * 10) + 90;
      
      // Actualizar gráfico de nodos
      this.nodesChart.data.datasets[0].data = [
        this.nodeStats.active,
        this.nodeStats.inactive,
        this.nodeStats.rendering,
        this.nodeStats.error
      ];
      this.nodesChart.update();
      
      console.log('Gráficos actualizados');
    },
    
    destroyCharts() {
      [this.performanceChart, this.queueChart, this.nodesChart, this.renderTimeChart, this.productivityChart]
        .forEach(chart => {
          if (chart) chart.destroy();
        });
    }
  },
  
  watch: {
    nodeChartType() {
      if (this.nodesChart) {
        this.nodesChart.destroy();
        this.initializeNodesChart();
      }
    }
  }
}
</script>

<style scoped>
canvas {
  max-height: 100%;
}
</style>