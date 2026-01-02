# 🚀 EMPLOYEE MANAGEMENT SYSTEM - COMPLETE STARTUP GUIDE

## ⚡ QUICKEST WAY - Just One Click!

### **Step 1: Double-Click to Start Everything**
1. Open File Explorer
2. Navigate to: **`e:\Employee management system`**
3. **Double-click** the file: **`run.bat`**
4. Two command windows will automatically open (Backend & Frontend)
5. Wait **10-15 seconds** for everything to load
6. **Open your browser** and go to: **http://localhost:3000**

---

## 📋 WHAT HAPPENS WHEN YOU RUN `run.bat`

When you double-click `run.bat`, it automatically:
- ✅ Checks if MongoDB is running
- ✅ Cleans up any old processes on ports 8000 and 3000
- ✅ Starts Backend Server (port 8000)
- ✅ Starts Frontend Server (port 3000)
- ✅ Shows you the URLs to access

---

## 🔐 LOGIN DETAILS

Once the app loads, you'll see a login page. Use these credentials:

```
Username: phanendra
Password: 123456
```

---

## 🌐 IMPORTANT URLS

| What | URL | Purpose |
|------|-----|---------|
| **Main App** | http://localhost:3000 | Use this to manage employees |
| **API Backend** | http://localhost:8000 | Backend server |
| **API Documentation** | http://localhost:8000/docs | See all API endpoints |
| **Health Check** | http://localhost:8000/health | Check if backend is running |

---

## ⚙️ ALTERNATIVE WAYS TO RUN

### **Option 2: Using Command Prompt**
1. Press **`Win + R`**
2. Type: **`cmd`** and press Enter
3. Copy and paste this:
```cmd
cd /d e:\Employee management system && run.bat
```
4. Press Enter

### **Option 3: From VS Code Terminal**
1. Open VS Code
2. Press **`Ctrl + J`** to open terminal
3. Type:
```cmd
cd "e:\Employee management system" && run.bat
```
4. Press Enter

---

## 🎯 EXPECTED FLOW

### **When you run `run.bat`:**
```
=====================================
Employee Management System
=====================================

Checking MongoDB connection...
✓ MongoDB is running

Cleaning up ports 8000 and 3000...

Starting Backend Server (port 8000)...
[Window 1 opens with backend running]

Starting Frontend Server (port 3000)...
[Window 2 opens with frontend running]

=====================================
Startup Complete!
=====================================

Backend:  http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs

Username: phanendra
Password: 123456
```

---

## ✅ VERIFICATION CHECKLIST

After running the app, verify:

- [ ] Backend window is open and shows no errors
- [ ] Frontend window is open and shows "Compiled with warnings"
- [ ] Browser opens to http://localhost:3000
- [ ] Login page shows with username/password fields
- [ ] Demo credentials are visible (phanendra / 123456)

---

## 🛑 HOW TO STOP THE APP

### **Method 1: Close the Windows**
Simply close both command windows:
- Close the "Backend Server" window
- Close the "Frontend Server" window

### **Method 2: Task Manager**
1. Press **`Ctrl + Shift + Esc`**
2. Find and close:
   - `python.exe` (backend)
   - `node.exe` (frontend)

### **Method 3: Command Prompt**
Open a new command prompt and run:
```cmd
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

---

## 📂 PROJECT FILE STRUCTURE

```
e:\Employee management system/
│
├── 📄 run.bat                          ⭐ MAIN FILE - Double-click this!
├── start.bat                           (Alternative startup)
├── STARTUP_GUIDE.md                    (Detailed guide)
├── README.md                           (Full documentation)
│
├── backend/                            (FastAPI Server - Port 8000)
│   ├── server.py                       Main backend app
│   ├── requirements.txt                Python dependencies
│   ├── .env                            Configuration file
│   └── uploads/                        File storage folder
│
└── frontend/                           (React App - Port 3000)
    ├── .env                            Frontend configuration
    ├── package.json                    Node dependencies
    ├── public/                         Static files
    └── src/
        ├── App.js                      Main app component
        ├── pages/                      Login, Dashboard, Employee List
        ├── components/                 Reusable components
        └── styles/                     CSS styling
```

---

## 🔧 TROUBLESHOOTING

### **Problem: Port 8000 already in use**
```cmd
netstat -ano | find ":8000"
taskkill /F /PID <pid_number>
```

### **Problem: Port 3000 already in use**
```cmd
netstat -ano | find ":3000"
taskkill /F /PID <pid_number>
```

### **Problem: MongoDB not running**
1. Press **`Win + R`**
2. Type: **`services.msc`**
3. Find "MongoDB Server"
4. Right-click → **Start**

### **Problem: Login still fails**
- Clear browser cache: **`Ctrl + Shift + Delete`**
- Close and reopen browser
- Try again at http://localhost:3000

### **Problem: See errors in backend window**
Read the error message in the command window and:
- Check MongoDB is running
- Verify ports are not in use
- Try restarting everything with `run.bat`

---

## 💡 TIPS & TRICKS

1. **Don't close the command windows!** They must stay open for the app to work
2. **First login might take a few seconds** - Just wait
3. **Refresh the page** if something looks wrong
4. **Check browser console** (F12) for any client-side errors
5. **Both windows need to be running** - If one closes, restart everything

---

## 📊 WHAT YOU CAN DO IN THE APP

After logging in, you can:

✅ **View Dashboard**
- See total employees
- See active employees
- View department statistics
- Check average salary

✅ **Manage Employees**
- Add new employees
- View employee list
- Search and filter employees
- Update employee information
- Delete employees (soft delete)

✅ **Export Data**
- Download as CSV
- Download as Excel
- Download as PDF

✅ **Security Features**
- Secure JWT authentication
- Password protected access
- Account lockout after 5 failed attempts
- Audit logging of all actions

---

## 🎓 SUMMARY - THREE SIMPLE STEPS

```
Step 1: Open e:\Employee management system
         ↓
Step 2: Double-click run.bat
         ↓
Step 3: Wait 10-15 seconds and open http://localhost:3000
         ↓
Step 4: Login with phanendra / 123456
         ↓
        🎉 Done! Start managing employees!
```

---

## ✨ THAT'S IT!

The whole system is now ready to use. Just run `run.bat` and enjoy! 🚀

**Questions?** Check the error messages in the command windows or the troubleshooting section above.

**Happy managing employees!** 😊
