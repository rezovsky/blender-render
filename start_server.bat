@echo off
cd /d %~dp0

call venv\Scripts\activate

uvicorn main:app --host 0.0.0.0 --port 5000

pause
