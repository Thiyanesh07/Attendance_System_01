import React, { useState, useEffect, useRef } from 'react'
import { camerasAPI, recognitionAPI } from '../services/api'
import './Components.css'

function LiveMonitoring() {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'single'
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [cameraStreams, setCameraStreams] = useState({}) // Store canvas refs and data per camera
  const [recognitionData, setRecognitionData] = useState({}) // Store recognition results per camera
  
  const canvasRefs = useRef({})
  const intervalRefs = useRef({})
  const processingRef = useRef({}) // Track if a camera is currently processing a frame
  const imageCache = useRef({}) // Cache images to prevent memory leaks

  useEffect(() => {
    fetchCameras()
    return () => {
      // Cleanup all intervals
      Object.values(intervalRefs.current).forEach(clearInterval)
      intervalRefs.current = {}
      processingRef.current = {}
      // Clear image cache
      imageCache.current = {}
    }
  }, [])

  useEffect(() => {
    // Start/stop polling based on active cameras and view mode
    if (cameras.length > 0) {
      // Clear all existing intervals first
      Object.values(intervalRefs.current).forEach(clearInterval)
      intervalRefs.current = {}
      
      cameras.forEach(camera => {
        if (camera.is_active) {
          // In single view, only poll the selected camera at high quality
          if (viewMode === 'single' && selectedCamera?.id !== camera.id) {
            return // Skip non-selected cameras in single view
          }
          startCameraPolling(camera)
        }
      })
    }
    
    return () => {
      Object.values(intervalRefs.current).forEach(clearInterval)
    }
  }, [cameras, viewMode, selectedCamera])

  const fetchCameras = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('[LiveMonitoring] Fetching cameras...')
      const response = await camerasAPI.getAll({ is_active: true })
      console.log('[LiveMonitoring] Cameras fetched:', response.data)
      setCameras(response.data)
      setLoading(false)
    } catch (err) {
      console.error('[LiveMonitoring] Error fetching cameras:', err)
      setError('Failed to load cameras. Please check if the backend server is running.')
      setLoading(false)
    }
  }

  const startCameraPolling = (camera) => {
    // Different polling rates based on view mode
    // Grid view: slower refresh (2 seconds) to reduce load
    // Single view: faster refresh (1 second) for better quality
    const pollInterval = viewMode === 'grid' ? 2000 : 1000
    
    // Clear existing interval if any
    if (intervalRefs.current[camera.id]) {
      clearInterval(intervalRefs.current[camera.id])
    }
    
    const interval = setInterval(() => {
      fetchAndRenderFrame(camera)
    }, pollInterval)
    
    intervalRefs.current[camera.id] = interval
    // Immediate first fetch
    fetchAndRenderFrame(camera)
  }

  const fetchAndRenderFrame = async (camera) => {
    // Skip if already processing this camera
    if (processingRef.current[camera.id]) {
      console.log(`[LiveMonitoring] Skipping camera ${camera.id} - already processing`)
      return
    }
    
    processingRef.current[camera.id] = true
    
    try {
      console.log(`[LiveMonitoring] Fetching frame for camera ${camera.id} (${camera.name})`)
      
      // Get snapshot with reduced resolution for grid view
      const isGridView = viewMode === 'grid' || selectedCamera?.id !== camera.id
      const snapRes = await camerasAPI.snapshot(camera.id, { 
        width: isGridView ? 480 : 960,  // Reduced from 640/1280
        height: isGridView ? 360 : 540  // Reduced from 480/720
      })
      const blob = snapRes.data
      
      console.log(`[LiveMonitoring] Snapshot received, size: ${blob.size} bytes`)

      // Convert to base64 for recognition
      const base64 = await blobToBase64(blob)
      const formData = new FormData()
      formData.append('frame_base64', base64.split(',')[1])
      formData.append('camera_id', String(camera.id))
      formData.append('mark_attendance', 'true')

      // Get recognition results
      const recRes = await recognitionAPI.recognizeFrame(formData)
      const faces = recRes.data.all_faces || []
      const students = recRes.data.students || []
      
      console.log(`[LiveMonitoring] Recognition complete: ${faces.length} faces, ${students.length} recognized`)

      // Update recognition data
      setRecognitionData(prev => ({
        ...prev,
        [camera.id]: {
          faces,
          students,
          timestamp: Date.now()
        }
      }))

      // Draw on canvas
      await drawFrameAndBoxes(camera.id, blob, faces)
    } catch (err) {
      console.error(`[LiveMonitoring] Error fetching frame for camera ${camera.id}:`, err)
      console.error('[LiveMonitoring] Error details:', err.response?.data || err.message)
    } finally {
      // Always release the processing lock
      processingRef.current[camera.id] = false
    }
  }

  const drawFrameAndBoxes = async (cameraId, blob, faces) => {
    console.log(`[LiveMonitoring] Drawing frame for camera ${cameraId}`)
    
    const canvas = canvasRefs.current[cameraId]
    if (!canvas) {
      console.error(`[LiveMonitoring] Canvas not found for camera ${cameraId}`)
      return
    }

    const ctx = canvas.getContext('2d', { alpha: false }) // Disable alpha for better performance
    
    // Reuse cached image if same blob
    let img
    try {
      img = await blobToImage(blob)
    } catch (err) {
      console.error(`[LiveMonitoring] Error loading image:`, err)
      return
    }
    
    console.log(`[LiveMonitoring] Image loaded: ${img.width}x${img.height}`)

    // Only resize canvas if dimensions changed
    if (canvas.width !== img.width || canvas.height !== img.height) {
      canvas.width = img.width
      canvas.height = img.height
    }

    // Clear and draw image
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, img.width, img.height)
    console.log(`[LiveMonitoring] Image drawn on canvas`)

    // Draw bounding boxes
    if (Array.isArray(faces) && faces.length > 0) {
      console.log(`[LiveMonitoring] Drawing ${faces.length} bounding boxes`)
      faces.forEach((face) => {
        const [x1, y1, x2, y2] = face.bbox
        const width = x2 - x1
        const height = y2 - y1
        const recognized = !!face.recognized

        // Box styling
        ctx.lineWidth = 2  // Reduced from 3 for better performance
        ctx.strokeStyle = recognized ? '#00ff00' : '#ff9800'
        ctx.fillStyle = recognized ? 'rgba(0,255,0,0.8)' : 'rgba(255,152,0,0.8)'
        
        // Draw rectangle
        ctx.strokeRect(x1, y1, width, height)

        // Prepare label with register number
        let label = 'Unknown'
        if (recognized && face.roll_number) {
          label = `${face.roll_number}`
          if (face.name) {
            label += ` - ${face.name}`
          }
          if (face.confidence) {
            label += ` (${Math.round(face.confidence * 100)}%)`
          }
        } else if (recognized && face.name) {
          label = face.name
          if (face.confidence) {
            label += ` (${Math.round(face.confidence * 100)}%)`
          }
        }

        // Draw label background and text
        ctx.font = 'bold 14px Arial'  // Reduced from 16px
        const textMetrics = ctx.measureText(label)
        const textWidth = textMetrics.width
        const textHeight = 18  // Reduced from 20

        // Background
        ctx.fillRect(x1, y1 - textHeight - 4, textWidth + 12, textHeight + 4)
        
        // Text
        ctx.fillStyle = '#ffffff'
        ctx.fillText(label, x1 + 6, y1 - 8)

        // Draw confidence bar if recognized
        if (recognized && face.confidence) {
          const barWidth = width
          const barHeight = 5  // Reduced from 6
          const confidenceWidth = barWidth * face.confidence

          // Bar background
          ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
          ctx.fillRect(x1, y2 - barHeight, barWidth, barHeight)

          // Confidence fill
          ctx.fillStyle = recognized ? '#00ff00' : '#ff9800'
          ctx.fillRect(x1, y2 - barHeight, confidenceWidth, barHeight)
        }
      })
    }
    
    // Clean up image object to prevent memory leaks
    img.src = ''
    img = null
  }

  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }

  const blobToImage = (blob) => {
    return new Promise((resolve, reject) => {
      const url = URL.createObjectURL(blob)
      const img = new Image()
      img.onload = () => {
        URL.revokeObjectURL(url)
        resolve(img)
      }
      img.onerror = reject
      img.src = url
    })
  }

  const handleCameraClick = (camera) => {
    setSelectedCamera(camera)
    setViewMode('single')
    
    // Restart polling with higher quality/faster refresh for single view
    cameras.forEach(cam => {
      if (intervalRefs.current[cam.id]) {
        clearInterval(intervalRefs.current[cam.id])
        delete intervalRefs.current[cam.id]
      }
      if (cam.id === camera.id) {
        // Selected camera: faster refresh
        startCameraPolling(cam)
      } else if (viewMode === 'grid') {
        // Other cameras: slower refresh in grid
        startCameraPolling(cam)
      }
    })
  }

  const handleBackToGrid = () => {
    setViewMode('grid')
    setSelectedCamera(null)
    
    // Restart all cameras with grid view settings
    cameras.forEach(cam => {
      if (intervalRefs.current[cam.id]) {
        clearInterval(intervalRefs.current[cam.id])
        delete intervalRefs.current[cam.id]
      }
      startCameraPolling(cam)
    })
  }

  if (loading) {
    return <div className="loading">Loading cameras...</div>
  }

  if (cameras.length === 0) {
    return (
      <div className="card">
        <div className="alert alert-info">
          No active cameras found. Please activate cameras in Camera Management.
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">
          {viewMode === 'grid' ? 'Live Camera Monitoring' : `Camera: ${selectedCamera?.name}`}
        </h1>
        <p className="page-subtitle">
          {viewMode === 'grid' 
            ? 'Real-time monitoring of all active cameras with face recognition'
            : 'Detailed view with real-time face recognition and attendance marking'
          }
        </p>
      </div>

      {error && (
        <div style={{ 
          padding: '15px', 
          marginBottom: '20px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          border: '1px solid #f5c6cb', 
          borderRadius: '4px' 
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {viewMode === 'single' && (
        <div style={{ marginBottom: 20 }}>
          <button onClick={handleBackToGrid} className="btn btn-secondary">
            ← Back to All Cameras
          </button>
        </div>
      )}

      {viewMode === 'grid' ? (
        <div className="live-monitoring-grid">
          {cameras.map((camera) => (
            <div 
              key={camera.id} 
              className="live-camera-card"
              onClick={() => handleCameraClick(camera)}
            >
              <div className="live-camera-header">
                <h3>{camera.name}</h3>
                <span className="live-badge">● LIVE</span>
              </div>
              <div className="live-camera-canvas-container">
                <canvas
                  ref={el => canvasRefs.current[camera.id] = el}
                  className="live-camera-canvas"
                />
                <div className="live-camera-overlay">
                  <span>Click to view details</span>
                </div>
              </div>
              <div className="live-camera-info">
                <p>📍 {camera.location || 'No location'}</p>
                <p>
                  {recognitionData[camera.id]?.students?.length || 0} student(s) recognized
                </p>
                {recognitionData[camera.id]?.timestamp && (
                  <p className="text-muted">
                    Updated: {new Date(recognitionData[camera.id].timestamp).toLocaleTimeString()}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="live-single-view">
          <div className="live-single-main">
            <div className="live-single-canvas-container">
              <canvas
                ref={el => canvasRefs.current[selectedCamera.id] = el}
                className="live-single-canvas"
              />
              <div className="live-overlay-badge">
                <span className="live-badge-large">● LIVE</span>
              </div>
            </div>
            
            <div className="live-camera-details">
              <h3>Camera Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <strong>Location:</strong> {selectedCamera.location || 'N/A'}
                </div>
                <div className="info-item">
                  <strong>IP Address:</strong> {selectedCamera.ip_address}
                </div>
                <div className="info-item">
                  <strong>Resolution:</strong> {selectedCamera.resolution}
                </div>
                <div className="info-item">
                  <strong>FPS:</strong> {selectedCamera.fps}
                </div>
              </div>
            </div>
          </div>

          <div className="live-single-sidebar">
            <h3>Recognized Students</h3>
            {recognitionData[selectedCamera.id]?.students?.length > 0 ? (
              <div className="recognized-students-list">
                {recognitionData[selectedCamera.id].students.map((student, idx) => (
                  <div key={idx} className="recognized-student-item">
                    <div className="student-avatar-circle">
                      {student.name?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div className="student-details">
                      <h4>{student.name || 'Unknown'}</h4>
                      <p className="roll-number">{student.roll_number}</p>
                      <div className="confidence-display">
                        <span>Confidence: {Math.round((student.confidence || 0) * 100)}%</span>
                        <div className="confidence-bar-small">
                          <div 
                            className="confidence-fill-small"
                            style={{ width: `${(student.confidence || 0) * 100}%` }}
                          />
                        </div>
                      </div>
                      <p className="attendance-status">✓ Attendance Marked</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No students recognized yet</p>
            )}

            <div className="live-stats">
              <h4>Detection Statistics</h4>
              <div className="stat-row">
                <span>Total Faces Detected:</span>
                <strong>{recognitionData[selectedCamera.id]?.faces?.length || 0}</strong>
              </div>
              <div className="stat-row">
                <span>Students Recognized:</span>
                <strong>{recognitionData[selectedCamera.id]?.students?.length || 0}</strong>
              </div>
              <div className="stat-row">
                <span>Unknown Faces:</span>
                <strong>
                  {(recognitionData[selectedCamera.id]?.faces?.length || 0) - 
                   (recognitionData[selectedCamera.id]?.students?.length || 0)}
                </strong>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LiveMonitoring
