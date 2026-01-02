@echo off
REM Employee Management System - Start Script
REM This script starts both the backend and frontend servers

echo ================================
echo Employee Management System Startup
echo ================================
echo.

REM Check if MongoDB is running
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ismaster')" >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: MongoDB is not running!
    echo.
    echo Please install MongoDB from: https://www.mongodb.com/try/download/community
    echo Or if already installed, start the MongoDB service:
    echo   - Press Win+R
    echo   - Type: services.msc
    echo   - Find "MongoDB Server"
    echo   - Right-click and select "Start"
    echo.
    pause
    exit /b 1
)

echo MongoDB is running. ✓
echo.

REM Start Backend
echo Starting Backend Server (permanent mode - no auto-reload)...
start cmd /k "cd /d backend && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level info"
timeout /t 3 /nobreak

REM Start Frontend
echo Starting Frontend Server...
start cmd /k "cd /d frontend && npm start"
timeout /t 3 /nobreak

echo.
echo ================================
echo Servers are starting...
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Login with:
echo   Username: phanendra
echo   Password: 123456
echo.
pause
