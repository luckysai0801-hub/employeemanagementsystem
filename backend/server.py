from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import shutil
from io import BytesIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import xlsxwriter

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging early so middleware and startup can use `logger`
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create uploads directory
UPLOADS_DIR = ROOT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# MongoDB connection (use defaults when env vars are missing)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'ems')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI()

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code} for {request.method} {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        raise

# Root health check endpoint
@app.get("/health")
async def root_health():
    """Simple health check for the root endpoint"""
    return {"status": "ok", "message": "Employee Management System Backend is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Employee Management System Backend API", "version": "1.0"}

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint (no authentication required)
@api_router.get("/health")
async def health_check():
    """Health check endpoint to verify backend is running"""
    return {
        "status": "ok",
        "message": "Backend server is running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    role: str  # Admin, HR, Manager
    last_login: Optional[datetime] = None
    status: str = "active"  # active, locked
    failed_attempts: int = 0

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: User

class Employee(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emp_code: str
    name: str
    email: EmailStr
    department: str
    role: str
    salary: float
    join_date: str
    phone: str
    address: str
    photo: Optional[str] = None
    status: str = "active"  # active, inactive
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    department: str
    role: str
    salary: float
    join_date: str
    phone: str
    address: str
    photo: Optional[str] = None

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    role: Optional[str] = None
    salary: Optional[float] = None
    join_date: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    photo: Optional[str] = None
    status: Optional[str] = None

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    user: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DashboardStats(BaseModel):
    total_employees: int
    active_employees: int
    department_count: int
    average_salary: float

class DepartmentData(BaseModel):
    department: str
    count: int

class SalaryData(BaseModel):
    department: str
    average_salary: float

class GrowthData(BaseModel):
    month: str
    count: int

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, username: str, role: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def generate_emp_code() -> str:
    # Get the count of employees and generate code
    count = await db.employees.count_documents({})
    return f"EMP{str(count + 1).zfill(5)}"

async def create_audit_log(action: str, user: str, employee_id: Optional[str] = None, employee_name: Optional[str] = None):
    log = AuditLog(
        action=action,
        employee_id=employee_id,
        employee_name=employee_name,
        user=user
    )
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    await db.audit_logs.insert_one(doc)

# Auth Routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        role=user_data.role
    )
    doc = user.model_dump()
    doc['password'] = hash_password(user_data.password)
    doc['last_login'] = None
    
    await db.users.insert_one(doc)
    return user

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    try:
        logger.info(f"Login attempt for username: {login_data.username}")
        
        # Find user
        user_doc = await db.users.find_one({"username": login_data.username})
        if not user_doc:
            logger.warning(f"Login failed: User '{login_data.username}' not found")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if account is locked
        if user_doc.get('status') == 'locked':
            logger.warning(f"Login failed: Account '{login_data.username}' is locked")
            raise HTTPException(status_code=403, detail="Account locked due to too many failed attempts")
        
        # Verify password
        if not verify_password(login_data.password, user_doc['password']):
            # Increment failed attempts
            failed_attempts = user_doc.get('failed_attempts', 0) + 1
            update_data = {"failed_attempts": failed_attempts}
            
            if failed_attempts >= 5:
                update_data['status'] = 'locked'
            
            await db.users.update_one(
                {"username": login_data.username},
                {"$set": update_data}
            )
            
            logger.warning(f"Login failed: Invalid password for '{login_data.username}' (attempt {failed_attempts})")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Reset failed attempts and update last login
        await db.users.update_one(
            {"username": login_data.username},
            {"$set": {
                "failed_attempts": 0,
                "last_login": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        logger.info(f"Login successful for user: {login_data.username}")
        
        # Create token
        token = create_token(user_doc['id'], user_doc['username'], user_doc['role'])
        
        user = User(**{k: v for k, v in user_doc.items() if k != 'password'})
        
        return LoginResponse(token=token, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: dict = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0, "password": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_doc)

@api_router.post("/auth/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logged out successfully"}

# Employee Routes
@api_router.post("/employees/add", response_model=Employee)
async def add_employee(employee_data: EmployeeCreate, current_user: dict = Depends(get_current_user)):
    # Check if email exists
    existing = await db.employees.find_one({"email": employee_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Generate employee code
    emp_code = await generate_emp_code()
    
    # Create employee
    employee = Employee(
        emp_code=emp_code,
        **employee_data.model_dump()
    )
    
    doc = employee.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.employees.insert_one(doc)
    
    # Create audit log
    await create_audit_log(
        action="Added new employee",
        user=current_user['username'],
        employee_id=employee.id,
        employee_name=employee.name
    )
    
    # Mock email notification
    logging.info(f"[MOCK EMAIL] New employee added: {employee.name} ({employee.email})")
    
    return employee

@api_router.get("/employees/list", response_model=List[Employee])
async def list_employees(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    current_user: dict = Depends(get_current_user)
):
    # Build query
    query = {}
    
    if search:
        query['$or'] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"emp_code": {"$regex": search, "$options": "i"}}
        ]
    
    if department:
        query['department'] = department
    
    if status:
        query['status'] = status
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Sort direction
    sort_dir = 1 if sort_order == "asc" else -1
    
    # Fetch employees
    employees = await db.employees.find(query, {"_id": 0}).sort(sort_by, sort_dir).skip(skip).limit(limit).to_list(limit)
    
    # Convert datetime strings
    for emp in employees:
        if isinstance(emp.get('created_at'), str):
            emp['created_at'] = datetime.fromisoformat(emp['created_at'])
        if isinstance(emp.get('updated_at'), str):
            emp['updated_at'] = datetime.fromisoformat(emp['updated_at'])
    
    return employees

@api_router.get("/employees/count")
async def count_employees(
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    
    if search:
        query['$or'] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"emp_code": {"$regex": search, "$options": "i"}}
        ]
    
    if department:
        query['department'] = department
    
    if status:
        query['status'] = status
    
    count = await db.employees.count_documents(query)
    return {"count": count}

@api_router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if isinstance(employee.get('created_at'), str):
        employee['created_at'] = datetime.fromisoformat(employee['created_at'])
    if isinstance(employee.get('updated_at'), str):
        employee['updated_at'] = datetime.fromisoformat(employee['updated_at'])
    
    return Employee(**employee)

@api_router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    current_user: dict = Depends(get_current_user)
):
    # Check if employee exists
    existing = await db.employees.find_one({"id": employee_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Update data
    update_data = {k: v for k, v in employee_data.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.employees.update_one(
        {"id": employee_id},
        {"$set": update_data}
    )
    
    # Create audit log
    await create_audit_log(
        action="Updated employee details",
        user=current_user['username'],
        employee_id=employee_id,
        employee_name=existing['name']
    )
    
    # Mock email notification
    logging.info(f"[MOCK EMAIL] Employee updated: {existing['name']} ({existing['email']})")
    
    # Fetch updated employee
    updated_employee = await db.employees.find_one({"id": employee_id}, {"_id": 0})
    
    if isinstance(updated_employee.get('created_at'), str):
        updated_employee['created_at'] = datetime.fromisoformat(updated_employee['created_at'])
    if isinstance(updated_employee.get('updated_at'), str):
        updated_employee['updated_at'] = datetime.fromisoformat(updated_employee['updated_at'])
    
    return Employee(**updated_employee)

@api_router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    # Soft delete
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await db.employees.update_one(
        {"id": employee_id},
        {"$set": {"status": "inactive", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create audit log
    await create_audit_log(
        action="Deleted employee",
        user=current_user['username'],
        employee_id=employee_id,
        employee_name=employee['name']
    )
    
    return {"message": "Employee deleted successfully"}

@api_router.post("/employees/{employee_id}/restore")
async def restore_employee(employee_id: str, current_user: dict = Depends(get_current_user)):
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    await db.employees.update_one(
        {"id": employee_id},
        {"$set": {"status": "active", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create audit log
    await create_audit_log(
        action="Restored employee",
        user=current_user['username'],
        employee_id=employee_id,
        employee_name=employee['name']
    )
    
    return {"message": "Employee restored successfully"}

# Upload Route
@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOADS_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": filename, "url": f"/api/uploads/{filename}"}

# Dashboard Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    total = await db.employees.count_documents({})
    active = await db.employees.count_documents({"status": "active"})
    
    # Get unique departments
    departments = await db.employees.distinct("department")
    dept_count = len(departments)
    
    # Calculate average salary
    pipeline = [
        {"$group": {"_id": None, "avg_salary": {"$avg": "$salary"}}}
    ]
    result = await db.employees.aggregate(pipeline).to_list(1)
    avg_salary = result[0]['avg_salary'] if result else 0
    
    return DashboardStats(
        total_employees=total,
        active_employees=active,
        department_count=dept_count,
        average_salary=round(avg_salary, 2)
    )

@api_router.get("/dashboard/department-data", response_model=List[DepartmentData])
async def get_department_data(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$group": {"_id": "$department", "count": {"$sum": 1}}},
        {"$project": {"department": "$_id", "count": 1, "_id": 0}}
    ]
    result = await db.employees.aggregate(pipeline).to_list(100)
    return result

@api_router.get("/dashboard/salary-data", response_model=List[SalaryData])
async def get_salary_data(current_user: dict = Depends(get_current_user)):
    pipeline = [
        {"$group": {"_id": "$department", "average_salary": {"$avg": "$salary"}}},
        {"$project": {"department": "$_id", "average_salary": 1, "_id": 0}}
    ]
    result = await db.employees.aggregate(pipeline).to_list(100)
    
    # Round salaries
    for item in result:
        item['average_salary'] = round(item['average_salary'], 2)
    
    return result

@api_router.get("/dashboard/recent-activities")
async def get_recent_activities(current_user: dict = Depends(get_current_user)):
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(5).to_list(5)
    
    for log in logs:
        if isinstance(log.get('timestamp'), str):
            log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    
    return logs

# Export Routes
@api_router.get("/export/csv")
async def export_csv(current_user: dict = Depends(get_current_user)):
    employees = await db.employees.find({"status": "active"}, {"_id": 0}).to_list(10000)
    
    # Create CSV using StringIO for text handling
    from io import StringIO
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Emp Code', 'Name', 'Email', 'Department', 'Role', 'Salary', 'Join Date', 'Phone', 'Status'])
    
    # Data
    for emp in employees:
        writer.writerow([
            emp.get('emp_code', ''),
            emp.get('name', ''),
            emp.get('email', ''),
            emp.get('department', ''),
            emp.get('role', ''),
            emp.get('salary', ''),
            emp.get('join_date', ''),
            emp.get('phone', ''),
            emp.get('status', '')
        ])
    
    # Convert to bytes with UTF-8 BOM
    csv_content = '\ufeff' + output.getvalue()  # Add BOM
    csv_bytes = BytesIO(csv_content.encode('utf-8'))
    csv_bytes.seek(0)
    
    return StreamingResponse(
        csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )

@api_router.get("/export/excel")
async def export_excel(current_user: dict = Depends(get_current_user)):
    employees = await db.employees.find({"status": "active"}, {"_id": 0}).to_list(10000)
    
    # Create Excel
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Employees')
    
    # Header format
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'border': 1
    })
    
    # Headers
    headers = ['Emp Code', 'Name', 'Email', 'Department', 'Role', 'Salary', 'Join Date', 'Phone', 'Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Data
    for row, emp in enumerate(employees, start=1):
        worksheet.write(row, 0, emp.get('emp_code', ''))
        worksheet.write(row, 1, emp.get('name', ''))
        worksheet.write(row, 2, emp.get('email', ''))
        worksheet.write(row, 3, emp.get('department', ''))
        worksheet.write(row, 4, emp.get('role', ''))
        worksheet.write(row, 5, emp.get('salary', ''))
        worksheet.write(row, 6, emp.get('join_date', ''))
        worksheet.write(row, 7, emp.get('phone', ''))
        worksheet.write(row, 8, emp.get('status', ''))
    
    workbook.close()
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=employees.xlsx"}
    )

@api_router.get("/export/pdf")
async def export_pdf(current_user: dict = Depends(get_current_user)):
    employees = await db.employees.find({"status": "active"}, {"_id": 0}).to_list(10000)
    
    # Create PDF
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph("Employee Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
    elements.append(Paragraph(f"Generated by: {current_user['username']}", styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))
    
    # Table data
    data = [['Code', 'Name', 'Email', 'Dept', 'Role', 'Salary']]
    
    for emp in employees:
        data.append([
            emp.get('emp_code', ''),
            emp.get('name', ''),
            emp.get('email', ''),
            emp.get('department', ''),
            emp.get('role', ''),
            f"${emp.get('salary', 0):,.2f}"
        ])
    
    # Create table
    table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=employees.pdf"}
    )

# Get departments list
@api_router.get("/departments")
async def get_departments(current_user: dict = Depends(get_current_user)):
    departments = await db.employees.distinct("department")
    return {"departments": departments}

# Include the router in the main app
app.include_router(api_router)

# Serve uploaded files
app.mount("/api/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# (logger already configured above)

@app.on_event("startup")
async def startup_event():
    try:
        # Create default admin user
        existing_admin = await db.users.find_one({"username": "phanendra"})
        if not existing_admin:
            admin = User(
                username="phanendra",
                role="Admin"
            )
            doc = admin.model_dump()
            doc['password'] = hash_password("123456")
            doc['last_login'] = None
            await db.users.insert_one(doc)
            logger.info("Default admin user created: phanendra / 123456")
        else:
            logger.info("Admin user 'phanendra' already exists")
        logger.info("Startup event completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()