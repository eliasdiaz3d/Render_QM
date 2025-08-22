@echo off
echo 🚀 Iniciando Render_QM Backend...
echo.

REM Crear directorios
if not exist "temp" mkdir temp
if not exist "renders" mkdir renders
if not exist "logs" mkdir logs

REM Configurar base de datos
echo 🗄️ Configurando base de datos...
python setup_db.py

echo.
echo 🌐 Servidor disponible en:
echo    • API: http://localhost:8000
echo    • Docs: http://localhost:8000/docs
echo    • Health: http://localhost:8000/health
echo.
echo 👤 Credenciales:
echo    • Usuario: admin
echo    • Contraseña: admin123
echo.
echo ⏹️ Presiona Ctrl+C para detener
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
