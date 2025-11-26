# Reporte de Estructura del Proyecto: Render_QM
**Fecha:** 2025-11-25 18:01:50

## 🌳 Árbol de Directorios
```text
📁 Render_QM/
│   📄 configuracion.py
│   📄 deps_audit.py
│   📄 generate_report.py
│   📄 install_render_node.py
│   📄 lista.py
│   📄 project_summary.json
│   📄 setup.py
│   📄 summarize_project.py
│   📄 test.py
│   📁 app/
│   │   📄 main.py
│   │   📄 __init__.py
│   │   📁 api/
│   │   │   📄 __init__.py
│   │   │   📁 v1/
│   │   │   │   📄 auth.py
│   │   │   │   📄 config.py
│   │   │   │   📄 jobs.py
│   │   │   │   📄 nodes.py
│   │   │   │   📄 notifications.py
│   │   │   │   📄 queue.py
│   │   │   │   📄 settings.py
│   │   │   │   📄 system.py
│   │   │   │   📄 upload.py
│   │   │   │   📄 __init__.py
│   │   📁 core/
│   │   │   📄 config.py
│   │   │   📄 database.py
│   │   │   📄 exceptions.py
│   │   │   📄 security.py
│   │   │   📄 __init__.py
│   │   📁 models/
│   │   │   📄 job.py
│   │   │   📄 node.py
│   │   │   📄 notification.py
│   │   │   📄 render_settings.py
│   │   │   📄 user.py
│   │   │   📄 __init__.py
│   │   📁 schemas/
│   │   │   📄 job_schemas.py
│   │   │   📄 node_schemas.py
│   │   │   📄 notification_schemas.py
│   │   │   📄 user_schemas.py
│   │   │   📄 __init__.py
│   │   📁 services/
│   │   │   📄 blender_service.py
│   │   │   📄 file_service.py
│   │   │   📄 file_transfer.py
│   │   │   📄 node_monitor.py
│   │   │   📄 node_service.py
│   │   │   📄 notification_service.py
│   │   │   📄 preview_generator.py
│   │   │   📄 queue_manager.py
│   │   │   📄 render_engine.py
│   │   │   📄 render_service.py
│   │   │   📄 scheduler.py
│   │   │   📄 __init__.py
│   │   📁 utils/
│   │   │   📄 cleanup.py
│   │   │   📄 file_utils.py
│   │   │   📄 logging_utils.py
│   │   │   📄 network_utils.py
│   │   │   📄 system_monitor.py
│   │   │   📄 validation_utils.py
│   │   │   📄 __init__.py
│   │   📁 workers/
│   │   │   📄 cleanup_worker.py
│   │   │   📄 file_sync_worker.py
│   │   │   📄 monitor_worker.py
│   │   │   📄 render_worker.py
│   │   │   📄 __init__.py
│   📁 backend/
│   │   📄 config.json
│   │   📄 Dockerfile
│   │   📄 faltantes.py
│   │   📄 fix_all.py
│   │   📄 main.py
│   │   📄 package-lock.json
│   │   📄 setup_db.py
│   │   📄 setup_initial.py
│   │   📄 test_simple.py
│   │   📁 app/
│   │   │   📄 main.py
│   │   │   📄 main_working.py
│   │   │   📄 __init__.py
│   │   │   📁 api/
│   │   │   │   📄 __init__.py
│   │   │   │   📁 v1/
│   │   │   │   │   📄 auth.py
│   │   │   │   │   📄 config.py
│   │   │   │   │   📄 jobs.py
│   │   │   │   │   📄 nodes.py
│   │   │   │   │   📄 notifications.py
│   │   │   │   │   📄 queue.py
│   │   │   │   │   📄 settings.py
│   │   │   │   │   📄 system.py
│   │   │   │   │   📄 upload.py
│   │   │   │   │   📄 __init__.py
│   │   │   📁 core/
│   │   │   │   📄 config.py
│   │   │   │   📄 database.py
│   │   │   │   📄 exceptions.py
│   │   │   │   📄 security.py
│   │   │   │   📄 __init__.py
│   │   │   📁 models/
│   │   │   │   📄 job.py
│   │   │   │   📄 node.py
│   │   │   │   📄 notification.py
│   │   │   │   📄 render_settings.py
│   │   │   │   📄 user.py
│   │   │   │   📄 __init__.py
│   │   │   📁 schemas/
│   │   │   │   📄 job_schemas.py
│   │   │   │   📄 node_schemas.py
│   │   │   │   📄 notification_schemas.py
│   │   │   │   📄 user_schemas.py
│   │   │   │   📄 __init__.py
│   │   │   📁 services/
│   │   │   │   📄 blender_service.py
│   │   │   │   📄 file_service.py
│   │   │   │   📄 file_transfer.py
│   │   │   │   📄 node_monitor.py
│   │   │   │   📄 node_service.py
│   │   │   │   📄 notification_service.py
│   │   │   │   📄 preview_generator.py
│   │   │   │   📄 queue_manager.py
│   │   │   │   📄 render_engine.py
│   │   │   │   📄 render_service.py
│   │   │   │   📄 scheduler.py
│   │   │   │   📄 __init__.py
│   │   │   📁 utils/
│   │   │   │   📄 cleanup.py
│   │   │   │   📄 file_utils.py
│   │   │   │   📄 logging_utils.py
│   │   │   │   📄 network_utils.py
│   │   │   │   📄 system_monitor.py
│   │   │   │   📄 validation_utils.py
│   │   │   │   📄 __init__.py
│   │   │   📁 workers/
│   │   │   │   📄 cleanup_worker.py
│   │   │   │   📄 file_sync_worker.py
│   │   │   │   📄 monitor_worker.py
│   │   │   │   📄 render_worker.py
│   │   │   │   📄 __init__.py
│   │   📁 core/
│   │   │   📄 config.py
│   │   📁 logs/
│   │   📁 renders/
│   │   │   📁 1188d8d1-47a7-4754-9592-dd3cc8c37eac/
│   │   │   📁 12f9792f-2077-4110-b282-c2c672f0946a/
│   │   │   📁 13be9679-5760-40ab-a1fc-ca82abfd380e/
│   │   │   📁 1ad0ad23-d777-49c6-9068-1a5edd7ca69c/
│   │   │   📁 2b8d8874-bffd-4521-a92d-419b1b1d23d3/
│   │   │   📁 43af92b8-95aa-40bc-b280-8201fd7ae1f0/
│   │   │   📁 460a4b2a-2985-4ae7-80fd-0ee6076a76af/
│   │   │   📁 58841558-bb18-4b94-880f-e8abc9dd6e20/
│   │   │   📁 5ec33524-c790-4ff7-b1cf-b179453bdad1/
│   │   │   📁 721674c4-8e91-4d83-b179-6526bffbbe58/
│   │   │   📁 796806b9-fd0b-45a0-855c-bb119ca6f2a6/
│   │   │   📁 7f2b9205-d14b-4b41-bf0b-67800768620d/
│   │   │   📁 83c900e6-76d3-4420-a224-d7e3ea9ad2af/
│   │   │   📁 84a6c59b-2a48-4529-8fba-b91676c0b374/
│   │   │   📁 8bc9c3fb-afc6-4c3f-8049-6678021f7a84/
│   │   │   📁 91dec543-82b7-4bfc-8fd3-c293b5c77e1e/
│   │   │   📁 96171241-0964-4a41-a7e2-69b3c44fb4d7/
│   │   │   📁 97e876f0-e269-487d-9420-b4f0fdc4bae0/
│   │   │   📁 a2df77f0-55ea-4fc8-ace3-4ea91f4ad061/
│   │   │   📁 ab3c390e-5a11-49ba-8226-4502433915b0/
│   │   │   📁 acd1f6ed-ed3e-4d31-9a7a-94f63654435c/
│   │   │   📁 b01d82fe-46bf-47c1-abc4-bc5650844187/
│   │   │   📁 cb96f05e-8514-40f9-8977-b0129cb6e5b7/
│   │   │   📁 d1c71397-f715-4bf1-9862-d587b9339fbe/
│   │   │   📁 f0b9bc1a-3dcf-4135-a0ae-9354b4a39b61/
│   │   │   📁 f2d294e9-7867-45d7-ad90-8a5deb1d4bab/
│   │   │   📁 fb62a067-7448-4e12-8deb-a841b8ab2b2f/
│   │   │   📁 fb8ab324-0a2e-471c-9ed4-647b37ec345d/
│   │   │   📁 fd5fb7c3-9893-4a37-b2bb-9422cae0ee8e/
│   │   📁 scripts/
│   │   │   📄 backup_db.py
│   │   │   📄 health_check.py
│   │   │   📄 migrate_db.py
│   │   │   📄 setup_master.py
│   │   │   📄 setup_node.py
│   │   📁 temp/
│   │   📁 tests/
│   │   │   📄 test_api.py
│   │   │   📄 test_models.py
│   │   │   📄 test_services.py
│   │   │   📄 test_workers.py
│   │   │   📄 __init__.py
│   │   📁 uploads/
│   📁 blender_addon/
│   │   📄 addon_prefs.py
│   │   📄 preferences.py
│   │   📄 __init__.py
│   │   📁 core/
│   │   │   📄 api_client.py
│   │   │   📄 file_manager.py
│   │   │   📄 job_submit.py
│   │   │   📄 scene_export.py
│   │   │   📄 settings_manager.py
│   │   │   📄 __init__.py
│   │   📁 ui/
│   │   │   📄 menus.py
│   │   │   📄 operators.py
│   │   │   📄 panels.py
│   │   │   📄 properties.py
│   │   │   📄 __init__.py
│   │   📁 utils/
│   │   │   📄 constants.py
│   │   │   📄 helpers.py
│   │   │   📄 validation.py
│   │   │   📄 __init__.py
│   📁 config/
│   📁 deploy/
│   │   📁 ansible/
│   │   │   📁 roles/
│   │   │   │   📁 master/
│   │   │   │   │   📁 tasks/
│   │   │   │   📁 node/
│   │   │   │   │   📁 tasks/
│   │   📁 docker/
│   │   📁 k8s/
│   │   📁 scripts/
│   │   📁 terraform/
│   📁 docs/
│   │   📁 diagrams/
│   │   📁 images/
│   📁 frontend/
│   │   📄 create_advanced_components.py
│   │   📄 dark_theme_auth_system.py
│   │   📄 Dockerfile
│   │   📄 package-lock.json
│   │   📄 package.json
│   │   📄 postcss.config.js
│   │   📄 setup_frontend.py
│   │   📄 tailwind.config.js
│   │   📄 vite.config.js
│   │   📁 public/
│   │   📁 src/
│   │   │   📄 main.js
│   │   │   📁 assets/
│   │   │   │   📁 css/
│   │   │   │   📁 icons/
│   │   │   │   📁 images/
│   │   │   📁 components/
│   │   │   │   📁 Common/
│   │   │   │   📁 Dashboard/
│   │   │   │   📁 Jobs/
│   │   │   │   📁 Nodes/
│   │   │   │   📁 Queue/
│   │   │   │   📁 Settings/
│   │   │   📁 composables/
│   │   │   │   📄 useApi.js
│   │   │   │   📄 useNotifications.js
│   │   │   │   📄 useWebSocket.js
│   │   │   📁 pages/
│   │   │   📁 router/
│   │   │   │   📄 guards.js
│   │   │   │   📄 index.js
│   │   │   📁 services/
│   │   │   │   📄 api.js
│   │   │   │   📄 auth.js
│   │   │   │   📄 file_upload.js
│   │   │   │   📄 notifications.js
│   │   │   │   📄 websocket.js
│   │   │   📁 stores/
│   │   │   │   📄 auth.js
│   │   │   │   📄 nodes.js
│   │   │   │   📄 notifications.js
│   │   │   │   📄 queue.js
│   │   │   │   📄 settings.js
│   │   │   📁 utils/
│   │   │   │   📄 constants.js
│   │   │   │   📄 formatters.js
│   │   │   │   📄 helpers.js
│   │   │   │   📄 validators.js
│   │   │   📁 views/
│   │   │   │   📁 auth/
│   │   │   │   📁 error/
│   📁 logs/
│   📁 monitoring/
│   │   📁 grafana/
│   │   │   📁 dashboards/
│   │   │   │   📄 render_queue.json
│   │   │   │   📄 system_health.json
│   │   📁 prometheus/
│   📁 node_client/
│   │   📄 api_client.py
│   │   📄 file_manager.py
│   │   📄 health_checker.py
│   │   📄 log_manager.py
│   │   📄 node_agent.py
│   │   📄 render_executor.py
│   │   📄 setup.py
│   │   📄 system_monitor.py
│   │   📁 config/
│   │   📁 renders_node/
│   │   │   📁 1236ed13-c687-406c-9de1-1ffd5a934c23/
│   │   │   📁 1aa21ecb-f651-4e48-a493-74d5378cceda/
│   │   │   📁 56daa534-1e14-4c65-9786-96bd21d59320/
│   │   │   📁 880119d3-ce97-4bb1-9297-17dac529b0bd/
│   │   │   📁 986d1ccd-219c-4284-984f-94b84f5f48f4/
│   │   │   📁 a99570a0-37e4-4919-8dc4-5ea3917745e0/
│   │   │   📁 b6837507-d874-4823-a5c0-1666f3557257/
│   │   │   📁 cff95a34-f379-4e3b-906a-17319e2891c2/
│   │   │   📁 e3360def-225c-4015-81da-a7dadc4abaf5/
│   │   📁 scripts/
│   │   │   📄 install.py
│   │   │   📄 service_setup.py
│   │   │   📄 uninstall.py
│   │   📁 temp_node/
│   │   │   📄 gpu_setup.py
│   │   │   📁 1236ed13-c687-406c-9de1-1ffd5a934c23/
│   │   │   📁 1aa21ecb-f651-4e48-a493-74d5378cceda/
│   │   │   📁 43af92b8-95aa-40bc-b280-8201fd7ae1f0/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 45eb0126-cac1-48e2-b76c-adb78053e3f1/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 56daa534-1e14-4c65-9786-96bd21d59320/
│   │   │   📁 5ec33524-c790-4ff7-b1cf-b179453bdad1/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 6caf0db0-9cd0-47da-aa64-2e30fbc5c618/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 796806b9-fd0b-45a0-855c-bb119ca6f2a6/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 880119d3-ce97-4bb1-9297-17dac529b0bd/
│   │   │   📁 89a737f8-6cb5-49fa-97ea-aa0ff716664b/
│   │   │   📁 986d1ccd-219c-4284-984f-94b84f5f48f4/
│   │   │   📁 a2df77f0-55ea-4fc8-ace3-4ea91f4ad061/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 acd1f6ed-ed3e-4d31-9a7a-94f63654435c/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 b6837507-d874-4823-a5c0-1666f3557257/
│   │   │   📁 cb96f05e-8514-40f9-8977-b0129cb6e5b7/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 cff95a34-f379-4e3b-906a-17319e2891c2/
│   │   │   📁 de1e113a-d425-42f0-8831-aca73eca1c5a/
│   │   │   📁 e1cb2aa0-ec15-451f-926a-31458fb489ef/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 f2d294e9-7867-45d7-ad90-8a5deb1d4bab/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   │   📁 fb62a067-7448-4e12-8deb-a841b8ab2b2f/
│   │   │   │   📄 gpu_setup.py
│   │   │   │   📁 output/
│   │   📁 utils/
│   │   │   📄 file_utils.py
│   │   │   📄 network_utils.py
│   │   │   📄 system_utils.py
│   📁 notification_services/
│   │   📄 notification_manager.py
│   │   📄 __init__.py
│   │   📁 email/
│   │   │   📄 attachment_handler.py
│   │   │   📄 email_client.py
│   │   │   📄 __init__.py
│   │   │   📁 templates/
│   │   📁 slack/
│   │   │   📄 slack_client.py
│   │   │   📄 webhook_handler.py
│   │   │   📄 __init__.py
│   │   📁 telegram/
│   │   │   📄 bot_commands.py
│   │   │   📄 telegram_client.py
│   │   │   📄 __init__.py
│   │   📁 whatsapp/
│   │   │   📄 media_handler.py
│   │   │   📄 message_templates.py
│   │   │   📄 whatsapp_client.py
│   │   │   📄 __init__.py
│   📁 renders/
│   📁 scripts/
│   │   📄 build_addon.py
│   │   📄 dev_setup.py
│   │   📄 install_dependencies.py
│   │   📄 migrate_data.py
│   │   📄 package_release.py
│   │   📄 run_tests.py
│   📁 shared/
│   │   📄 constants.py
│   │   📄 exceptions.py
│   │   📄 models.py
│   │   📄 protocols.py
│   │   📄 schemas.py
│   │   📄 utils.py
│   │   📄 __init__.py
│   📁 temp/
│   📁 tests/
│   │   📁 backend/
│   │   │   📄 test_api.py
│   │   │   📄 test_models.py
│   │   │   📄 test_services.py
│   │   │   📄 test_workers.py
│   │   │   📄 __init__.py
│   │   📁 e2e/
│   │   │   📄 test_addon_integration.py
│   │   │   📄 test_user_flows.py
│   │   │   📄 __init__.py
│   │   📁 fixtures/
│   │   │   📁 sample_blend_files/
│   │   │   📁 test_data/
│   │   📁 frontend/
│   │   │   📄 components.test.js
│   │   │   📄 stores.test.js
│   │   │   📄 utils.test.js
│   │   📁 integration/
│   │   │   📄 test_full_workflow.py
│   │   │   📄 test_node_communication.py
│   │   │   📄 test_notifications.py
│   │   │   📄 __init__.py
│   │   📁 performance/
│   │   │   📄 test_queue_performance.py
│   │   │   📄 test_render_performance.py
│   │   │   📄 __init__.py
```

