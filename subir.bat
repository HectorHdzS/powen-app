@echo off
echo 🚀 Preparando para subir cambios a la nube...
git add .
set /p mensaje="Escribe tu mensaje para el commit: "
git commit -m "%mensaje%"
git push origin main
echo ✅ ¡Listo! Tu App Powen esta actualizada.
pause
