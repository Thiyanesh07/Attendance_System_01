import React, { useState, useEffect } from 'react'
import { studentsAPI, trainingAPI } from '../services/api'
import AddStudentModal from './AddStudentModal'
import './Components.css'

function StudentsManagement() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedStudent, setSelectedStudent] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchStudents()
  }, [])

  const fetchStudents = async () => {
    try {
      setLoading(true)
      const response = await studentsAPI.getAll()
      setStudents(response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching students:', err)
      setLoading(false)
    }
  }

  const handleAddStudent = () => {
    setSelectedStudent(null)
    setShowModal(true)
  }

  const handleEditStudent = (student) => {
    setSelectedStudent(student)
    setShowModal(true)
  }

  const handleDeleteStudent = async (studentId) => {
    if (!window.confirm('Are you sure you want to delete this student?')) {
      return
    }

    try {
      await studentsAPI.delete(studentId)
      alert('Student deleted successfully')
      fetchStudents()
    } catch (err) {
      console.error('Error deleting student:', err)
      alert('Error deleting student')
    }
  }

  const handleModalClose = (updated) => {
    setShowModal(false)
    setSelectedStudent(null)
    if (updated) {
      fetchStudents()
    }
  }

  const filteredStudents = students.filter((student) =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.roll_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    student.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (loading) {
    return <div className="loading">Loading students...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Students Management</h1>
        <p className="page-subtitle">Add, edit, and manage student records</p>
      </div>

      <div className="card">
        <div className="card-actions">
          <input
            type="text"
            placeholder="Search students..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button onClick={handleAddStudent} className="btn btn-primary">
            + Add New Student
          </button>
        </div>

        <div className="students-grid">
          {filteredStudents.map((student) => (
            <div key={student.id} className="student-card">
              <div className="student-card-header">
                <div className="student-avatar-small">
                  {student.photo_path ? (
                    <img src={student.photo_path} alt={student.name} />
                  ) : (
                    <div className="avatar-placeholder-small">
                      {student.name.charAt(0).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="student-card-info">
                  <h3>{student.name}</h3>
                  <p className="roll-number">{student.roll_number}</p>
                </div>
              </div>

              <div className="student-card-body">
                <p><strong>Email:</strong> {student.email}</p>
                <p><strong>Department:</strong> {student.department}</p>
                <p><strong>Year:</strong> {student.year} | <strong>Section:</strong> {student.section}</p>
                <p><strong>Status:</strong>
                  <span className={`status-badge ${student.is_active ? 'status-present' : 'status-absent'}`}>
                    {student.is_active ? 'Active' : 'Inactive'}
                  </span>
                </p>
                <p><strong>Face Enrolled:</strong>
                  <span className={`status-badge ${student.face_encoding_id ? 'status-present' : 'status-absent'}`}>
                    {student.face_encoding_id ? 'Yes' : 'No'}
                  </span>
                </p>
              </div>

              <div className="student-card-actions">
                <button
                  onClick={() => handleEditStudent(student)}
                  className="btn btn-secondary btn-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteStudent(student.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {filteredStudents.length === 0 && (
          <p className="no-data">No students found.</p>
        )}
      </div>

      {showModal && (
        <AddStudentModal
          student={selectedStudent}
          onClose={handleModalClose}
        />
      )}
    </div>
  )
}

export default StudentsManagement
