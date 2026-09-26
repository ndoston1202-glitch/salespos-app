@echo off
cd /d "%~dp0"
title SalesPOS
color 0E

echo ============================================
echo    SalesPOS - KAFE TIZIMI
echo ============================================
echo.

:: Python tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [XATO] Python topilmadi!
    echo  https://www.python.org/downloads/ dan o'rnating
    echo  ("Add Python to PATH" ni belgilang!)
    echo.
    pause
    exit /b 1
)

:: Virtual muhit
if not exist "venv" (
    echo  Birinchi marta - tayyorlanmoqda...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Django o'rnatilganmi
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo  Paketlar o'rnatilmoqda (1 daqiqa)...
    pip install Django==4.2.7 djangorestframework==3.14.0 -q --disable-pip-version-check
)

:: Eski serverni to'xtatish
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

:: Brauzerni 4 soniyadan keyin ochish (fonda)
start "" /b cmd /c "timeout /t 4 /nobreak >nul & start http://localhost:8000"

echo.
echo ============================================
echo    SERVER ISHGA TUSHMOQDA...
echo    Brauzer ochiladi: http://localhost:8000
echo    Login: admin   Parol: admin123
echo.
echo    BU OYNANI YOPMANG! (server shu yerda ishlaydi)
echo ============================================
echo.

:: Serverni SHU oynada ishga tushirish (xato bo'lsa ko'rinadi)
python server.py

:: Agar server to'xtasa (xato), oyna ochiq qoladi
echo.
echo  [!] Server to'xtadi. Yuqoridagi xatoni o'qing.
pause