## 🐍 Análisis Detallado de Backend (.py)

### 📄 `configuracion.py`
**Librerías/Imports:** `app.core.database.Base, app.core.database.SessionLocal, app.core.database.engine, app.main.app, app.models.job.Job, app.models.node.Node, app.models.user.User, os, passlib.context.CryptContext, pathlib.Path, requests, subprocess, sys, time, traceback`

**Estructura del Código:**
- ⚡ **Función:** `create_all_files`
  - *Descripción:* Crear todos los archivos necesarios
- ⚡ **Función:** `install_dependencies`
  - *Descripción:* Instalar dependencias
- ⚡ **Función:** `setup_database`
  - *Descripción:* Configurar base de datos y crear usuario admin
- ⚡ **Función:** `test_server`
  - *Descripción:* Probar que el servidor funciona
- ⚡ **Función:** `create_startup_script`
  - *Descripción:* Crear script de inicio
- ⚡ **Función:** `main`
  - *Descripción:* Función principal

---

### 📄 `deps_audit.py`
**Librerías/Imports:** `collections.defaultdict, json, os, pathlib.Path, re, sys`

**Estructura del Código:**
- ⚡ **Función:** `parse_req_line`
- ⚡ **Función:** `read_requirements`
- ⚡ **Función:** `load_summary`
- ⚡ **Función:** `main`

---

### 📄 `generate_report.py`
**Librerías/Imports:** `ast, datetime, os`

**Estructura del Código:**
- ⚡ **Función:** `get_file_info`
  - *Descripción:* Analiza un archivo Python y extrae imports, clases y funciones.
- ⚡ **Función:** `generate_tree`
  - *Descripción:* Genera un árbol visual de directorios.
- ⚡ **Función:** `main`

---

### 📄 `install_render_node.py`
**Librerías/Imports:** `json, os, pathlib.Path, platform, socket, subprocess, sys, time, tkinter, tkinter.messagebox, tkinter.simpledialog, urllib.request, yaml`

**Estructura del Código:**
- ⚡ **Función:** `log`
  - *Descripción:* Función de logging que funciona siempre
- ⚡ **Función:** `show_message`
  - *Descripción:* Mostrar mensaje usando GUI o consola
- ⚡ **Función:** `get_input`
  - *Descripción:* Obtener entrada del usuario con GUI o valores por defecto
- ⚡ **Función:** `detect_server`
  - *Descripción:* Detectar servidor automáticamente
- ⚡ **Función:** `install_dependencies`
  - *Descripción:* Instalar dependencias Python
