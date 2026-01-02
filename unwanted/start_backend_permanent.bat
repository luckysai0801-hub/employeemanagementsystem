@echo off
REM Backend Server Startup Script
REM Starts FastAPI/Uvicorn server without auto-reload for permanent running

cd /d "%~dp0\backend"

echo ================================
echo Starting Backend Server
echo ================================
echo.
echo Server will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

REM Check if MongoDB is running first
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ismaster')" >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: MongoDB is not running!
    echo Please start MongoDB service:
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

REM Start backend without reload (permanent mode)
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level info

REM If we reach here, the server crashed
echo.
echo ERROR: Backend server stopped unexpectedly!
echo Check the error messages above.
echo.
pause
