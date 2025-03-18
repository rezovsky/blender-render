@echo off
cd /d %~dp0

echo === Проверка наличия Python ===
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден. Скачиваем и устанавливаем...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python установлен. Продолжаем...
) else (
    echo Python уже установлен.
)

echo === Проверка наличия Node.js ===
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js не найден. Скачиваем и устанавливаем...
    powershell -Command "Invoke-WebRequest -Uri https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi -OutFile node-installer.msi"
    start /wait msiexec /i node-installer.msi /quiet /norestart
    del node-installer.msi
    echo Node.js установлен. Перезапускаем скрипт для обновления PATH...
    timeout /t 2 >nul
    start "" "%~f0"
    exit /b
) else (
    echo Node.js уже установлен.
)

echo === Создание виртуального окружения ===
python -m venv venv

echo === Активация виртуального окружения и установка Python-зависимостей ===
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo === Установка frontend-зависимостей и сборка фронтенда ===
cd web
call npm install
call npm run build
cd ..

echo === Всё готово! Установка завершена. ===
pause
