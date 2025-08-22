# Render_QM - Render Queue Manager

Sistema profesional de gestión de colas de render distribuido para Blender.

## Características Principales

- 🎬 Cola de render distribuida
- 🖥️ Monitoreo de nodos en tiempo real
- 📱 Notificaciones por WhatsApp/Email
- 🔧 Addon integrado para Blender
- 📊 Dashboard web completo
- ⚙️ Configuración flexible
- 🔒 Sistema de usuarios y permisos

## Estructura del Proyecto

```
Render_QM/
├── backend/          # API REST con FastAPI
├── frontend/         # Dashboard web con Vue.js
├── blender_addon/    # Addon para Blender
├── node_client/      # Cliente para nodos de render
├── notification_services/  # Servicios de notificación
├── shared/           # Código compartido
├── deploy/           # Scripts de deployment
├── docs/             # Documentación
└── tests/            # Tests automatizados
```

## Quick Start

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd Render_QM
   ```

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Instalar Addon en Blender**
   - Comprimir la carpeta `blender_addon/`
   - Instalar en Blender: Edit > Preferences > Add-ons > Install

## Documentación

Ver la carpeta `docs/` para documentación completa.

## Licencia

MIT License - Ver archivo LICENSE para detalles.
