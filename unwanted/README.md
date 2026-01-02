# Employee Management System - Setup Instructions

## Prerequisites
This application requires:
1. **MongoDB** - Database server running on `localhost:27017`
2. **Node.js** - v14+ for the React frontend
3. **Python** - v3.8+ with pip for the FastAPI backend

## Backend Setup

### Install MongoDB
**Download MongoDB Community Edition:**
- Visit: https://www.mongodb.com/try/download/community
- Select your OS (Windows)
- Download and install
- MongoDB will run as a Windows Service on `localhost:27017`

**Verify MongoDB is running:**
```bash
mongo --version
# or
mongosh --version
```

### Start Backend Server
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: **http://localhost:8000**

**API Documentation available at:** http://localhost:8000/docs

## Frontend Setup

### Install Dependencies
```bash
cd frontend
npm install
```

### Update Backend URL (if needed)
Edit `frontend/.env`:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Start Frontend Development Server
```bash
npm start
```

The frontend will open at: **http://localhost:3000**

## Default Login Credentials
- **Username:** phanendra
- **Password:** 123456
- **Role:** Admin

## Features

### Dashboard
- View employee statistics
- Department distribution
- Average salary by department
- Recent activities log

### Employee Management
- Add new employees
- View employee list with pagination
- Filter by department, status
- Search by name, email, or code
- Delete employees (soft delete)

### Authentication
- Secure login with JWT tokens
- Account lockout after 5 failed attempts
- Session persistence with local storage

### Reporting
- Export employees to CSV
- Export employees to Excel
- Generate PDF reports
- Audit logs for all actions

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Employees
- `GET /api/employees/list` - List employees (paginated)
- `POST /api/employees/add` - Add new employee
- `GET /api/employees/{id}` - Get employee details
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee
- `POST /api/employees/{id}/restore` - Restore deleted employee

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/department-data` - Get department distribution
- `GET /api/dashboard/salary-data` - Get salary by department
- `GET /api/dashboard/recent-activities` - Get recent activities

### Export
- `GET /api/export/csv` - Export employees as CSV
- `GET /api/export/excel` - Export employees as Excel
- `GET /api/export/pdf` - Export employees as PDF

## Troubleshooting

### Backend won't start
**Error:** "No connection could be made... localhost:27017"
- **Solution:** Install and start MongoDB before running the backend

### Frontend npm install fails
**Error:** "No matching version found"
- **Solution:** Ensure Node.js is installed and npm is updated
  ```bash
  node --version
  npm --version
  npm install -g npm@latest
  ```

### CORS errors in browser
- **Solution:** Backend CORS is configured to accept all origins (`*`)
- Check that backend is running on port 8000

### Port already in use
**Backend (8000):**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Frontend (3000):**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## Architecture

### Frontend (React)
- React 18 with React Router
- Axios for API calls
- CSS for styling
- Responsive design

### Backend (FastAPI)
- FastAPI framework with async support
- Motor for async MongoDB operations
- JWT authentication
- File uploads support
- Multiple export formats (CSV, Excel, PDF)

### Database (MongoDB)
- Collections: users, employees, audit_logs
- Document-based storage
- Automatic indexing

## Development Notes

The application includes:
- ✅ User authentication with JWT
- ✅ Employee CRUD operations
- ✅ Dashboard with statistics
- ✅ Search and filtering
- ✅ Pagination
- ✅ Audit logging
- ✅ Export functionality
- ✅ Responsive UI

## Next Steps

1. Download and install MongoDB
2. Start MongoDB service
3. Run the backend: `uvicorn server:app --reload`
4. Install frontend dependencies: `npm install`
5. Start the frontend: `npm start`
6. Login with phanendra / 123456

Enjoy using the Employee Management System! 🎉
