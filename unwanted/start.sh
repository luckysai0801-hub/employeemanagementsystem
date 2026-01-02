#!/bin/bash
# Startup script for Employee Management System (Linux/Mac version)

echo "================================"
echo "Employee Management System Startup"
echo "================================"
echo ""

# Check if MongoDB is running
echo "Checking MongoDB connection..."
timeout 2 python3 -c "from pymongo import MongoClient; MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000).admin.command('ismaster')" >/dev/null 2>&1

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: MongoDB is not running!"
    echo ""
    echo "Please start MongoDB:"
    echo "  Linux: sudo systemctl start mongod"
    echo "  Mac: brew services start mongodb-community"
    echo "  Or run: mongod"
    echo ""
    exit 1
fi

echo "MongoDB is running. ✓"
echo ""

# Start Backend
echo "Starting Backend Server..."
cd backend
python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
sleep 2

# Start Frontend
echo "Starting Frontend Server..."
cd ../frontend
npm start &
FRONTEND_PID=$!
sleep 3

echo ""
echo "================================"
echo "Servers are running..."
echo "================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Login with:"
echo "  Username: phanendra"
echo "  Password: 123456"
echo ""
echo "Press Ctrl+C to stop servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
