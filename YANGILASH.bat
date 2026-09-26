@echo off
cd /d "%~dp0"
title SalesPOS - Yangilanmoqda...
color 0B

echo ============================================
echo    SalesPOS - YANGILANMOQDA
echo ============================================
echo.

:: Serverni to'xtatish
echo  [1/4] Server to'xtatilmoqda...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
timeout /t 1 /nobreak >nul

:: GitHub bilan ulash (qotib qolmasin uchun login o'chirilgan)
echo  [2/4] GitHub dan yangi kod yuklanmoqda...
set GIT_TERMINAL_PROMPT=0
git --version >nul 2>&1
if errorlevel 1 (
    echo        (Git yo'q - o'tkazib yuborildi)
) else (
    if not exist ".git" (
        git init -q
        git remote add origin https://github.com/ndoston1202-glitch/salespos.git
    )
    git remote set-url origin https://github.com/ndoston1202-glitch/salespos.git >nul 2>&1
    git fetch origin main -q 2>nul && git reset --hard origin/main -q 2>nul && echo        Yangilandi! || echo        (Yangilanmadi - mavjud kod ishlatiladi)
)

:: Virtual muhit + paketlar
echo  [3/4] Paketlar tekshirilmoqda...
if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo        Paketlar o'rnatilmoqda...
    pip install Django==4.2.7 djangorestframework==3.14.0 -q --disable-pip-version-check
)

:: Serverni qayta ishga tushirish
echo  [4/4] Server ishga tushirilmoqda...
start "SalesPOS Server" /min cmd /c "cd /d "%~dp0" && venv\Scripts\activate && python server.py"
timeout /t 4 /nobreak >nul
start http://localhost:8000

echo.
echo ============================================
echo    YANGILANDI VA ISHGA TUSHDI!
echo    http://localhost:8000
echo    Login: admin   Parol: admin123
echo ============================================
timeout /t 3 /nobreak >nul
exit
