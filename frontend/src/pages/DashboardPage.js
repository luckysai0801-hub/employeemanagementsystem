import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/DashboardPage.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function DashboardPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [departmentData, setDepartmentData] = useState([]);
  const [salaryData, setSalaryData] = useState([]);
  const [recentActivities, setRecentActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      const [statsRes, deptRes, salaryRes, activitiesRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/dashboard/stats`, { headers }),
        axios.get(`${BACKEND_URL}/api/dashboard/department-data`, { headers }),
        axios.get(`${BACKEND_URL}/api/dashboard/salary-data`, { headers }),
        axios.get(`${BACKEND_URL}/api/dashboard/recent-activities`, { headers })
      ]);

      setStats(statsRes.data);
      setDepartmentData(deptRes.data);
      setSalaryData(salaryRes.data);
      setRecentActivities(activitiesRes.data);
    } catch (err) {
      // Provide more detailed error information to help debugging
      const responseDetail = err?.response?.data?.detail || err?.response?.data;
      const basicDetail = err?.message;
      const code = err?.code || (err?.name ? err.name : null);
      const url = err?.config?.url || '';

      const detail = responseDetail || basicDetail;

      // If there was no response (network-level error), include code and the request URL
      const info = err && !err.response ? `${detail} (code: ${code || 'N/A'}) while requesting ${url}` : detail;

      setError(`Failed to load dashboard data${info ? `: ${info}` : ''}`);
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="dashboard">
        <nav className="navbar">
          <div className="nav-brand">Employee Management System</div>
          <div className="nav-right">
            <span>{user?.username}</span>
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          </div>
        </nav>
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <nav className="navbar">
        <div className="nav-brand">Employee Management System</div>
        <div className="nav-right">
          <span>{user?.username}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </nav>

      <div className="dashboard-container">
        <div className="dashboard-header">
          <div className="header-left">
            <h1>Dashboard</h1>
            <p>Welcome, {user?.username}</p>
          </div>
          <div className="header-actions" style={{display: 'flex', justifyContent: 'flex-end', alignItems: 'center'}}>
            <button onClick={() => navigate('/employees')} className="btn btn-primary">Manage Employees</button>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="stats-grid">
          {stats && (
            <>
              <div className="stat-card">
                <div className="stat-icon">👥</div>
                <div className="stat-content">
                  <p className="stat-label">Total Employees</p>
                  <p className="stat-value">{stats.total_employees}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">✓</div>
                <div className="stat-content">
                  <p className="stat-label">Active Employees</p>
                  <p className="stat-value">{stats.active_employees}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">🏢</div>
                <div className="stat-content">
                  <p className="stat-label">Departments</p>
                  <p className="stat-value">{stats.department_count}</p>
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-icon">💰</div>
                <div className="stat-content">
                  <p className="stat-label">Average Salary</p>
                  <p className="stat-value">₹{stats.average_salary?.toLocaleString() || '0'}</p>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="dashboard-grid">
          <div className="card">
            <h2>Department Distribution</h2>
            <div className="department-list">
              {departmentData.length > 0 ? (
                departmentData.map((dept) => (
                  <div key={dept.department} className="department-item">
                    <span>{dept.department}</span>
                    <span className="badge">{dept.count}</span>
                  </div>
                ))
              ) : (
                <p className="empty-state">No department data available</p>
              )}
            </div>
          </div>

          <div className="card">
            <h2>Average Salary by Department</h2>
            <div className="salary-list">
              {salaryData.length > 0 ? (
                salaryData.map((dept) => (
                  <div key={dept.department} className="salary-item">
                    <span>{dept.department}</span>
                    <span className="salary-value">₹{dept.average_salary?.toLocaleString() || '0'}</span>
                  </div>
                ))
              ) : (
                <p className="empty-state">No salary data available</p>
              )}
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Recent Activities</h2>
          <div className="activities-list">
            {recentActivities.length > 0 ? (
              recentActivities.map((activity, idx) => (
                <div key={idx} className="activity-item">
                  <div className="activity-content">
                    <p className="activity-action">{activity.action}</p>
                    <p className="activity-user">By: {activity.user}</p>
                  </div>
                  <span className="activity-time">
                    {new Date(activity.timestamp).toLocaleString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="empty-state">No activities yet</p>
            )}
          </div>
        </div>

        <div className="action-buttons">
          <button onClick={() => navigate('/employees')} className="btn btn-primary">
            Manage Employees
          </button>
          <button onClick={fetchDashboardData} className="btn btn-secondary">
            Refresh Data
          </button>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
