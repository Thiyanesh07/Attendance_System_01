import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { studentsAPI, attendanceAPI } from '../services/api'
import { format } from 'date-fns'
import './StudentDashboard.css'

function StudentDashboard() {
  const { rollNumber } = useParams()
  const navigate = useNavigate()
  const [student, setStudent] = useState(null)
  const [attendance, setAttendance] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [todayStatus, setTodayStatus] = useState(null)

  useEffect(() => {
    fetchStudentData()
  }, [rollNumber])

  const fetchStudentData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch student details with attendance stats
      const response = await studentsAPI.getByRoll(rollNumber)
      setStudent(response.data)

      // Fetch attendance records
      const attendanceResponse = await studentsAPI.getAttendance(response.data.id)
      setAttendance(attendanceResponse.data)

      // Check today's status
      const today = format(new Date(), 'yyyy-MM-dd')
      const todayRecord = attendanceResponse.data.find(
        (record) => format(new Date(record.date), 'yyyy-MM-dd') === today
      )
      setTodayStatus(todayRecord)

      setLoading(false)
    } catch (err) {
      console.error('Error fetching student data:', err)
      setError('Student not found or unable to fetch data')
      setLoading(false)
    }
  }

  const handleLogout = () => {
    navigate('/')
  }

  if (loading) {
    return <div className="loading">Loading student data...</div>
  }

  if (error) {
    return (
      <div className="container">
        <div className="alert alert-error">{error}</div>
        <button onClick={handleLogout} className="btn btn-secondary">
          Back to Home
        </button>
      </div>
    )
  }

  return (
    <div className="student-dashboard">
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand">Student Portal</div>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </nav>

      <div className="container">
        {/* Student Info Card */}
        <div className="card student-info-card">
          <div className="student-header">
            <div className="student-avatar">
              {student.photo_path ? (
                <img src={student.photo_path} alt={student.name} />
              ) : (
                <div className="avatar-placeholder">
                  {student.name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className="student-details">
              <h1>{student.name}</h1>
              <p>Roll Number: <strong>{student.roll_number}</strong></p>
              <p>Department: {student.department} | Year: {student.year} | Section: {student.section}</p>
              <p>Email: {student.email}</p>
            </div>
          </div>
        </div>

        {/* Today's Status */}
        <div className="card">
          <h2>Today's Status</h2>
          <div className="today-status">
            {todayStatus ? (
              <div className="status-present-container">
                <div className="status-icon">✓</div>
                <div>
                  <h3>Present</h3>
                  <p>Marked at: {format(new Date(todayStatus.time), 'hh:mm a')}</p>
                  {todayStatus.camera_name && <p>Camera: {todayStatus.camera_name}</p>}
                  <p>Confidence: {(todayStatus.confidence * 100).toFixed(1)}%</p>
                </div>
              </div>
            ) : (
              <div className="status-absent-container">
                <div className="status-icon">✗</div>
                <div>
                  <h3>Not Marked</h3>
                  <p>Attendance not recorded yet for today</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Attendance Statistics */}
        <div className="grid grid-3">
          <div className="stat-card">
            <div className="stat-value">{student.attendance_percentage.toFixed(1)}%</div>
            <div className="stat-label">Attendance Percentage</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{student.present_days}</div>
            <div className="stat-label">Days Present</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{student.total_days}</div>
            <div className="stat-label">Total Days</div>
          </div>
        </div>

        {/* Attendance History */}
        <div className="card">
          <h2>Attendance History</h2>
          {attendance.length > 0 ? (
            <div className="attendance-table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Camera</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {attendance.map((record) => (
                    <tr key={record.id}>
                      <td>{format(new Date(record.date), 'MMM dd, yyyy')}</td>
                      <td>{format(new Date(record.time), 'hh:mm a')}</td>
                      <td>
                        <span className={`status-badge status-${record.status}`}>
                          {record.status}
                        </span>
                      </td>
                      <td>{record.camera_name || 'N/A'}</td>
                      <td>{(record.confidence * 100).toFixed(1)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No attendance records found.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default StudentDashboard
