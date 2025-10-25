import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { studentsAPI, attendanceAPI, camerasAPI, trainingAPI } from '../services/api'
import StudentsManagement from '../components/StudentsManagement'
import CamerasManagement from '../components/CamerasManagement'
import LiveRecognition from '../components/LiveRecognition'
import AttendanceManagement from '../components/AttendanceManagement'
import './AdminDashboard.css'

function AdminDashboard() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [stats, setStats] = useState({
    total_students: 0,
    present_today: 0,
    absent_today: 0,
    attendance_percentage: 0,
  })
  const [modelStats, setModelStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const [attendanceResponse, modelResponse] = await Promise.all([
        attendanceAPI.getStats(),
        trainingAPI.getModelStats(),
      ])
      setStats(attendanceResponse.data)
      setModelStats(modelResponse.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching stats:', err)
      setLoading(false)
    }
  }

  const handleLogout = () => {
    navigate('/')
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return renderDashboard()
      case 'students':
        return <StudentsManagement />
      case 'cameras':
        return <CamerasManagement />
      case 'recognition':
        return <LiveRecognition />
      case 'attendance':
        return <AttendanceManagement />
      default:
        return renderDashboard()
    }
  }

  const renderDashboard = () => (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard Overview</h1>
        <p className="page-subtitle">Monitor attendance and system statistics</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-4">
        <div className="stat-card">
          <div className="stat-value">{stats.total_students}</div>
          <div className="stat-label">Total Students</div>
        </div>
        <div className="stat-card stat-success">
          <div className="stat-value">{stats.present_today}</div>
          <div className="stat-label">Present Today</div>
        </div>
        <div className="stat-card stat-danger">
          <div className="stat-value">{stats.absent_today}</div>
          <div className="stat-label">Absent Today</div>
        </div>
        <div className="stat-card stat-info">
          <div className="stat-value">{stats.attendance_percentage.toFixed(1)}%</div>
          <div className="stat-label">Attendance Rate</div>
        </div>
      </div>

      {/* Model Stats */}
      {modelStats && (
        <div className="card">
          <h2>Face Recognition Model Statistics</h2>
          <div className="grid grid-3">
            <div className="info-item">
              <div className="info-label">Total Embeddings</div>
              <div className="info-value">{modelStats.total_embeddings}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Registered Students</div>
              <div className="info-value">{modelStats.unique_students}</div>
            </div>
            <div className="info-item">
              <div className="info-label">Model Dimension</div>
              <div className="info-value">{modelStats.dimension}</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <button
            className="btn btn-primary"
            onClick={() => setActiveTab('students')}
          >
            Manage Students
          </button>
          <button
            className="btn btn-success"
            onClick={() => setActiveTab('cameras')}
          >
            Manage Cameras
          </button>
          <button
            className="btn btn-info"
            onClick={() => setActiveTab('recognition')}
          >
            Live Recognition
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => setActiveTab('attendance')}
          >
            View Attendance
          </button>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return <div className="loading">Loading dashboard...</div>
  }

  return (
    <div className="admin-dashboard">
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand">Admin Portal</div>
          <button onClick={handleLogout} className="btn btn-danger">
            Logout
          </button>
        </div>
      </nav>

      <div className="admin-container">
        <div className="sidebar">
          <div className="sidebar-menu">
            <button
              className={`sidebar-item ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`sidebar-item ${activeTab === 'students' ? 'active' : ''}`}
              onClick={() => setActiveTab('students')}
            >
              👥 Students
            </button>
            <button
              className={`sidebar-item ${activeTab === 'cameras' ? 'active' : ''}`}
              onClick={() => setActiveTab('cameras')}
            >
              🎥 Cameras
            </button>
            <button
              className={`sidebar-item ${activeTab === 'recognition' ? 'active' : ''}`}
              onClick={() => setActiveTab('recognition')}
            >
              🤖 Live Recognition
            </button>
            <button
              className={`sidebar-item ${activeTab === 'attendance' ? 'active' : ''}`}
              onClick={() => setActiveTab('attendance')}
            >
              📝 Attendance
            </button>
          </div>
        </div>

        <div className="main-content">
          {renderContent()}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