- ⚡ **Función:** `detect_blender`
  - *Descripción:* Detectar Blender automáticamente
- ⚡ **Función:** `download_node_files`
  - *Descripción:* Descargar archivos del nodo
- ⚡ **Función:** `create_minimal_node`
  - *Descripción:* Crear nodo mínimo si no se puede descargar
- ⚡ **Función:** `create_config`
  - *Descripción:* Crear archivo de configuración
- ⚡ **Función:** `create_shortcuts`
  - *Descripción:* Crear accesos directos y scripts de inicio
- ⚡ **Función:** `test_installation`
  - *Descripción:* Probar la instalación
- ⚡ **Función:** `main`
  - *Descripción:* Función principal del instalador

---

### 📄 `lista.py`
**Librerías/Imports:** `os`

**Estructura del Código:**
- ⚡ **Función:** `listar_directorio_a_txt`
  - *Descripción:* Recorre un directorio y guarda los nombres de las carpetas y archivos en un archivo .txt.

---

### 📄 `setup.py`

**Estructura del Código:**

---

### 📄 `summarize_project.py`
**Librerías/Imports:** `argparse, ast, collections.Counter, collections.defaultdict, json, os, pathlib.Path, re, typing.Dict, typing.List, typing.Optional, typing.Set, typing.Tuple`

**Estructura del Código:**
- ⚡ **Función:** `read_text`
- ⚡ **Función:** `parse_requirements`
- ⚡ **Función:** `list_python_files`
- ⚡ **Función:** `safe_parse_ast`
- ⚡ **Función:** `collect_imports`
  - *Descripción:* Returns:
- ⚡ **Función:** `grep_patterns`
- ⚡ **Función:** `find_env_vars`
- ⚡ **Función:** `find_fastapi_routes`
  - *Descripción:* Heurística: encuentra APIRouter y rutas via .get/ .post / .put / .delete.
- ⚡ **Función:** `detect_files`
- ⚡ **Función:** `short_rel`
- ⚡ **Función:** `summarize_structure`
  - *Descripción:* Lista carpetas de primer nivel y algunos submódulos comunes.
- ⚡ **Función:** `read_project_name`
- ⚡ **Función:** `collect_entrypoints`
- ⚡ **Función:** `main`

---

### 📄 `test.py`
**Librerías/Imports:** `aiohttp, app.core.database.Base, app.core.database.SessionLocal, app.core.database.engine, app.models.Job, app.models.Node, app.models.User, asyncio, datetime.datetime, fastapi, json, os, passlib.context.CryptContext, pathlib.Path, socket, sqlalchemy, sqlite3, subprocess, sys, uvicorn, websockets`

**Estructura del Código:**
- 🏛️ **Clase:** `RenderQMTester`
  - 🔹 Método: `__init__`
  - 🔹 Método: `get_auth_headers`
- ⚡ **Función:** `check_requirements`
  - *Descripción:* Verificar que el servidor esté disponible
- ⚡ **Función:** `setup_environment`
  - *Descripción:* Configurar entorno inicial
- ⚡ **Función:** `setup_database`
  - *Descripción:* Configurar base de datos inicial
- ⚡ **Función:** `check_dependencies`
  - *Descripción:* Verificar dependencias
- ⚡ **Función:** `run_server`
  - *Descripción:* Ejecutar servidor
- ⚡ **Función:** `main`
  - *Descripción:* Función principal

---

### 📄 `app\main.py`

**Estructura del Código:**

---

### 📄 `app\__init__.py`

**Estructura del Código:**

---

### 📄 `app\api\__init__.py`

**Estructura del Código:**

---

### 📄 `app\api\v1\auth.py`
**Librerías/Imports:** `core.database.get_db, fastapi.APIRouter, fastapi.Depends, fastapi.HTTPException, fastapi.security.OAuth2PasswordBearer, fastapi.security.OAuth2PasswordRequestForm, fastapi.status, models.user.User, passlib.context.CryptContext, schemas.user_schemas.Token, schemas.user_schemas.UserResponse, sqlalchemy.orm.Session`

**Estructura del Código:**
- ⚡ **Función:** `verify_password`
- ⚡ **Función:** `authenticate_user`

---

### 📄 `app\api\v1\config.py`
**Librerías/Imports:** `app.services.blender_service.blender_service, fastapi.APIRouter, fastapi.HTTPException, os, pathlib.Path, platform, pydantic.BaseModel, subprocess, typing.Dict, typing.List`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderTestRequest`

---

### 📄 `app\api\v1\jobs.py`
**Librerías/Imports:** `app.core.config.settings, app.core.database.add_job_to_queue, app.core.database.cleanup_old_jobs, app.core.database.create_job, app.core.database.delete_job, app.core.database.get_job, app.core.database.get_jobs_by_status, app.core.database.get_queue_statistics, app.core.database.jobs_db, app.core.database.search_jobs, app.core.database.update_job, app.core.database.validate_database_integrity, app.models.job.BlendFileAnalysis, app.models.job.JobCreate, app.models.job.JobExport, app.models.job.JobFilter, app.models.job.JobListResponse, app.models.job.JobResponse, app.models.job.JobSearch, app.models.job.JobUpdate, app.services.blender_service.blender_service, app.services.render_service.render_service, asyncio, csv, datetime.datetime, datetime.timedelta, fastapi.APIRouter, fastapi.BackgroundTasks, fastapi.File, fastapi.Form, fastapi.HTTPException, fastapi.Query, fastapi.UploadFile, fastapi.responses.FileResponse, fastapi.responses.StreamingResponse, io.BytesIO, io.StringIO, json, logging, os, pathlib.Path, re, shutil, typing.Any, typing.Dict, typing.List, typing.Optional, uuid, zipfile`

**Estructura del Código:**

---

### 📄 `app\api\v1\nodes.py`
**Error de Sintaxis al leer este archivo**

---

### 📄 `app\api\v1\notifications.py`
**Librerías/Imports:** `fastapi.APIRouter`

**Estructura del Código:**

---

### 📄 `app\api\v1\queue.py`
**Librerías/Imports:** `core.database.get_db, fastapi.APIRouter, fastapi.Depends, models.job.Job, models.node.Node, sqlalchemy.orm.Session`

**Estructura del Código:**

---

### 📄 `app\api\v1\settings.py`
**Librerías/Imports:** `os, pathlib.Path, pydantic.BaseModel, subprocess, typing.Dict, typing.List, winreg`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderTestRequest`

---

### 📄 `app\api\v1\system.py`

**Estructura del Código:**

---

### 📄 `app\api\v1\upload.py`

**Estructura del Código:**

---

### 📄 `app\api\v1\__init__.py`

**Estructura del Código:**

---

### 📄 `app\core\config.py`
**Librerías/Imports:** `json, logging, os, pathlib.Path, platform, sys, typing.Any, typing.Dict`

**Estructura del Código:**
- ⚡ **Función:** `load_config`
  - *Descripción:* Cargar configuración desde archivo JSON.
- ⚡ **Función:** `save_config`
  - *Descripción:* Guardar configuración a archivo JSON.
- ⚡ **Función:** `merge_configs`
  - *Descripción:* Merge configuración del usuario con la por defecto (recursivo).
- 🏛️ **Clase:** `Settings`
  - *Descripción:* Clase de configuración singleton para el sistema.
  - 🔹 Método: `__init__`
  - 🔹 Método: `get_blender_config`
  - 🔹 Método: `update_blender_config`
  - 🔹 Método: `get_render_config`
  - 🔹 Método: `update_render_config`
  - 🔹 Método: `save_config`
  - 🔹 Método: `reload_config`
  - 🔹 Método: `reset_config`
  - 🔹 Método: `get_system_info`
  - 🔹 Método: `validate_config`
- ⚡ **Función:** `get_settings`
  - *Descripción:* Obtener instancia singleton de configuración.

---

### 📄 `app\core\database.py`
**Librerías/Imports:** `app.core.config.settings, collections.defaultdict, datetime.datetime, datetime.timedelta, logging, os, pathlib.Path, platform, shutil, typing.Any, typing.Dict, typing.List, uuid`

**Estructura del Código:**
- ⚡ **Función:** `init_directories`
  - *Descripción:* Inicializar directorios necesarios
- ⚡ **Función:** `init_database`
  - *Descripción:* Inicializar base de datos en memoria con valores por defecto
- ⚡ **Función:** `create_job`
  - *Descripción:* Crear un nuevo trabajo en la base de datos
- ⚡ **Función:** `get_job`
  - *Descripción:* Obtener trabajo por ID
- ⚡ **Función:** `update_job`
  - *Descripción:* Actualizar trabajo existente
- ⚡ **Función:** `delete_job`
  - *Descripción:* Eliminar trabajo de la base de datos
- ⚡ **Función:** `get_jobs_by_status`
  - *Descripción:* Obtener trabajos por estado
- ⚡ **Función:** `get_jobs_by_user`
  - *Descripción:* Obtener trabajos de un usuario específico
- ⚡ **Función:** `register_node`
  - *Descripción:* Registrar un nuevo nodo
- ⚡ **Función:** `update_node_heartbeat`
  - *Descripción:* Actualizar heartbeat de un nodo
- ⚡ **Función:** `get_available_nodes`
  - *Descripción:* Obtener nodos disponibles para asignar trabajos
- ⚡ **Función:** `cleanup_offline_nodes`
  - *Descripción:* Limpiar nodos que están offline
- ⚡ **Función:** `add_job_to_queue`
  - *Descripción:* Añadir trabajo a la cola distribuida
- ⚡ **Función:** `get_next_job_from_queue`
  - *Descripción:* Obtener siguiente trabajo de la cola
- ⚡ **Función:** `assign_job_to_node`
  - *Descripción:* Asignar trabajo a un nodo específico
- ⚡ **Función:** `create_upload_session`
  - *Descripción:* Crear sesión de upload por chunks
- ⚡ **Función:** `update_upload_session`
  - *Descripción:* Actualizar progreso de sesión de upload
- ⚡ **Función:** `cleanup_expired_sessions`
  - *Descripción:* Limpiar sesiones expiradas
- ⚡ **Función:** `get_queue_statistics`
  - *Descripción:* Obtener estadísticas de la cola de render
