# Makefile para Render_QM

.PHONY: help install dev test build clean docker-up docker-down

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	@echo "Instalando dependencias del backend..."
	cd backend && pip install -r requirements.txt
	@echo "Instalando dependencias del frontend..."
	cd frontend && npm install
	@echo "Instalando dependencias del node client..."
	cd node_client && pip install -r requirements.txt

dev: ## Ejecutar en modo desarrollo
	@echo "Iniciando servicios en modo desarrollo..."
	docker-compose up -d db redis
	@echo "Servicios de base de datos iniciados. Ejecuta en terminales separadas:"
	@echo "  Backend: cd backend && uvicorn app.main:app --reload"
	@echo "  Frontend: cd frontend && npm run dev"

test: ## Ejecutar tests
	@echo "Ejecutando tests del backend..."
	cd backend && python -m pytest
	@echo "Ejecutando tests del frontend..."
	cd frontend && npm test

build: ## Construir el proyecto
	@echo "Construyendo backend..."
	cd backend && docker build -t render-qm-backend .
	@echo "Construyendo frontend..."
	cd frontend && npm run build

clean: ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache

docker-up: ## Levantar todos los servicios con Docker
	docker-compose up -d

docker-down: ## Bajar todos los servicios de Docker
	docker-compose down

docker-logs: ## Ver logs de Docker
	docker-compose logs -f

setup-dev: install ## Configurar entorno de desarrollo completo
	@echo "Copiando archivos de configuración..."
	cp .env.example .env
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "Configuración completada. Edita los archivos .env según tu entorno."

addon-build: ## Construir addon de Blender
	@echo "Construyendo addon de Blender..."
	cd blender_addon && zip -r ../render_qm_addon.zip . -x "*.pyc" "*__pycache__*"
	@echo "Addon creado: render_qm_addon.zip"

docs: ## Generar documentación
	@echo "Generando documentación..."
	# Aquí se puede agregar generación de docs automática

lint: ## Ejecutar linters
	@echo "Ejecutando linters..."
	cd backend && flake8 app/
	cd frontend && npm run lint

format: ## Formatear código
	@echo "Formateando código..."
	cd backend && black app/
	cd frontend && npm run format
