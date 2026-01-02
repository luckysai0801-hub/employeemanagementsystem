@echo off
setlocal enabledelayedexpansion

REM Employee Management System - Robust Start Script
REM This script starts both backend and frontend servers reliably

title Employee Management System

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

REM Kill any existing processes on ports 8000 and 3000
echo Cleaning up any existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| find ":3000"') do taskkill /F /PID %%a 2>nul
timeout /t 2 /nobreak

REM Change to project root
cd /d "%~dp0"

REM Start Backend in a new window
echo Starting Backend Server on port 8000...
start "Backend Server" cmd /c "cd backend && python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level info"
timeout /t 4 /nobreak

REM Start Frontend in a new window
echo Starting Frontend Server on port 3000...
start "Frontend Server" cmd /c "cd frontend && npm start"
timeout /t 5 /nobreak

REM Check if servers started
echo.
echo Verifying servers are running...
netstat -ano | find ":8000" >nul
if errorlevel 1 (
    echo WARNING: Backend server may not be running on port 8000
) else (
    echo ✓ Backend server is running on port 8000
)

netstat -ano | find ":3000" >nul
if errorlevel 1 (
    echo WARNING: Frontend server may not be running on port 3000
) else (
    echo ✓ Frontend server is running on port 3000
)

echo.
echo ================================
echo System Startup Complete!
echo ================================
echo.
echo Access the application at:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Login Credentials:
echo   Username: phanendra
echo   Password: 123456
echo.
echo Note: This window will remain open. Do NOT close it!
echo To stop the servers, close the Backend and Frontend windows.
echo.
pause