- ⚡ **Función:** `get_nodes_statistics`
  - *Descripción:* Obtener estadísticas de los nodos
- ⚡ **Función:** `get_system_statistics`
  - *Descripción:* Obtener estadísticas generales del sistema
- ⚡ **Función:** `format_duration`
  - *Descripción:* Formatear duración en formato legible
- ⚡ **Función:** `export_database_state`
  - *Descripción:* Exportar estado actual de la base de datos
- ⚡ **Función:** `import_database_state`
  - *Descripción:* Importar estado de la base de datos
- ⚡ **Función:** `search_jobs`
  - *Descripción:* Buscar trabajos por criterios
- ⚡ **Función:** `get_jobs_summary_by_date`
  - *Descripción:* Obtener resumen de trabajos por fecha
- ⚡ **Función:** `cleanup_old_jobs`
  - *Descripción:* Limpiar trabajos antiguos completados/fallidos
- ⚡ **Función:** `validate_database_integrity`
  - *Descripción:* Validar integridad de la base de datos

---

### 📄 `app\core\exceptions.py`

**Estructura del Código:**

---

### 📄 `app\core\security.py`

**Estructura del Código:**

---

### 📄 `app\core\__init__.py`

**Estructura del Código:**

---

### 📄 `app\models\job.py`
**Librerías/Imports:** `datetime.datetime, enum.Enum, pydantic.BaseModel, pydantic.Field, pydantic.validator, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `JobStatus`
  - *Descripción:* Estados posibles de un trabajo de render
- 🏛️ **Clase:** `RenderEngine`
  - *Descripción:* Motores de render soportados
- 🏛️ **Clase:** `JobPriority`
  - *Descripción:* Niveles de prioridad de trabajos
- 🏛️ **Clase:** `DistributionType`
  - *Descripción:* Tipos de distribución de trabajos
- 🏛️ **Clase:** `JobCreate`
  - *Descripción:* Modelo para crear un nuevo trabajo
  - 🔹 Método: `validate_frame_range`
  - 🔹 Método: `validate_tags`
- 🏛️ **Clase:** `JobUpdate`
  - *Descripción:* Modelo para actualizar un trabajo existente
- 🏛️ **Clase:** `JobResponse`
  - *Descripción:* Modelo de respuesta para trabajos
- 🏛️ **Clase:** `JobStatistics`
  - *Descripción:* Estadísticas de un trabajo
- 🏛️ **Clase:** `JobProgress`
  - *Descripción:* Progreso detallado de un trabajo
- 🏛️ **Clase:** `JobQueue`
  - *Descripción:* Información de posición en cola
- 🏛️ **Clase:** `CyclesSettings`
  - *Descripción:* Configuraciones específicas para Cycles
- 🏛️ **Clase:** `EeveeSettings`
  - *Descripción:* Configuraciones específicas para Eevee
- 🏛️ **Clase:** `RenderSettings`
  - *Descripción:* Configuraciones generales de render
- 🏛️ **Clase:** `JobFilter`
  - *Descripción:* Filtros para búsqueda de trabajos
- 🏛️ **Clase:** `JobSearch`
  - *Descripción:* Parámetros de búsqueda de trabajos
- 🏛️ **Clase:** `JobListResponse`
  - *Descripción:* Respuesta paginada de lista de trabajos
- 🏛️ **Clase:** `BlendFileInfo`
  - *Descripción:* Información extraída de un archivo .blend
- 🏛️ **Clase:** `BlendFileAnalysis`
  - *Descripción:* Análisis completo de un archivo .blend
- 🏛️ **Clase:** `JobNotification`
  - *Descripción:* Notificación de estado de trabajo
- 🏛️ **Clase:** `JobExport`
  - *Descripción:* Configuración para exportar trabajos
- 🏛️ **Clase:** `JobImport`
  - *Descripción:* Configuración para importar trabajos
- ⚡ **Función:** `validate_job_data`
  - *Descripción:* Validar datos de trabajo antes de crear
- ⚡ **Función:** `estimate_job_complexity`
  - *Descripción:* Estimar complejidad de un trabajo (0-10)

---

### 📄 `app\models\node.py`
**Librerías/Imports:** `datetime.datetime, enum.Enum, pydantic.BaseModel, pydantic.Field, pydantic.validator, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NodeStatus`
  - *Descripción:* Estados posibles de un nodo
- 🏛️ **Clase:** `NodePlatform`
  - *Descripción:* Plataformas soportadas
- 🏛️ **Clase:** `NodeCapabilityType`
  - *Descripción:* Tipos de capacidades de nodo
- 🏛️ **Clase:** `GPUType`
  - *Descripción:* Tipos de GPU soportadas
- 🏛️ **Clase:** `SystemStats`
  - *Descripción:* Estadísticas del sistema del nodo
- 🏛️ **Clase:** `NodeInfo`
  - *Descripción:* Información estática del nodo
  - 🔹 Método: `logical_cores_gte_physical`
- 🏛️ **Clase:** `NodeCapabilities`
  - *Descripción:* Capacidades del nodo
  - 🔹 Método: `validate_engines`
- 🏛️ **Clase:** `NodeRegistration`
  - *Descripción:* Datos para registrar un nuevo nodo
  - 🔹 Método: `validate_tags`
- 🏛️ **Clase:** `NodeHeartbeat`
  - *Descripción:* Datos del heartbeat de un nodo
- 🏛️ **Clase:** `NodeResponse`
  - *Descripción:* Respuesta completa de información del nodo
- 🏛️ **Clase:** `JobAssignment`
  - *Descripción:* Asignación de trabajo a nodo
- 🏛️ **Clase:** `NodeWorkload`
  - *Descripción:* Carga de trabajo actual del nodo
- 🏛️ **Clase:** `NodeConfig`
  - *Descripción:* Configuración de un nodo
- 🏛️ **Clase:** `NodeUpdate`
  - *Descripción:* Actualización de configuración de nodo
- 🏛️ **Clase:** `NodeStatistics`
  - *Descripción:* Estadísticas detalladas del nodo
- 🏛️ **Clase:** `NodesOverview`
  - *Descripción:* Vista general de todos los nodos
- 🏛️ **Clase:** `NodePerformance`
  - *Descripción:* Métricas de rendimiento de nodo
- 🏛️ **Clase:** `NodeFilter`
  - *Descripción:* Filtros para búsqueda de nodos
- 🏛️ **Clase:** `NodeSearch`
  - *Descripción:* Parámetros de búsqueda de nodos
- 🏛️ **Clase:** `NodeMaintenance`
  - *Descripción:* Programar mantenimiento de nodo
- 🏛️ **Clase:** `NodeDiagnostic`
  - *Descripción:* Diagnóstico de nodo
- ⚡ **Función:** `validate_node_requirements`
  - *Descripción:* Validar que un nodo cumple los requisitos mínimos
- ⚡ **Función:** `calculate_node_score`
  - *Descripción:* Calcular puntuación global del nodo (0-100)
- ⚡ **Función:** `find_best_node_for_job`
  - *Descripción:* Encontrar el mejor nodo para un trabajo específico

---

### 📄 `app\models\notification.py`

**Estructura del Código:**

---

### 📄 `app\models\render_settings.py`

**Estructura del Código:**

---

### 📄 `app\models\user.py`
**Librerías/Imports:** `core.database.Base, sqlalchemy.Boolean, sqlalchemy.Column, sqlalchemy.DateTime, sqlalchemy.Integer, sqlalchemy.String, sqlalchemy.sql.func`

**Estructura del Código:**
- 🏛️ **Clase:** `User`

---

### 📄 `app\models\__init__.py`

**Estructura del Código:**

---

### 📄 `app\schemas\job_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `JobCreate`
- 🏛️ **Clase:** `JobResponse`

---

### 📄 `app\schemas\node_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NodeCreate`
- 🏛️ **Clase:** `NodeStats`
- 🏛️ **Clase:** `NodeResponse`

---

### 📄 `app\schemas\notification_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.EmailStr, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NotificationBase`
- 🏛️ **Clase:** `NotificationCreate`
- 🏛️ **Clase:** `NotificationResponse`

---

### 📄 `app\schemas\user_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.EmailStr, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `UserCreate`
- 🏛️ **Clase:** `UserResponse`
- 🏛️ **Clase:** `Token`

---

### 📄 `app\schemas\__init__.py`

**Estructura del Código:**

---

### 📄 `app\services\blender_service.py`
**Librerías/Imports:** `app.core.config.settings, json, logging, os, pathlib.Path, platform, re, subprocess, time, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderService`
  - *Descripción:* Servicio para gestión de Blender y análisis de archivos .blend
  - 🔹 Método: `__init__`
  - 🔹 Método: `scan_for_blender`
  - 🔹 Método: `_verify_blender_installation`
  - 🔹 Método: `get_current_blender_path`
  - 🔹 Método: `verify_blender_path`
  - 🔹 Método: `get_blend_file_info`
  - 🔹 Método: `estimate_render_time`
  - 🔹 Método: `_format_time_duration`
  - 🔹 Método: `validate_blend_file`
  - 🔹 Método: `get_recommended_settings`
  - 🔹 Método: `auto_detect_and_configure`
  - 🔹 Método: `test_render_capability`
  - 🔹 Método: `clear_cache`

---

### 📄 `app\services\file_service.py`

**Estructura del Código:**

---

### 📄 `app\services\file_transfer.py`

**Estructura del Código:**

---

### 📄 `app\services\node_monitor.py`

**Estructura del Código:**

---

### 📄 `app\services\node_service.py`

**Estructura del Código:**

---

### 📄 `app\services\notification_service.py`
**Librerías/Imports:** `aiohttp, app.core.config.settings, asyncio, datetime.datetime, email.encoders, email.mime.base.MIMEBase, email.mime.multipart.MIMEMultipart, email.mime.text.MIMEText, pathlib.Path, smtplib`

**Estructura del Código:**
- 🏛️ **Clase:** `NotificationService`
  - 🔹 Método: `__init__`

---

### 📄 `app\services\preview_generator.py`

**Estructura del Código:**

---

