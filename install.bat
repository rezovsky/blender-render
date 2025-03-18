@echo off
cd /d %~dp0

echo === �஢�ઠ ������ Python ===
python --version >nul 2>&1
if errorlevel 1 (
    echo Python �� ������. ���稢��� � ��⠭��������...
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
    echo Python ��⠭�����. �த������...
) else (
    echo Python 㦥 ��⠭�����.
)

echo === �஢�ઠ ������ Node.js ===
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js �� ������. ���稢��� � ��⠭��������...
    powershell -Command "Invoke-WebRequest -Uri https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi -OutFile node-installer.msi"
    start /wait msiexec /i node-installer.msi /quiet /norestart
    del node-installer.msi
    echo Node.js ��⠭�����. ��१���᪠�� �ਯ� ��� ���������� PATH...
    timeout /t 2 >nul
    start "" "%~f0"
    exit /b
) else (
    echo Node.js 㦥 ��⠭�����.
)

echo === �������� ����㠫쭮�� ���㦥��� ===
python -m venv venv

echo === ��⨢��� ����㠫쭮�� ���㦥��� � ��⠭���� Python-����ᨬ��⥩ ===
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo === ��⠭���� frontend-����ᨬ��⥩ � ᡮઠ �஭⥭�� ===
cd web
call npm install
call npm run build
cd ..

echo === ��� ��⮢�! ��⠭���� �����襭�. ===
pause
