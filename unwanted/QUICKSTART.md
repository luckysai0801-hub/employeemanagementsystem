# Employee Management System - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### Step 1: Install MongoDB
1. Download from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the default installation
3. MongoDB will start as a Windows Service automatically

### Step 2: Verify Backend is Ready
The backend is pre-configured and ready to run:
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3: Start Frontend
```bash
cd frontend
npm install  # (if not already done)
npm start
```

### Step 4: Login
Open http://localhost:3000 and login with:
- **Username:** phanendra  
- **Password:** 123456

---

## 📋 What's Included

### Backend Features ✅
- ✅ FastAPI with async support
- ✅ JWT authentication with account lockout
- ✅ MongoDB integration
- ✅ Employee CRUD operations
- ✅ Dashboard statistics
- ✅ CSV, Excel, PDF export
- ✅ Audit logging
- ✅ Search and filtering
- ✅ Pagination

### Frontend Features ✅
- ✅ React 18 with React Router
- ✅ Login page with validation
- ✅ Dashboard with statistics
- ✅ Employee list with CRUD
- ✅ Search and filter
- ✅ Responsive design
- ✅ Local storage for auth

---

## 🔧 Troubleshooting

### "No connection could be made... localhost:27017"
**Solution:** MongoDB is not running
1. Press `Win + R`
2. Type: `services.msc`
3. Find "MongoDB Server"
4. Right-click → Start

### "npm install" is slow
**Solution:** Use `--legacy-peer-deps` flag:
```bash
npm install --legacy-peer-deps
```

### Port 8000 or 3000 already in use
**Kill process:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### CORS errors in browser
- Backend CORS is set to accept all origins
- Ensure backend is running on port 8000

---

## 📊 API Endpoints

### Auth
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register

### Employees  
- `GET /api/employees/list` - Get all employees
- `POST /api/employees/add` - Add employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee

### Dashboard
- `GET /api/dashboard/stats` - Statistics
- `GET /api/dashboard/department-data` - Departments
- `GET /api/dashboard/salary-data` - Salaries
- `GET /api/dashboard/recent-activities` - Activities

### Export
- `GET /api/export/csv` - Export as CSV
- `GET /api/export/excel` - Export as Excel
- `GET /api/export/pdf` - Export as PDF

---

## 🎯 Testing the App

1. **Dashboard Page:** View overall statistics
2. **Add Employee:** Click "+ Add Employee" button
3. **Search:** Use search bar to filter employees
4. **Delete:** Remove employee (soft delete)
5. **Logout:** Click logout button in navbar

---

## 📁 Project Structure

```
Employee management system/
├── backend/
│   ├── server.py (FastAPI app)
│   ├── requirements.txt (Python dependencies)
│   ├── .env (Configuration)
│   └── uploads/ (File storage)
├── frontend/
│   ├── src/
│   │   ├── pages/ (React pages)
│   │   ├── styles/ (CSS files)
│   │   ├── utils/ (Helper functions)
│   │   └── App.js (Main app)
│   ├── public/ (Static files)
│   └── package.json (Node dependencies)
└── README.md (Full documentation)
```

---

## ✨ Key Technologies

**Backend:**
- FastAPI 0.110.1
- Motor 3.3.1 (async MongoDB)
- PyJWT 2.10.1
- Uvicorn 0.25.0
- ReportLab 4.4.4 (PDF)
- XlsxWriter 3.2.9 (Excel)

**Frontend:**
- React 18.2.0
- React Router 6.20.0
- Axios 1.6.0
- Recharts 2.10.0

**Database:**
- MongoDB 5.0+

---

## 🚀 Performance Tips

1. **Use pagination** - Lists are paginated by default
2. **Clear browser cache** - For frontend updates
3. **Check network** - Use browser dev tools
4. **Monitor logs** - Check terminal output for errors

---

## 📞 Support

For issues:
1. Check README.md for detailed documentation
2. Review error messages in terminal
3. Verify all services are running (MongoDB, Backend, Frontend)
4. Check browser console (F12) for client-side errors

---

## 🎉 You're All Set!

Your Employee Management System is ready to go!

Visit: **http://localhost:3000**