### 📄 `app\services\queue_manager.py`
**Librerías/Imports:** `asyncio, core.database.SessionLocal, datetime.datetime, models.job.Job, models.job.JobStatus, models.node.Node, sqlalchemy.orm.Session, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `QueueManager`
  - 🔹 Método: `__init__`

---

### 📄 `app\services\render_engine.py`
**Librerías/Imports:** `asyncio, core.config.settings, json, os, pathlib.Path, subprocess, typing.Any, typing.Dict, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderRenderer`
  - 🔹 Método: `__init__`
  - 🔹 Método: `_build_render_args`
  - 🔹 Método: `_create_temp_script`

---

### 📄 `app\services\render_service.py`
**Librerías/Imports:** `app.core.config.settings, app.core.database.jobs_db, app.core.database.nodes_db, app.core.database.update_job, app.services.blender_service.blender_service, app.utils.system_monitor.system_monitor, asyncio, datetime.datetime, datetime.timedelta, logging, os, pathlib.Path, platform, re, shutil, subprocess, typing.Any, typing.Callable, typing.Dict, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `RenderService`
  - *Descripción:* Servicio principal de renderización
  - 🔹 Método: `__init__`
  - 🔹 Método: `_prepare_render_config`
  - 🔹 Método: `_get_engine_specific_args`
  - 🔹 Método: `_parse_frame_completion`
  - 🔹 Método: `_evaluate_render_result`
  - 🔹 Método: `_find_rendered_files`
  - 🔹 Método: `cancel_job`
  - 🔹 Método: `get_active_jobs`
  - 🔹 Método: `get_render_statistics`
  - 🔹 Método: `cleanup_old_renders`

---

### 📄 `app\services\scheduler.py`

**Estructura del Código:**

---

### 📄 `app\services\__init__.py`

**Estructura del Código:**

---

### 📄 `app\utils\cleanup.py`
**Librerías/Imports:** `app.core.database.upload_sessions, asyncio, datetime.datetime, datetime.timedelta`

**Estructura del Código:**

---

### 📄 `app\utils\file_utils.py`

**Estructura del Código:**

---

### 📄 `app\utils\logging_utils.py`

**Estructura del Código:**

---

### 📄 `app\utils\network_utils.py`

**Estructura del Código:**

---

### 📄 `app\utils\system_monitor.py`
**Librerías/Imports:** `platform, psutil, typing.Any, typing.Dict`

**Estructura del Código:**
- 🏛️ **Clase:** `SystemMonitor`
  - 🔹 Método: `get_system_stats`

---

### 📄 `app\utils\validation_utils.py`

**Estructura del Código:**

---

### 📄 `app\utils\__init__.py`

**Estructura del Código:**

---

### 📄 `app\workers\cleanup_worker.py`

**Estructura del Código:**

---

### 📄 `app\workers\file_sync_worker.py`

**Estructura del Código:**

---

### 📄 `app\workers\monitor_worker.py`

**Estructura del Código:**

---

### 📄 `app\workers\render_worker.py`

**Estructura del Código:**

---

### 📄 `app\workers\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\faltantes.py`
**Librerías/Imports:** `os, pathlib.Path`

**Estructura del Código:**
- ⚡ **Función:** `create_file`
  - *Descripción:* Crear archivo con contenido
- ⚡ **Función:** `main`

---

### 📄 `backend\fix_all.py`
**Librerías/Imports:** `os, re`

**Estructura del Código:**
- ⚡ **Función:** `fix_pydantic_issues`
  - *Descripción:* Arregla todos los problemas de compatibilidad de Pydantic

---

### 📄 `backend\main.py`
**Librerías/Imports:** `app.services.notification_service.notification_service, asyncio, datetime.datetime, datetime.timedelta, fastapi.BackgroundTasks, fastapi.FastAPI, fastapi.File, fastapi.Form, fastapi.HTTPException, fastapi.UploadFile, fastapi.middleware.cors.CORSMiddleware, fastapi.responses.FileResponse, fastapi.responses.JSONResponse, fastapi.responses.Response, fastapi.responses.StreamingResponse, fastapi.staticfiles.StaticFiles, glob, hashlib, io.BytesIO, json, os, pathlib.Path, platform, psutil, pydantic.BaseModel, re, shutil, subprocess, sys, tempfile, typing.Any, typing.Dict, typing.List, typing.Optional, uuid, uvicorn, zipfile`

**Estructura del Código:**
- 🏛️ **Clase:** `QueueConfig`
- 🏛️ **Clase:** `BlenderTestRequest`
- 🏛️ **Clase:** `BlenderDetectedVersion`
- 🏛️ **Clase:** `SystemInfo`
- 🏛️ **Clase:** `UserInfo`
- 🏛️ **Clase:** `BlenderConfigUpdate`
- 🏛️ **Clase:** `NodeInfo`
- 🏛️ **Clase:** `JobAssignment`
- 🏛️ **Clase:** `NodeRegistration`
- 🏛️ **Clase:** `JobStatusUpdate`
- ⚡ **Función:** `load_config`
  - *Descripción:* Cargar configuración desde archivo
- ⚡ **Función:** `save_config`
  - *Descripción:* Guardar configuración a archivo
- ⚡ **Función:** `merge_configs`
  - *Descripción:* Merge configuración del usuario con la por defecto
- 🏛️ **Clase:** `JobStatus`
- 🏛️ **Clase:** `NodeStatus`
- ⚡ **Función:** `scan_for_blender`
  - *Descripción:* Escanear sistema buscando instalaciones de Blender
- ⚡ **Función:** `get_current_blender_path`
  - *Descripción:* Obtener el path actual de Blender según configuración
- ⚡ **Función:** `verify_blender_path`
  - *Descripción:* Verificar que un path de Blender funciona
- ⚡ **Función:** `get_blend_file_info`
  - *Descripción:* Extraer información del archivo .blend usando Blender
- ⚡ **Función:** `estimate_render_time`
  - *Descripción:* Estimar tiempo de render basado en configuración
- ⚡ **Función:** `find_blender_executable`
  - *Descripción:* Obtener ejecutable de Blender usando configuración
- ⚡ **Función:** `get_system_stats`
  - *Descripción:* Obtener estadísticas actuales del sistema

---

### 📄 `backend\setup_db.py`
**Librerías/Imports:** `app.core.database.Base, app.core.database.SessionLocal, app.core.database.engine, app.models.job.Job, app.models.node.Node, app.models.user.User, os, passlib.context.CryptContext, sys, traceback`

**Estructura del Código:**
- ⚡ **Función:** `setup_database`

---

### 📄 `backend\setup_initial.py`
**Librerías/Imports:** `app.core.database.Base, app.core.database.SessionLocal, app.core.database.engine, app.models.job.Job, app.models.node.Node, app.models.user.User, os, passlib.context.CryptContext, pathlib.Path, sys`

**Estructura del Código:**
- ⚡ **Función:** `setup_database`
- ⚡ **Función:** `create_directories`

---

### 📄 `backend\test_simple.py`
**Librerías/Imports:** `aiohttp, asyncio, json`

**Estructura del Código:**

---

### 📄 `backend\app\main.py`
**Librerías/Imports:** `app.api.v1.auth, app.api.v1.config, app.api.v1.jobs, app.api.v1.nodes, app.api.v1.notifications, app.api.v1.queue, fastapi.APIRouter, fastapi.FastAPI, os, platform, starlette.middleware.cors.CORSMiddleware, uvicorn`

**Estructura del Código:**
- ⚡ **Función:** `get_system_info`
  - *Descripción:* Endpoint para evitar el error 404 en /api/v1/system/info
    *Decoradores:* @get(...)
- ⚡ **Función:** `get_dashboard_stats`
  - *Descripción:* Endpoint para evitar el error 404 en /api/v1/stats/dashboard
    *Decoradores:* @get(...)
- ⚡ **Función:** `health_check`
  - *Descripción:* Endpoint básico para verificar que el servidor está vivo
    *Decoradores:* @get(...)

---

### 📄 `backend\app\main_working.py`
**Librerías/Imports:** `datetime.datetime, fastapi.APIRouter, fastapi.FastAPI, fastapi.middleware.cors.CORSMiddleware, os, subprocess`

**Estructura del Código:**

---

### 📄 `backend\app\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\api\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\auth.py`
**Librerías/Imports:** `core.database.get_db, fastapi.APIRouter, fastapi.Depends, fastapi.HTTPException, fastapi.security.OAuth2PasswordBearer, fastapi.security.OAuth2PasswordRequestForm, fastapi.status, passlib.context.CryptContext, typing.Any, typing.Dict`

**Estructura del Código:**
- ⚡ **Función:** `verify_password`
  - *Descripción:* Verificar contraseña
- ⚡ **Función:** `get_password_hash`
  - *Descripción:* Generar hash de contraseña
- ⚡ **Función:** `authenticate_user`
  - *Descripción:* Autenticar usuario usando la base de datos en memoria
- ⚡ **Función:** `get_user_by_username`
  - *Descripción:* Obtener usuario por nombre de usuario

---

### 📄 `backend\app\api\v1\config.py`
**Librerías/Imports:** `app.core.config.settings, app.services.blender_service.blender_service, fastapi.APIRouter, fastapi.HTTPException, fastapi.status, os, platform, pydantic.BaseModel, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderConfig`

---

