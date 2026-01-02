# 🚀 Employee Management System - Quick Start Guide

## ✅ Current Status
- **Backend**: Running on http://localhost:8000 ✓
- **Frontend**: Running on http://localhost:3000 ✓
- **Database**: MongoDB Connected ✓
- **Login**: Ready to use ✓

---

## 📋 How to Start the System

### **Option 1: Double-Click (RECOMMENDED)**
1. Open File Explorer
2. Navigate to: `e:\Employee management system`
3. **Double-click** `run.bat`
4. Wait 10 seconds for servers to start
5. Two command windows will open (don't close them!)
6. Open browser to: **http://localhost:3000**

### **Option 2: From Command Prompt**
```cmd
cd e:\Employee management system
run.bat
```

---

## 🔐 Login Credentials
- **Username:** `phanendra`
- **Password:** `123456`

---

## 🌐 Access URLs
| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Main application |
| Backend API | http://localhost:8000 | API endpoints |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| Health Check | http://localhost:8000/health | Server status |

---

## 🛑 How to Stop

### Method 1: Close Command Windows
- Close both the "Backend" and "Frontend" command windows

### Method 2: Task Manager
- Press `Ctrl + Shift + Esc`
- Find `python.exe` → Right-click → End Task
- Find `node.exe` → Right-click → End Task

### Method 3: Command Prompt
```cmd
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## ⚠️ If Login Fails

### Check Backend is Running
```cmd
netstat -ano | find ":8000"
```
Should show: `TCP    0.0.0.0:8000           LISTENING`

### Check Frontend is Running
```cmd
netstat -ano | find ":3000"
```
Should show: `TCP    0.0.0.0:3000           LISTENING`

### Check MongoDB
1. Press `Win + R`
2. Type: `services.msc`
3. Find "MongoDB Server" 
4. Ensure it says "Running"

### Clear Browser Cache
- Press `Ctrl + Shift + Delete`
- Clear all data
- Try login again

---

## 📁 Project Structure
```
Employee management system/
├── backend/                    # FastAPI server
│   ├── server.py             # Main application
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Configuration
│   └── uploads/               # File storage
├── frontend/                   # React app
│   ├── src/
│   │   ├── pages/            # Login, Dashboard, Employee List
│   │   ├── components/       # Reusable components
│   │   └── styles/           # CSS files
│   ├── package.json          # Node dependencies
│   └── public/               # Static files
├── run.bat                    # ⭐ Main startup script
├── start.bat                  # Alternative startup
└── README.md                  # Full documentation
```

---

## ✨ Features

### Dashboard
- View total employees
- See active employee count
- Department statistics
- Average salary calculation
- Recent activities

### Employee Management
- Add new employees
- View employee list with pagination
- Search and filter employees
- Update employee details
- Delete employees (soft delete)

### Exports
- Export to CSV
- Export to Excel
- Export to PDF

### Security
- JWT authentication
- Password hashing with bcrypt
- Account lockout after failed attempts
- Audit logging

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 already in use | `taskkill /F /PID <pid>` |
| Port 3000 already in use | `taskkill /F /PID <pid>` |
| MongoDB not found | Install from https://www.mongodb.com/try/download/community |
| Login credentials not working | Verify user in MongoDB or restart backend |
| CORS errors | Backend CORS is set to allow all origins (*) |
| npm install errors | Use `npm install --legacy-peer-deps` |

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - User logout

### Employees
- `GET /api/employees/list` - Get all employees
- `POST /api/employees/add` - Add new employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/department-data` - Department info
- `GET /api/dashboard/salary-data` - Salary statistics

### Exports
- `GET /api/export/csv` - Export as CSV
- `GET /api/export/excel` - Export as Excel
- `GET /api/export/pdf` - Export as PDF

---

## 🎯 Quick Tips

1. **First Time Login**: Use `phanendra` / `123456`
2. **Add Employees**: Go to "Employee List" → Click "+ Add Employee"
3. **Search**: Use the search bar to filter employees by name/email/code
4. **View Details**: Click on any employee row to see full details
5. **Export Data**: Click the export button to download employee data

---

## ⚙️ Technical Stack

**Backend:**
- FastAPI (async web framework)
- Motor (async MongoDB driver)
- PyJWT (authentication)
- Uvicorn (ASGI server)

**Frontend:**
- React 18
- React Router 6
- Axios (HTTP client)
- Recharts (data visualization)

**Database:**
- MongoDB 5.0+

---

## 📞 Support

If you encounter issues:
1. Check the error messages in the command windows
2. Verify all services are running (netstat)
3. Check browser console (F12) for client-side errors
4. Ensure MongoDB is running
5. Try clearing browser cache and restarting

---

## ✅ System is Ready!

Everything is configured and ready to use. Just run `run.bat` and start managing employees!

**Happy coding! 🎉**
