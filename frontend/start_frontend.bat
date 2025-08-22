@echo off
echo 🎨 Iniciando Frontend de Render_QM...
echo.

REM Verificar si node_modules existe
if not exist "node_modules" (
    echo 📦 Instalando dependencias...
    npm install
)

echo 🚀 Iniciando servidor de desarrollo...
echo.
echo 🌐 Frontend disponible en:
echo    • URL: http://localhost:3000
echo    • Proxy API: http://localhost:3000/api -> http://localhost:8000/api
echo.
echo ⏹️ Presiona Ctrl+C para detener
echo.

npm run dev

pause