### 📄 `backend\app\api\v1\jobs.py`
**Librerías/Imports:** `app.core.config.settings, app.core.database.add_job_to_queue, app.core.database.cleanup_old_jobs, app.core.database.create_job, app.core.database.delete_job, app.core.database.get_job, app.core.database.get_jobs_by_status, app.core.database.get_queue_statistics, app.core.database.jobs_db, app.core.database.search_jobs, app.core.database.update_job, app.core.database.validate_database_integrity, app.models.job.BlendFileAnalysis, app.models.job.JobCreate, app.models.job.JobExport, app.models.job.JobFilter, app.models.job.JobListResponse, app.models.job.JobResponse, app.models.job.JobSearch, app.models.job.JobUpdate, app.services.blender_service.blender_service, app.services.render_service.render_service, asyncio, csv, datetime.datetime, datetime.timedelta, fastapi.APIRouter, fastapi.BackgroundTasks, fastapi.File, fastapi.Form, fastapi.HTTPException, fastapi.Query, fastapi.UploadFile, fastapi.responses.FileResponse, fastapi.responses.StreamingResponse, io.BytesIO, io.StringIO, json, os, pathlib.Path, re, shutil, typing.Any, typing.Dict, typing.List, typing.Optional, uuid, zipfile`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\nodes.py`
**Librerías/Imports:** `app.core.config.settings, app.core.database.assign_job_to_node, app.core.database.cleanup_offline_nodes, app.core.database.distributed_job_queue, app.core.database.get_available_nodes, app.core.database.get_next_job_from_queue, app.core.database.get_nodes_statistics, app.core.database.get_queue_statistics, app.core.database.job_assignments, app.core.database.jobs_db, app.core.database.nodes_registry, app.core.database.register_node, app.core.database.update_node_heartbeat, app.models.node.NodeDiagnostic, app.models.node.NodeFilter, app.models.node.NodeHeartbeat, app.models.node.NodeRegistration, app.models.node.NodeResponse, app.models.node.NodeSearch, app.models.node.NodeUpdate, app.models.node.NodesOverview, fastapi.APIRouter, fastapi.Depends, fastapi.File, fastapi.HTTPException, fastapi.Query, fastapi.UploadFile, fastapi.responses.FileResponse, fastapi.responses.JSONResponse, hashlib, platform, shutil, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\notifications.py`
**Librerías/Imports:** `fastapi.APIRouter`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\queue.py`
**Librerías/Imports:** `core.database.add_job_to_queue, core.database.assign_job_to_node, core.database.distributed_job_queue, core.database.get_available_nodes, core.database.get_jobs_by_status, core.database.get_next_job_from_queue, core.database.get_queue_statistics, core.database.jobs_db, fastapi.APIRouter, fastapi.HTTPException, fastapi.status, typing.Any, typing.Dict, typing.List`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\settings.py`
**Librerías/Imports:** `core.config.settings, fastapi.APIRouter`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\system.py`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\upload.py`

**Estructura del Código:**

---

### 📄 `backend\app\api\v1\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\core\config.py`
**Librerías/Imports:** `os, pydantic.AnyHttpUrl, pydantic.field_validator, pydantic_settings.BaseSettings, typing.Any, typing.Dict, typing.List, typing.Union`

**Estructura del Código:**
- 🏛️ **Clase:** `Settings`
  - 🔹 Método: `assemble_cors_origins`
  - 🔹 Método: `get_blender_config`
  - 🔹 Método: `update_blender_config`
  - 🔹 Método: `_update_env_file`

---

### 📄 `backend\app\core\database.py`
**Librerías/Imports:** `app.core.config.settings, collections.defaultdict, datetime.datetime, datetime.timedelta, logging, os, pathlib.Path, platform, shutil, sqlalchemy.create_engine, sqlalchemy.ext.declarative.declarative_base, sqlalchemy.orm.sessionmaker, typing.Any, typing.Dict, typing.List, uuid`

**Estructura del Código:**
- ⚡ **Función:** `init_directories`
  - *Descripción:* Inicializar directorios necesarios
- ⚡ **Función:** `init_database`
  - *Descripción:* Inicializar base de datos en memoria con valores por defecto
- ⚡ **Función:** `create_job`
  - *Descripción:* Crear un nuevo trabajo en la base de datos
- ⚡ **Función:** `get_job`
  - *Descripción:* Obtener trabajo por ID
- ⚡ **Función:** `update_job`
  - *Descripción:* Actualizar trabajo existente
- ⚡ **Función:** `delete_job`
  - *Descripción:* Eliminar trabajo de la base de datos
- ⚡ **Función:** `get_jobs_by_status`
  - *Descripción:* Obtener trabajos por estado
- ⚡ **Función:** `get_jobs_by_user`
  - *Descripción:* Obtener trabajos de un usuario específico
- ⚡ **Función:** `register_node`
  - *Descripción:* Registrar un nuevo nodo
- ⚡ **Función:** `update_node_heartbeat`
  - *Descripción:* Actualizar heartbeat de un nodo
- ⚡ **Función:** `get_available_nodes`
  - *Descripción:* Obtener nodos disponibles para asignar trabajos
- ⚡ **Función:** `cleanup_offline_nodes`
  - *Descripción:* Limpiar nodos que están offline
- ⚡ **Función:** `add_job_to_queue`
  - *Descripción:* Añadir trabajo a la cola distribuida
- ⚡ **Función:** `get_next_job_from_queue`
  - *Descripción:* Obtener siguiente trabajo de la cola
- ⚡ **Función:** `assign_job_to_node`
  - *Descripción:* Asignar trabajo a un nodo específico
- ⚡ **Función:** `create_upload_session`
  - *Descripción:* Crear sesión de upload por chunks
- ⚡ **Función:** `update_upload_session`
  - *Descripción:* Actualizar progreso de sesión de upload
- ⚡ **Función:** `cleanup_expired_sessions`
  - *Descripción:* Limpiar sesiones expiradas
- ⚡ **Función:** `get_queue_statistics`
  - *Descripción:* Obtener estadísticas de la cola de render
- ⚡ **Función:** `get_nodes_statistics`
  - *Descripción:* Obtener estadísticas de los nodos
- ⚡ **Función:** `get_system_statistics`
  - *Descripción:* Obtener estadísticas generales del sistema
- ⚡ **Función:** `format_duration`
  - *Descripción:* Formatear duración en formato legible
- ⚡ **Función:** `export_database_state`
  - *Descripción:* Exportar estado actual de la base de datos
- ⚡ **Función:** `import_database_state`
  - *Descripción:* Importar estado de la base de datos
- ⚡ **Función:** `search_jobs`
  - *Descripción:* Buscar trabajos por criterios
- ⚡ **Función:** `get_jobs_summary_by_date`
  - *Descripción:* Obtener resumen de trabajos por fecha
- ⚡ **Función:** `cleanup_old_jobs`
  - *Descripción:* Limpiar trabajos antiguos completados/fallidos
- ⚡ **Función:** `validate_database_integrity`
  - *Descripción:* Validar integridad de la base de datos
- ⚡ **Función:** `get_db`
  - *Descripción:* Función de dependencia para FastAPI - retorna el contexto de base de datos

---

### 📄 `backend\app\core\exceptions.py`

**Estructura del Código:**

---

### 📄 `backend\app\core\security.py`

**Estructura del Código:**

---

### 📄 `backend\app\core\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\models\job.py`
**Librerías/Imports:** `datetime.datetime, enum.Enum, pydantic.BaseModel, pydantic.Field, pydantic.validator, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `JobStatus`
  - *Descripción:* Estados posibles de un trabajo de render
- 🏛️ **Clase:** `RenderEngine`
  - *Descripción:* Motores de render soportados
- 🏛️ **Clase:** `JobPriority`
  - *Descripción:* Niveles de prioridad de trabajos
- 🏛️ **Clase:** `DistributionType`
  - *Descripción:* Tipos de distribución de trabajos
- 🏛️ **Clase:** `JobCreate`
  - *Descripción:* Modelo para crear un nuevo trabajo
  - 🔹 Método: `validate_frame_range`
  - 🔹 Método: `validate_tags`
- 🏛️ **Clase:** `JobUpdate`
  - *Descripción:* Modelo para actualizar un trabajo existente
- 🏛️ **Clase:** `JobResponse`
  - *Descripción:* Modelo de respuesta para trabajos
- 🏛️ **Clase:** `JobStatistics`
  - *Descripción:* Estadísticas de un trabajo
- 🏛️ **Clase:** `JobProgress`
  - *Descripción:* Progreso detallado de un trabajo
- 🏛️ **Clase:** `JobQueue`
  - *Descripción:* Información de posición en cola
- 🏛️ **Clase:** `CyclesSettings`
  - *Descripción:* Configuraciones específicas para Cycles
- 🏛️ **Clase:** `EeveeSettings`
  - *Descripción:* Configuraciones específicas para Eevee
- 🏛️ **Clase:** `RenderSettings`
  - *Descripción:* Configuraciones generales de render
- 🏛️ **Clase:** `JobFilter`
  - *Descripción:* Filtros para búsqueda de trabajos
- 🏛️ **Clase:** `JobSearch`
  - *Descripción:* Parámetros de búsqueda de trabajos
- 🏛️ **Clase:** `JobListResponse`
  - *Descripción:* Respuesta paginada de lista de trabajos
- 🏛️ **Clase:** `BlendFileInfo`
  - *Descripción:* Información extraída de un archivo .blend
- 🏛️ **Clase:** `BlendFileAnalysis`
  - *Descripción:* Análisis completo de un archivo .blend
- 🏛️ **Clase:** `JobNotification`
  - *Descripción:* Notificación de estado de trabajo
- 🏛️ **Clase:** `JobExport`
  - *Descripción:* Configuración para exportar trabajos
- 🏛️ **Clase:** `JobImport`
  - *Descripción:* Configuración para importar trabajos
- ⚡ **Función:** `validate_job_data`
  - *Descripción:* Validar datos de trabajo antes de crear
- ⚡ **Función:** `estimate_job_complexity`
  - *Descripción:* Estimar complejidad de un trabajo (0-10)

---

### 📄 `backend\app\models\node.py`
**Librerías/Imports:** `datetime.datetime, enum.Enum, pydantic.BaseModel, pydantic.Field, pydantic.validator, typing.Any, typing.Dict, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NodeStatus`
  - *Descripción:* Estados posibles de un nodo
- 🏛️ **Clase:** `NodePlatform`
  - *Descripción:* Plataformas soportadas
- 🏛️ **Clase:** `NodeCapabilityType`
  - *Descripción:* Tipos de capacidades de nodo
- 🏛️ **Clase:** `GPUType`
  - *Descripción:* Tipos de GPU soportadas
- 🏛️ **Clase:** `SystemStats`
  - *Descripción:* Estadísticas del sistema del nodo
- 🏛️ **Clase:** `NodeInfo`
  - *Descripción:* Información estática del nodo
  - 🔹 Método: `logical_cores_gte_physical`
- 🏛️ **Clase:** `NodeCapabilities`
  - *Descripción:* Capacidades del nodo
  - 🔹 Método: `validate_engines`
- 🏛️ **Clase:** `NodeRegistration`
  - *Descripción:* Datos para registrar un nuevo nodo
  - 🔹 Método: `validate_tags`
