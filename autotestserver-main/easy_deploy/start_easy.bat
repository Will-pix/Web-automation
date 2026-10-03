@echo off
setlocal
cd /d %~dp0
docker compose -f docker-compose.easydeploy.yml up -d --build
echo.
echo Easy deploy started.
pause
