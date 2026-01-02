@echo off
REM Employee Management System - Final Startup Script
REM Runs backend and frontend in completely separate windows

title Employee Management System Launcher

echo.
echo ================================
echo Employee Management System
echo ================================
echo.

REM Check MongoDB
echo Checking MongoDB connection...
python -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ismaster')" >nul 2>&1

if errorlevel 1 (
    echo ERROR: MongoDB is not running!
    echo.
    echo To start MongoDB:
    echo  1. Press Win+R
    echo  2. Type: services.msc
    echo  3. Find "MongoDB Server"
    echo  4. Right-click and Start
    echo.
    pause
    exit /b 1
)

echo ✓ MongoDB is running
echo.

REM Clean up any existing processes on ports
echo Cleaning up ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000"') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak

REM Start Backend Server
echo.
echo Starting Backend Server (port 8000)...
start "Employee Management - Backend" /D "e:\Employee management system\backend" cmd /c "python -m uvicorn server:app --host 0.0.0.0 --port 8000"
timeout /t 5

REM Start Frontend Server  
echo Starting Frontend Server (port 3000)...
start "Employee Management - Frontend" /D "e:\Employee management system\frontend" cmd /c "npm start"
timeout /t 5

echo.
echo ================================
echo Startup Complete!
echo ================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Username: phanendra
echo Password: 123456
echo.
echo Note: Two new windows will open with the running servers.
echo.
pause