- 🏛️ **Clase:** `NodeHeartbeat`
  - *Descripción:* Datos del heartbeat de un nodo
- 🏛️ **Clase:** `NodeResponse`
  - *Descripción:* Respuesta completa de información del nodo
- 🏛️ **Clase:** `JobAssignment`
  - *Descripción:* Asignación de trabajo a nodo
- 🏛️ **Clase:** `NodeWorkload`
  - *Descripción:* Carga de trabajo actual del nodo
- 🏛️ **Clase:** `NodeConfig`
  - *Descripción:* Configuración de un nodo
- 🏛️ **Clase:** `NodeUpdate`
  - *Descripción:* Actualización de configuración de nodo
- 🏛️ **Clase:** `NodeStatistics`
  - *Descripción:* Estadísticas detalladas del nodo
- 🏛️ **Clase:** `NodesOverview`
  - *Descripción:* Vista general de todos los nodos
- 🏛️ **Clase:** `NodePerformance`
  - *Descripción:* Métricas de rendimiento de nodo
- 🏛️ **Clase:** `NodeFilter`
  - *Descripción:* Filtros para búsqueda de nodos
- 🏛️ **Clase:** `NodeSearch`
  - *Descripción:* Parámetros de búsqueda de nodos
- 🏛️ **Clase:** `NodeMaintenance`
  - *Descripción:* Programar mantenimiento de nodo
- 🏛️ **Clase:** `NodeDiagnostic`
  - *Descripción:* Diagnóstico de nodo
- ⚡ **Función:** `validate_node_requirements`
  - *Descripción:* Validar que un nodo cumple los requisitos mínimos
- ⚡ **Función:** `calculate_node_score`
  - *Descripción:* Calcular puntuación global del nodo (0-100)
- ⚡ **Función:** `find_best_node_for_job`
  - *Descripción:* Encontrar el mejor nodo para un trabajo específico

---

### 📄 `backend\app\models\notification.py`

**Estructura del Código:**

---

### 📄 `backend\app\models\render_settings.py`

**Estructura del Código:**

---

### 📄 `backend\app\models\user.py`
**Librerías/Imports:** `core.database.Base, sqlalchemy.Boolean, sqlalchemy.Column, sqlalchemy.DateTime, sqlalchemy.Integer, sqlalchemy.String, sqlalchemy.sql.func`

**Estructura del Código:**
- 🏛️ **Clase:** `User`

---

### 📄 `backend\app\models\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\schemas\job_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `JobCreate`
- 🏛️ **Clase:** `JobResponse`

---

### 📄 `backend\app\schemas\node_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NodeCreate`
- 🏛️ **Clase:** `NodeStats`
- 🏛️ **Clase:** `NodeResponse`

---

### 📄 `backend\app\schemas\notification_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.EmailStr, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `NotificationBase`
- 🏛️ **Clase:** `NotificationCreate`
- 🏛️ **Clase:** `NotificationResponse`

---

### 📄 `backend\app\schemas\user_schemas.py`
**Librerías/Imports:** `datetime.datetime, pydantic.BaseModel, pydantic.EmailStr, pydantic.Field, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `UserCreate`
- 🏛️ **Clase:** `UserResponse`
- 🏛️ **Clase:** `Token`

---

### 📄 `backend\app\schemas\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\blender_service.py`
**Librerías/Imports:** `app.core.config.settings, datetime.datetime, json, logging, os, pathlib.Path, platform, re, shutil, string, subprocess, time, typing.Dict, typing.List, typing.Optional, winreg`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderService`
  - *Descripción:* Servicio para gestión de Blender y análisis de archivos .blend
  - 🔹 Método: `__init__`
  - 🔹 Método: `scan_for_blender`
  - 🔹 Método: `_verify_blender_installation`
  - 🔹 Método: `get_current_blender_path`
  - 🔹 Método: `verify_blender_path`
  - 🔹 Método: `get_blend_file_info`
  - 🔹 Método: `estimate_render_time`
  - 🔹 Método: `_format_time_duration`
  - 🔹 Método: `validate_blend_file`
  - 🔹 Método: `get_recommended_settings`
  - 🔹 Método: `auto_detect_and_configure`
  - 🔹 Método: `test_render_capability`
  - 🔹 Método: `clear_cache`

---

### 📄 `backend\app\services\file_service.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\file_transfer.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\node_monitor.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\node_service.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\notification_service.py`
**Error de Sintaxis al leer este archivo**

---

### 📄 `backend\app\services\preview_generator.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\queue_manager.py`
**Librerías/Imports:** `asyncio, core.database.SessionLocal, datetime.datetime, models.job.Job, models.job.JobStatus, models.node.Node, sqlalchemy.orm.Session, typing.List, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `QueueManager`
  - 🔹 Método: `__init__`

---

### 📄 `backend\app\services\render_engine.py`
**Librerías/Imports:** `asyncio, core.config.settings, json, os, pathlib.Path, subprocess, typing.Any, typing.Dict, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `BlenderRenderer`
  - 🔹 Método: `__init__`
  - 🔹 Método: `_build_render_args`
  - 🔹 Método: `_create_temp_script`

---

### 📄 `backend\app\services\render_service.py`
**Librerías/Imports:** `app.core.config.settings, app.core.database.jobs_db, app.core.database.nodes_db, app.core.database.update_job, app.services.blender_service.blender_service, app.utils.system_monitor.system_monitor, asyncio, datetime.datetime, datetime.timedelta, logging, os, pathlib.Path, platform, re, shutil, subprocess, typing.Any, typing.Callable, typing.Dict, typing.Optional`

**Estructura del Código:**
- 🏛️ **Clase:** `RenderService`
  - *Descripción:* Servicio principal de renderización
  - 🔹 Método: `__init__`
  - 🔹 Método: `_prepare_render_config`
  - 🔹 Método: `_get_engine_specific_args`
  - 🔹 Método: `_parse_frame_completion`
  - 🔹 Método: `_evaluate_render_result`
  - 🔹 Método: `_find_rendered_files`
  - 🔹 Método: `cancel_job`
  - 🔹 Método: `get_active_jobs`
  - 🔹 Método: `get_render_statistics`
  - 🔹 Método: `cleanup_old_renders`

---

### 📄 `backend\app\services\scheduler.py`

**Estructura del Código:**

---

### 📄 `backend\app\services\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\utils\cleanup.py`
**Librerías/Imports:** `app.core.database.upload_sessions, asyncio, datetime.datetime, datetime.timedelta`

**Estructura del Código:**

---

### 📄 `backend\app\utils\file_utils.py`

**Estructura del Código:**

---

### 📄 `backend\app\utils\logging_utils.py`

**Estructura del Código:**

---

### 📄 `backend\app\utils\network_utils.py`

**Estructura del Código:**

---

### 📄 `backend\app\utils\system_monitor.py`
**Librerías/Imports:** `platform, psutil, typing.Any, typing.Dict`

**Estructura del Código:**
- 🏛️ **Clase:** `SystemMonitor`
  - 🔹 Método: `get_system_stats`

---

### 📄 `backend\app\utils\validation_utils.py`

**Estructura del Código:**

---

### 📄 `backend\app\utils\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\app\workers\cleanup_worker.py`

**Estructura del Código:**

---

### 📄 `backend\app\workers\file_sync_worker.py`

**Estructura del Código:**

---

### 📄 `backend\app\workers\monitor_worker.py`

**Estructura del Código:**

---

### 📄 `backend\app\workers\render_worker.py`

**Estructura del Código:**

---

### 📄 `backend\app\workers\__init__.py`

**Estructura del Código:**

---

### 📄 `backend\core\config.py`
**Librerías/Imports:** `pydantic_settings.BaseSettings`

**Estructura del Código:**
- 🏛️ **Clase:** `Settings`

---

### 📄 `backend\scripts\backup_db.py`

**Estructura del Código:**

---

### 📄 `backend\scripts\health_check.py`

**Estructura del Código:**

---

### 📄 `backend\scripts\migrate_db.py`

**Estructura del Código:**

---

### 📄 `backend\scripts\setup_master.py`
**Error de Sintaxis al leer este archivo**

---

### 📄 `backend\scripts\setup_node.py`

**Estructura del Código:**

---

### 📄 `backend\tests\test_api.py`

**Estructura del Código:**

---

### 📄 `backend\tests\test_models.py`

**Estructura del Código:**

---

### 📄 `backend\tests\test_services.py`

**Estructura del Código:**

---

### 📄 `backend\tests\test_workers.py`

**Estructura del Código:**

---

### 📄 `backend\tests\__init__.py`

**Estructura del Código:**

---

### 📄 `blender_addon\addon_prefs.py`

**Estructura del Código:**

---

### 📄 `blender_addon\preferences.py`

**Estructura del Código:**

---

### 📄 `blender_addon\__init__.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\api_client.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\file_manager.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\job_submit.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\scene_export.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\settings_manager.py`

**Estructura del Código:**

---

### 📄 `blender_addon\core\__init__.py`

**Estructura del Código:**

---

### 📄 `blender_addon\ui\menus.py`

**Estructura del Código:**

---

### 📄 `blender_addon\ui\operators.py`

**Estructura del Código:**

---

### 📄 `blender_addon\ui\panels.py`

**Estructura del Código:**

---

### 📄 `blender_addon\ui\properties.py`

**Estructura del Código:**

---

### 📄 `blender_addon\ui\__init__.py`

**Estructura del Código:**

---

### 📄 `blender_addon\utils\constants.py`

**Estructura del Código:**

---

### 📄 `blender_addon\utils\helpers.py`

**Estructura del Código:**

---

### 📄 `blender_addon\utils\validation.py`

**Estructura del Código:**

---

### 📄 `blender_addon\utils\__init__.py`

**Estructura del Código:**

---

### 📄 `frontend\create_advanced_components.py`
**Librerías/Imports:** `os, pathlib.Path, subprocess`

**Estructura del Código:**
- ⚡ **Función:** `create_file`
  - *Descripción:* Crear archivo con contenido
- ⚡ **Función:** `create_advanced_components`
  - *Descripción:* Crear componentes avanzados
- ⚡ **Función:** `install_additional_dependencies`
  - *Descripción:* Instalar dependencias adicionales
