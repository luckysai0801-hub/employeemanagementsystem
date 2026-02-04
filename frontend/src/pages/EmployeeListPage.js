import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/EmployeeListPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function EmployeeListPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [departments, setDepartments] = useState([]);
  const [status, setStatus] = useState('');
  const [sortBy] = useState('name');
  const [sortOrder] = useState('asc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    department: '',
    role: '',
    salary: '',
    join_date: '',
    phone: '',
    address: '',
    photo: ''
  });

  const [uploading, setUploading] = useState(false);

  const fetchDepartments = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${BACKEND_URL}/api/departments`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDepartments(response.data.departments || []);
    } catch (err) {
      console.error('Failed to fetch departments:', err);
    }
  }, []);

  const fetchEmployees = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      
      const countRes = await axios.get(`${BACKEND_URL}/api/employees/count`, {
        params: { search, department, status },
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const listRes = await axios.get(`${BACKEND_URL}/api/employees/list`, {
        params: {
          page,
          limit,
          search,
          department,
          status,
          sort_by: sortBy,
          sort_order: sortOrder
        },
        headers: { Authorization: `Bearer ${token}` }
      });

      setTotalCount(countRes.data.count);
      setEmployees(listRes.data);
    } catch (err) {
      setError('Failed to load employees');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, department, status, sortBy, sortOrder]);

  useEffect(() => {
    fetchDepartments();
    fetchEmployees();
  }, [fetchDepartments, fetchEmployees]);

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${BACKEND_URL}/api/employees/add`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Reset form and refresh list
      setFormData({
        name: '',
        email: '',
        department: '',
        role: '',
        salary: '',
        join_date: '',
        phone: '',
        address: '',
        photo: ''
      });
      setShowAddForm(false);
      setPage(1);
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add employee');
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    // auto-upload when file selected
    await uploadFile(file);
  };

  const uploadFile = async (file) => {
    try {
      setUploading(true);
      const token = localStorage.getItem('token');
      const fd = new FormData();
      fd.append('file', file);

      const res = await axios.post(`${BACKEND_URL}/api/upload`, fd, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      // Backend returns { filename, url }
      const url = res.data.url || res.data.filename || '';
      // Store absolute URL so frontend can display it
      const absolute = url.startsWith('http') ? url : `${BACKEND_URL}${url}`;
      setFormData((prev) => ({ ...prev, photo: absolute }));
    } catch (err) {
      setError('Failed to upload image');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${BACKEND_URL}/api/employees/${employeeId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchEmployees();
      } catch (err) {
        setError('Failed to delete employee');
      }
    }
  };

  const handleEditEmployee = (employee) => {
    setEditingEmployee(employee);
    setFormData({
      name: employee.name,
      email: employee.email,
      department: employee.department,
      role: employee.role,
      salary: employee.salary,
      join_date: employee.join_date,
      phone: employee.phone,
      address: employee.address,
      photo: employee.photo || ''
    });
    setShowEditForm(true);
  };

  const handleUpdateEmployee = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${BACKEND_URL}/api/employees/${editingEmployee.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Reset form and refresh list
      setFormData({
        name: '',
        email: '',
        department: '',
        role: '',
        salary: '',
        join_date: '',
        phone: '',
        address: '',
        photo: ''
      });
      setEditingEmployee(null);
      setShowEditForm(false);
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update employee');
    }
  };

  const handleRestoreEmployee = async (employeeId) => {
    if (!window.confirm('Activate this employee again?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${BACKEND_URL}/api/employees/${employeeId}/restore`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchEmployees();
    } catch (err) {
      console.error(err);
      setError('Failed to activate employee');
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  // Export helpers (CSV / Excel / Print to PDF)
  const buildCsv = (rows) => {
    const headers = [
      'Code','Name','Email','Department','Role','Salary','Status'
    ];
    const lines = [headers.join(',')];
    rows.forEach((r) => {
      const line = [
        `"${r.emp_code ?? ''}"`,
        `"${(r.name ?? '').replace(/"/g, '""')}"`,
        `"${(r.email ?? '').replace(/"/g, '""')}"`,
        `"${(r.department ?? '').replace(/"/g, '""')}"`,
        `"${(r.role ?? '').replace(/"/g, '""')}"`,
        `"${r.salary ?? ''}"`,
        `"${r.status ?? ''}"`
      ];
      lines.push(line.join(','));
    });
    return lines.join('\n');
  };

  const downloadBlob = (content, fileName, mime) => {
    const blob = new Blob([content], { type: mime });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!employees || employees.length === 0) return;
    const csv = buildCsv(employees);
    downloadBlob(csv, `employees_page${page}.csv`, 'text/csv;charset=utf-8;');
  };

  // Excel: emit CSV but use an Excel-friendly mime / extension so users can open in Excel
  const handleExportExcel = () => {
    if (!employees || employees.length === 0) return;
    const csv = buildCsv(employees);
    // Use older Excel MIME to improve compatibility; modern Excel will still open CSV.
    downloadBlob(csv, `employees_page${page}.xls`, 'application/vnd.ms-excel');
  };

  // Simple print approach: open a new window with a printable table and call print()
  const handlePrintPDF = () => {
    if (!employees || employees.length === 0) return;
    const printable = `
      <html>
      <head>
        <title>Employees - Page ${page}</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #ccc; padding: 6px 8px; text-align: left; }
          th { background: #f4f4f4; }
        </style>
      </head>
      <body>
        <h2>Employees (Page ${page})</h2>
        <table>
          <thead>
            <tr>
              <th>Code</th><th>Name</th><th>Email</th><th>Department</th><th>Role</th><th>Salary</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${employees.map(e => `
              <tr>
                <td>${e.emp_code ?? ''}</td>
                <td>${(e.name ?? '').replace(/</g,'&lt;')}</td>
                <td>${(e.email ?? '').replace(/</g,'&lt;')}</td>
                <td>${(e.department ?? '').replace(/</g,'&lt;')}</td>
                <td>${(e.role ?? '').replace(/</g,'&lt;')}</td>
                <td>${e.salary ?? ''}</td>
                <td>${(e.status ?? '').replace(/</g,'&lt;')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </body>
      </html>
    `;

    const w = window.open('', '_blank');
    if (!w) {
      setError('Popup blocked. Please allow popups to print or export to PDF.');
      return;
    }
    w.document.open();
    w.document.write(printable);
    w.document.close();
    // Give the new window a moment to render then call print
    setTimeout(() => {
      w.focus();
      w.print();
    }, 500);
  };

  const totalPages = Math.ceil(totalCount / limit);

  return (
    <div className="employee-list">
      <nav className="navbar">
        <div className="nav-brand">Employee Management System</div>
        <div className="nav-right">
          <button onClick={() => navigate('/dashboard')} className="nav-btn">Dashboard</button>
          <span>{user?.username}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </nav>

      <div className="container">
        <div className="header">
          <h1>Employees</h1>
          <div className="header-actions">
            <div className="export-buttons">
              <button onClick={handleExportCSV} className="btn btn-secondary" disabled={loading || employees.length===0}>
                Export CSV
              </button>
              <button onClick={handleExportExcel} className="btn btn-secondary" disabled={loading || employees.length===0}>
                Export Excel
              </button>
              <button onClick={handlePrintPDF} className="btn btn-secondary" disabled={loading || employees.length===0}>
                Print / PDF
              </button>
            </div>
            <button 
              onClick={() => setShowAddForm(!showAddForm)} 
              className="btn btn-primary"
            >
              {showAddForm ? 'Cancel' : '+ Add Employee'}
            </button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showAddForm && (
          <div className="add-form">
            <h2>Add New Employee</h2>
            <form onSubmit={handleAddEmployee}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Department *</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Role *</label>
                  <input
                    type="text"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Salary *</label>
                  <input
                    type="number"
                    value={formData.salary}
                    onChange={(e) => setFormData({...formData, salary: parseFloat(e.target.value)})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Join Date *</label>
                  <input
                    type="date"
                    value={formData.join_date}
                    onChange={(e) => setFormData({...formData, join_date: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                />
                {uploading && <div style={{marginTop:8}}>Uploading...</div>}
                {formData.photo && (
                  <div style={{marginTop:8}}>
                    <img src={formData.photo} alt="preview" style={{width:80, height:80, objectFit:'cover', borderRadius:6}} />
                  </div>
                )}
              </div>
              <button type="submit" className="btn btn-primary">Save Employee</button>
            </form>
          </div>
        )}

        {showEditForm && editingEmployee && (
          <div className="add-form">
            <h2>Edit Employee: {editingEmployee.name}</h2>
            <form onSubmit={handleUpdateEmployee}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Email *</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Department *</label>
                  <input
                    type="text"
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Role *</label>
                  <input
                    type="text"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Salary *</label>
                  <input
                    type="number"
                    value={formData.salary}
                    onChange={(e) => setFormData({...formData, salary: parseFloat(e.target.value)})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Join Date *</label>
                  <input
                    type="date"
                    value={formData.join_date}
                    onChange={(e) => setFormData({...formData, join_date: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Phone</label>
                  <input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Photo</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                />
                {uploading && <div style={{marginTop:8}}>Uploading...</div>}
                {formData.photo && (
                  <div style={{marginTop:8}}>
                    <img src={formData.photo} alt="preview" style={{width:80, height:80, objectFit:'cover', borderRadius:6}} />
                  </div>
                )}
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">Update Employee</button>
                <button 
                  type="button" 
                  onClick={() => {
                    setShowEditForm(false);
                    setEditingEmployee(null);
                    setFormData({
                      name: '',
                      email: '',
                      department: '',
                      role: '',
                      salary: '',
                      join_date: '',
                      phone: '',
                      address: ''
                    });
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="filters">
          <input
            type="text"
            placeholder="Search by name, email, or code..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="search-input"
          />
          <select 
            value={department} 
            onChange={(e) => {
              setDepartment(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Departments</option>
            {departments.map(dept => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
          <select 
            value={status} 
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select value={limit} onChange={(e) => setLimit(parseInt(e.target.value))}>
            <option value="10">10 per page</option>
            <option value="20">20 per page</option>
            <option value="50">50 per page</option>
          </select>
        </div>

        {loading ? (
          <div className="loading">Loading employees...</div>
        ) : (
          <>
            <div className="employees-table">
              <table>
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Role</th>
                    <th>Salary</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.length > 0 ? (
                    employees.map(emp => (
                      <tr key={emp.id}>
                        <td>{emp.emp_code}</td>
                        <td>{emp.name}</td>
                        <td>{emp.email}</td>
                        <td>{emp.department}</td>
                        <td>{emp.role}</td>
                        <td>₹{emp.salary?.toLocaleString() || '0'}</td>
                        <td>
                          <span className={`status-badge status-${emp.status}`}>
                            {emp.status}
                          </span>
                        </td>
                        <td>
                          {emp.status === 'inactive' ? (
                            <button
                              onClick={() => handleRestoreEmployee(emp.id)}
                              className="btn btn-primary"
                            >
                              Activate
                            </button>
                          ) : (
                            <div className="action-buttons-group">
                              <button 
                                onClick={() => handleEditEmployee(emp)}
                                className="btn btn-secondary"
                              >
                                Edit
                              </button>
                              <button 
                                onClick={() => handleDeleteEmployee(emp.id)}
                                className="btn btn-delete"
                              >
                                Delete
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" className="empty-state">No employees found</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="pagination">
              <span>Page {page} of {totalPages} (Total: {totalCount})</span>
              <div className="pagination-buttons">
                <button 
                  onClick={() => setPage(Math.max(1, page - 1))} 
                  disabled={page === 1}
                  className="btn"
                >
                  ← Previous
                </button>
                <button 
                  onClick={() => setPage(Math.min(totalPages, page + 1))} 
                  disabled={page === totalPages}
                  className="btn"
                >
                  Next →
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default EmployeeListPage;
