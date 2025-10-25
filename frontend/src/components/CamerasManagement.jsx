import React, { useState, useEffect } from 'react'
import { camerasAPI } from '../services/api'
import './Components.css'

function CamerasManagement() {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [formData, setFormData] = useState({
    name: '',
    ip_address: '',
    location: '',
    fps: 30,
    resolution: '640x480',
  })

  useEffect(() => {
    fetchCameras()
  }, [])

  const fetchCameras = async () => {
    try {
      setLoading(true)
      const response = await camerasAPI.getAll()
      setCameras(response.data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching cameras:', err)
      setLoading(false)
    }
  }

  const handleAddCamera = () => {
    setSelectedCamera(null)
    setFormData({
      name: '',
      ip_address: '',
      location: '',
      fps: 30,
      resolution: '640x480',
    })
    setShowModal(true)
  }

  const handleEditCamera = (camera) => {
    setSelectedCamera(camera)
    setFormData({
      name: camera.name,
      ip_address: camera.ip_address,
      location: camera.location || '',
      fps: camera.fps,
      resolution: camera.resolution,
    })
    setShowModal(true)
  }

  const handleDeleteCamera = async (cameraId) => {
    if (!window.confirm('Are you sure you want to delete this camera?')) {
      return
    }

    try {
      await camerasAPI.delete(cameraId)
      alert('Camera deleted successfully')
      fetchCameras()
    } catch (err) {
      console.error('Error deleting camera:', err)
      alert('Error deleting camera')
    }
  }

  const handleToggleCamera = async (cameraId) => {
    try {
      await camerasAPI.toggle(cameraId)
      fetchCameras()
    } catch (err) {
      console.error('Error toggling camera:', err)
      alert('Error toggling camera status')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    try {
      if (selectedCamera) {
        await camerasAPI.update(selectedCamera.id, formData)
        alert('Camera updated successfully')
      } else {
        await camerasAPI.create(formData)
        alert('Camera added successfully')
      }
      setShowModal(false)
      fetchCameras()
    } catch (err) {
      console.error('Error saving camera:', err)
      alert('Error saving camera: ' + (err.response?.data?.detail || err.message))
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  if (loading) {
    return <div className="loading">Loading cameras...</div>
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Cameras Management</h1>
        <p className="page-subtitle">Add and manage surveillance cameras</p>
      </div>

      <div className="card">
        <div className="card-actions">
          <button onClick={handleAddCamera} className="btn btn-primary">
            + Add New Camera
          </button>
        </div>

        <div className="cameras-grid">
          {cameras.map((camera) => (
            <div key={camera.id} className="camera-card">
              <div className="camera-header">
                <div className="camera-icon">🎥</div>
                <div className="camera-status">
                  <span className={`status-badge ${camera.is_active ? 'status-present' : 'status-absent'}`}>
                    {camera.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="camera-body">
                <h3>{camera.name}</h3>
                <p><strong>IP Address:</strong> {camera.ip_address}</p>
                <p><strong>Location:</strong> {camera.location || 'N/A'}</p>
                <p><strong>FPS:</strong> {camera.fps}</p>
                <p><strong>Resolution:</strong> {camera.resolution}</p>
              </div>

              <div className="camera-actions">
                <button
                  onClick={() => handleToggleCamera(camera.id)}
                  className={`btn ${camera.is_active ? 'btn-danger' : 'btn-success'} btn-sm`}
                >
                  {camera.is_active ? 'Deactivate' : 'Activate'}
                </button>
                <button
                  onClick={() => handleEditCamera(camera)}
                  className="btn btn-secondary btn-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteCamera(camera.id)}
                  className="btn btn-danger btn-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {cameras.length === 0 && (
          <p className="no-data">No cameras configured.</p>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">
                {selectedCamera ? 'Edit Camera' : 'Add New Camera'}
              </h2>
              <button className="close-btn" onClick={() => setShowModal(false)}>
                ×
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Camera Name *</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., Entrance Camera"
                  />
                </div>

                <div className="form-group">
                  <label>IP Address / RTSP URL *</label>
                  <input
                    type="text"
                    name="ip_address"
                    value={formData.ip_address}
                    onChange={handleInputChange}
                    required
                    placeholder="e.g., rtsp://192.168.1.100:554 or 0 for default camera"
                  />
                </div>

                <div className="form-group">
                  <label>Location</label>
                  <input
                    type="text"
                    name="location"
                    value={formData.location}
                    onChange={handleInputChange}
                    placeholder="e.g., Main Building Entrance"
                  />
                </div>

                <div className="grid grid-2">
                  <div className="form-group">
                    <label>FPS</label>
                    <input
                      type="number"
                      name="fps"
                      value={formData.fps}
                      onChange={handleInputChange}
                      min="1"
                      max="60"
                    />
                  </div>

                  <div className="form-group">
                    <label>Resolution</label>
                    <select
                      name="resolution"
                      value={formData.resolution}
                      onChange={handleInputChange}
                    >
                      <option value="640x480">640x480</option>
                      <option value="1280x720">1280x720</option>
                      <option value="1920x1080">1920x1080</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {selectedCamera ? 'Update' : 'Add'} Camera
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default CamerasManagement