- ⚡ **Función:** `main`
  - *Descripción:* Función principal

---

### 📄 `frontend\dark_theme_auth_system.py`
**Librerías/Imports:** `os, pathlib.Path`

**Estructura del Código:**
- ⚡ **Función:** `create_file`
  - *Descripción:* Crear archivo con contenido
- ⚡ **Función:** `update_styles_dark_theme`
  - *Descripción:* Actualizar estilos a tema oscuro
- ⚡ **Función:** `create_auth_store`
  - *Descripción:* Crear store de autenticación
- ⚡ **Función:** `create_login_page`
  - *Descripción:* Crear página de login mejorada
- ⚡ **Función:** `create_layout_component`
  - *Descripción:* Crear componente Layout con tema oscuro
- ⚡ **Función:** `update_router_with_auth`
  - *Descripción:* Actualizar router con guards de autenticación
- ⚡ **Función:** `update_dashboard_dark_theme`
  - *Descripción:* Actualizar Dashboard con tema oscuro
- ⚡ **Función:** `update_stats_card_dark`
  - *Descripción:* Actualizar StatsCard para tema oscuro
- ⚡ **Función:** `update_app_vue`
  - *Descripción:* Actualizar App.vue
- ⚡ **Función:** `update_main_js`
  - *Descripción:* Actualizar main.js con Pinia
- ⚡ **Función:** `main`
  - *Descripción:* Función principal

---

### 📄 `frontend\setup_frontend.py`
**Librerías/Imports:** `os, pathlib.Path`

**Estructura del Código:**
- ⚡ **Función:** `create_file`
  - *Descripción:* Crear archivo con contenido
- ⚡ **Función:** `update_styles_dark_theme`
  - *Descripción:* Actualizar estilos a tema oscuro
- ⚡ **Función:** `create_auth_store`
  - *Descripción:* Crear store de autenticación
- ⚡ **Función:** `create_login_page`
  - *Descripción:* Crear página de login mejorada
- ⚡ **Función:** `create_layout_component`
  - *Descripción:* Crear componente Layout con tema oscuro
- ⚡ **Función:** `update_router_with_auth`
  - *Descripción:* Actualizar router con guards de autenticación
- ⚡ **Función:** `update_dashboard_dark_theme`
  - *Descripción:* Actualizar Dashboard con tema oscuro
- ⚡ **Función:** `update_stats_card_dark`
  - *Descripción:* Actualizar StatsCard para tema oscuro
- ⚡ **Función:** `update_app_vue`
  - *Descripción:* Actualizar App.vue
- ⚡ **Función:** `update_main_js`
  - *Descripción:* Actualizar main.js con Pinia
- ⚡ **Función:** `main`
  - *Descripción:* Función principal

---

### 📄 `node_client\api_client.py`

**Estructura del Código:**

---

### 📄 `node_client\file_manager.py`

**Estructura del Código:**

---

### 📄 `node_client\health_checker.py`

**Estructura del Código:**

---

### 📄 `node_client\log_manager.py`

**Estructura del Código:**

---

### 📄 `node_client\node_agent.py`
**Librerías/Imports:** `GPUtil, aiohttp, asyncio, dataclasses.asdict, dataclasses.dataclass, datetime.datetime, hashlib, json, logging, os, pathlib.Path, platform, psutil, shutil, signal, subprocess, sys, time, traceback, typing.Any, typing.Dict, typing.Optional, uuid, yaml, zipfile`

**Estructura del Código:**
- 🏛️ **Clase:** `NodeConfig`
  - *Descripción:* Configuración del nodo de render
  - 🔹 Método: `__post_init__`
- 🏛️ **Clase:** `SystemStats`
  - *Descripción:* Estadísticas del sistema del nodo
  - 🔹 Método: `__post_init__`
- 🏛️ **Clase:** `JobStatus`
  - *Descripción:* Estado de un trabajo en el nodo
  - 🔹 Método: `__post_init__`
- 🏛️ **Clase:** `SystemMonitor`
  - *Descripción:* Monitor de recursos del sistema
  - 🔹 Método: `get_system_stats`
- 🏛️ **Clase:** `FileTransferManager`
  - *Descripción:* Gestor de transferencia de archivos con el master - VERSIÓN DEFINITIVA
  - 🔹 Método: `__init__`
  - 🔹 Método: `cleanup_job_files`
- 🏛️ **Clase:** `RenderExecutor`
  - *Descripción:* Ejecutor de renders usando Blender - VERSIÓN DEFINITIVA
  - 🔹 Método: `__init__`
  - 🔹 Método: `create_gpu_script`
  - 🔹 Método: `cancel_current_render`
- 🏛️ **Clase:** `RenderNode`
  - *Descripción:* Nodo de render principal - VERSIÓN DEFINITIVA
  - 🔹 Método: `__init__`
  - 🔹 Método: `_setup_signal_handlers`
  - 🔹 Método: `_load_config`
  - 🔹 Método: `_save_config`
  - 🔹 Método: `_generate_node_id`

---

### 📄 `node_client\render_executor.py`

**Estructura del Código:**

---

### 📄 `node_client\setup.py`

**Estructura del Código:**

---

### 📄 `node_client\system_monitor.py`

**Estructura del Código:**

---

### 📄 `node_client\scripts\install.py`

**Estructura del Código:**

---

### 📄 `node_client\scripts\service_setup.py`

**Estructura del Código:**

---

### 📄 `node_client\scripts\uninstall.py`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\gpu_setup.py`
**Error de Sintaxis al leer este archivo**

---

### 📄 `node_client\temp_node\43af92b8-95aa-40bc-b280-8201fd7ae1f0\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\45eb0126-cac1-48e2-b76c-adb78053e3f1\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\5ec33524-c790-4ff7-b1cf-b179453bdad1\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\6caf0db0-9cd0-47da-aa64-2e30fbc5c618\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\796806b9-fd0b-45a0-855c-bb119ca6f2a6\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\a2df77f0-55ea-4fc8-ace3-4ea91f4ad061\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\acd1f6ed-ed3e-4d31-9a7a-94f63654435c\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\cb96f05e-8514-40f9-8977-b0129cb6e5b7\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\e1cb2aa0-ec15-451f-926a-31458fb489ef\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\f2d294e9-7867-45d7-ad90-8a5deb1d4bab\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\temp_node\fb62a067-7448-4e12-8deb-a841b8ab2b2f\gpu_setup.py`
**Librerías/Imports:** `bpy`

**Estructura del Código:**

---

### 📄 `node_client\utils\file_utils.py`

**Estructura del Código:**

---

### 📄 `node_client\utils\network_utils.py`

**Estructura del Código:**

---

### 📄 `node_client\utils\system_utils.py`

**Estructura del Código:**

---

### 📄 `notification_services\notification_manager.py`

**Estructura del Código:**

---

### 📄 `notification_services\__init__.py`

**Estructura del Código:**

---

### 📄 `notification_services\email\attachment_handler.py`

**Estructura del Código:**

---

### 📄 `notification_services\email\email_client.py`

**Estructura del Código:**

---

### 📄 `notification_services\email\__init__.py`

**Estructura del Código:**

---

### 📄 `notification_services\slack\slack_client.py`

**Estructura del Código:**

---

### 📄 `notification_services\slack\webhook_handler.py`

**Estructura del Código:**

---

### 📄 `notification_services\slack\__init__.py`

**Estructura del Código:**

---

### 📄 `notification_services\telegram\bot_commands.py`

**Estructura del Código:**

---

### 📄 `notification_services\telegram\telegram_client.py`

**Estructura del Código:**

---

### 📄 `notification_services\telegram\__init__.py`

**Estructura del Código:**

---

### 📄 `notification_services\whatsapp\media_handler.py`

**Estructura del Código:**

---

### 📄 `notification_services\whatsapp\message_templates.py`

**Estructura del Código:**

---

### 📄 `notification_services\whatsapp\whatsapp_client.py`

**Estructura del Código:**

---

### 📄 `notification_services\whatsapp\__init__.py`

**Estructura del Código:**

---

### 📄 `scripts\build_addon.py`

**Estructura del Código:**

---

### 📄 `scripts\dev_setup.py`

**Estructura del Código:**

---

### 📄 `scripts\install_dependencies.py`

**Estructura del Código:**

---

### 📄 `scripts\migrate_data.py`

**Estructura del Código:**

---

### 📄 `scripts\package_release.py`

**Estructura del Código:**

---

### 📄 `scripts\run_tests.py`

**Estructura del Código:**

---

### 📄 `shared\constants.py`

**Estructura del Código:**

---

### 📄 `shared\exceptions.py`

**Estructura del Código:**

---

### 📄 `shared\models.py`

**Estructura del Código:**

---

### 📄 `shared\protocols.py`

**Estructura del Código:**

---

### 📄 `shared\schemas.py`

**Estructura del Código:**

---

### 📄 `shared\utils.py`

**Estructura del Código:**

---

### 📄 `shared\__init__.py`

**Estructura del Código:**

---

### 📄 `tests\backend\test_api.py`

**Estructura del Código:**

---

### 📄 `tests\backend\test_models.py`

**Estructura del Código:**

---

### 📄 `tests\backend\test_services.py`

**Estructura del Código:**

---

### 📄 `tests\backend\test_workers.py`

**Estructura del Código:**

---

### 📄 `tests\backend\__init__.py`

**Estructura del Código:**

---

### 📄 `tests\e2e\test_addon_integration.py`

**Estructura del Código:**

---

### 📄 `tests\e2e\test_user_flows.py`

**Estructura del Código:**

---

### 📄 `tests\e2e\__init__.py`

**Estructura del Código:**

---

### 📄 `tests\integration\test_full_workflow.py`

**Estructura del Código:**

---

### 📄 `tests\integration\test_node_communication.py`

**Estructura del Código:**

---

### 📄 `tests\integration\test_notifications.py`

**Estructura del Código:**

---

### 📄 `tests\integration\__init__.py`

**Estructura del Código:**

---

### 📄 `tests\performance\test_queue_performance.py`

**Estructura del Código:**

---

### 📄 `tests\performance\test_render_performance.py`

**Estructura del Código:**

---

### 📄 `tests\performance\__init__.py`

**Estructura del Código:**

---
