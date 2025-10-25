import React, { useState, useEffect } from 'react'
import { attendanceAPI, studentsAPI } from '../services/api'
import { format } from 'date-fns'
import './Components.css'

function AttendanceManagement() {
  const [attendance, setAttendance] = useState([])
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDate, setSelectedDate] = useState(format(new Date(), 'yyyy-MM-dd'))
  const [filterStudent, setFilterStudent] = useState('')

  useEffect(() => {
    fetchData()
  }, [selectedDate])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [attendanceResponse, studentsResponse] = await Promise.all([
        attendanceAPI.getAll({ date_filter: selectedDate }),
        studentsAPI.getAll(),
      ])
      setAttendance(attendanceResponse.data)
      setStudents(studentsResponse.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching data:', err)
      setLoading(false)
    }
  }

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('Are you sure you want to delete this attendance record?')) {
      return
    }

    try {
      await attendanceAPI.delete(recordId)
      alert('Attendance record deleted successfully')
      fetchData()
    } catch (err) {
      console.error('Error deleting record:', err)
      alert('Error deleting attendance record')
    }
  }

  const handleExport = () => {
    // Simple CSV export
    const csvContent = [
      ['Date', 'Time', 'Student Name', 'Roll Number', 'Status', 'Camera', 'Confidence'],
      ...attendance.map((record) => [
        format(new Date(record.date), 'yyyy-MM-dd'),
        format(new Date(record.time), 'HH:mm:ss'),
        record.student_name,
        record.student_roll_number,
        record.status,
        record.camera_name || 'N/A',
        (record.confidence * 100).toFixed(1) + '%',
      ]),
    ]
      .map((row) => row.join(','))
      .join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `attendance_${selectedDate}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const filteredAttendance = attendance.filter((record) =>
    record.student_name.toLowerCase().includes(filterStudent.toLowerCase()) ||
    record.student_roll_number.toLowerCase().includes(filterStudent.toLowerCase())
  )

  if (loading) {
    return <div className="loading">Loading attendance...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Attendance Management</h1>
        <p className="page-subtitle">View and manage attendance records</p>
      </div>

      <div className="card">
        <div className="attendance-filters">
          <div className="form-group">
            <label>Select Date:</label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Search Student:</label>
            <input
              type="text"
              placeholder="Name or Roll Number"
              value={filterStudent}
              onChange={(e) => setFilterStudent(e.target.value)}
            />
          </div>

          <button onClick={handleExport} className="btn btn-success">
            Export CSV
          </button>
        </div>

        <div className="attendance-stats-bar">
          <div className="stat-item">
            <span className="stat-label">Total Records:</span>
            <span className="stat-value">{filteredAttendance.length}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Present:</span>
            <span className="stat-value text-success">
              {filteredAttendance.filter((r) => r.status === 'present').length}
            </span>
          </div>
        </div>

        {filteredAttendance.length > 0 ? (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Student Name</th>
                  <th>Roll Number</th>
                  <th>Status</th>
                  <th>Camera</th>
                  <th>Confidence</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredAttendance.map((record) => (
                  <tr key={record.id}>
                    <td>{format(new Date(record.date), 'MMM dd, yyyy')}</td>
                    <td>{format(new Date(record.time), 'hh:mm a')}</td>
                    <td>{record.student_name}</td>
                    <td>{record.student_roll_number}</td>
                    <td>
                      <span className={`status-badge status-${record.status}`}>
                        {record.status}
                      </span>
                    </td>
                    <td>{record.camera_name || 'N/A'}</td>
                    <td>{(record.confidence * 100).toFixed(1)}%</td>
                    <td>
                      <button
                        onClick={() => handleDeleteRecord(record.id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="no-data">No attendance records found for the selected date.</p>
        )}
      </div>
    </div>
  )
}

export default AttendanceManagement
