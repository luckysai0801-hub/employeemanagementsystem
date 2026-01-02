@echo off
cd /d "e:\Employee management system\backend"
call "..\.venv\Scripts\activate.bat"
python -m uvicorn server:app --host 127.0.0.1 --port 8001
pause
