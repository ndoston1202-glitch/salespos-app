@echo off
cd /d "%~dp0"
title SalesPOS - To'xtatilmoqda...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq SalesPOS Server" /F >nul 2>&1
echo  SalesPOS to'xtatildi.
timeout /t 2 /nobreak >nul
exit
