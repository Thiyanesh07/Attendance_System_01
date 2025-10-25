import React, { useState, useEffect, useRef } from 'react'
import Webcam from 'react-webcam'
import { camerasAPI, recognitionAPI } from '../services/api'
import './Components.css'

function LiveRecognition() {
  const [cameras, setCameras] = useState([])
  const [selectedCamera, setSelectedCamera] = useState(null)
  const [recognizing, setRecognizing] = useState(false)
  const [recognitionResults, setRecognitionResults] = useState([])
  const [allFaces, setAllFaces] = useState([])  // Store all detected faces for bounding boxes
  const [loading, setLoading] = useState(true)
  const webcamRef = useRef(null)
  const canvasRef = useRef(null)  // Canvas for drawing bounding boxes
  const recognitionIntervalRef = useRef(null)

  useEffect(() => {
    fetchCameras()
    return () => {
      stopRecognition()
    }
  }, [])

  const fetchCameras = async () => {
    try {
      setLoading(true)
      const response = await camerasAPI.getAll({ is_active: true })
      setCameras(response.data)
      if (response.data.length > 0) {
        setSelectedCamera(response.data[0])
      }
      setLoading(false)
    } catch (err) {
      console.error('Error fetching cameras:', err)
      setLoading(false)
    }
  }

  const startRecognition = () => {
    setRecognizing(true)
    setRecognitionResults([])
    setAllFaces([])

    recognitionIntervalRef.current = setInterval(async () => {
      const imageSrc = webcamRef.current?.getScreenshot()
      if (imageSrc) {
        try {
          const formData = new FormData()
          formData.append('frame_base64', imageSrc.split(',')[1])
          formData.append('camera_id', selectedCamera?.id || '')
          formData.append('mark_attendance', 'true')

          const response = await recognitionAPI.recognizeFrame(formData)
          
          console.log('[FRONTEND] Recognition response:', response.data)
          console.log('[FRONTEND] All faces:', response.data.all_faces)
          
          // Update recognized students
          if (response.data.students && response.data.students.length > 0) {
            setRecognitionResults(response.data.students)
            console.log('[FRONTEND] Recognized students:', response.data.students)
          } else {
            setRecognitionResults([])
          }
          
          // Update all detected faces for bounding boxes
          if (response.data.all_faces && response.data.all_faces.length > 0) {
            setAllFaces(response.data.all_faces)
            console.log('[FRONTEND] Drawing bounding boxes for', response.data.all_faces.length, 'faces')
            drawBoundingBoxes(response.data.all_faces)
          } else {
            setAllFaces([])
            clearCanvas()
            console.log('[FRONTEND] No faces detected, clearing canvas')
          }
        } catch (err) {
          console.error('Recognition error:', err)
        }
      }
    }, 2000) // Recognize every 2 seconds
  }

  const drawBoundingBoxes = (faces) => {
    console.log('[FRONTEND] drawBoundingBoxes called with:', faces)
    
    const canvas = canvasRef.current
    const video = webcamRef.current?.video
    
    console.log('[FRONTEND] Canvas element:', canvas)
    console.log('[FRONTEND] Video element:', video)
    
    if (!canvas || !video) {
      console.log('[FRONTEND] Canvas or video not available!')
      return
    }
    
    const ctx = canvas.getContext('2d')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    console.log('[FRONTEND] Canvas dimensions:', canvas.width, 'x', canvas.height)
    console.log('[FRONTEND] Video dimensions:', video.videoWidth, 'x', video.videoHeight)
    
    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Scale factor (webcam is 640x480, but video might be different)
    const scaleX = canvas.width / 640
    const scaleY = canvas.height / 480
    
    console.log('[FRONTEND] Scale factors:', scaleX, scaleY)
    
    faces.forEach((face, idx) => {
      console.log(`[FRONTEND] Drawing face ${idx + 1}:`, face)
      
      const [x1, y1, x2, y2] = face.bbox
      const scaledX1 = x1 * scaleX
      const scaledY1 = y1 * scaleY
      const scaledX2 = x2 * scaleX
      const scaledY2 = y2 * scaleY
      const width = scaledX2 - scaledX1
      const height = scaledY2 - scaledY1
      
      console.log(`[FRONTEND] Face ${idx + 1} bbox:`, { x1, y1, x2, y2 })
      console.log(`[FRONTEND] Face ${idx + 1} scaled:`, { scaledX1, scaledY1, width, height })
      
      // Choose color based on recognition status
      if (face.recognized) {
        ctx.strokeStyle = '#00ff00'  // Green for recognized
        ctx.fillStyle = '#00ff00'
        console.log(`[FRONTEND] Face ${idx + 1} is RECOGNIZED - green box`)
      } else {
        ctx.strokeStyle = '#ff9800'  // Orange for detected but not recognized
        ctx.fillStyle = '#ff9800'
        console.log(`[FRONTEND] Face ${idx + 1} is UNKNOWN - orange box`)
      }
      
      ctx.lineWidth = 3
      
      // Draw rectangle
      ctx.strokeRect(scaledX1, scaledY1, width, height)
      console.log(`[FRONTEND] Drew rectangle at:`, scaledX1, scaledY1, width, height)
      
      // Draw label
      if (face.name) {
        const label = `${face.name} (${(face.confidence * 100).toFixed(0)}%)`
        console.log(`[FRONTEND] Drawing label:`, label)
        ctx.font = '16px Arial'
        const textWidth = ctx.measureText(label).width
        
        // Background for text
        ctx.fillRect(scaledX1, scaledY1 - 25, textWidth + 10, 25)
        ctx.fillStyle = '#ffffff'
        ctx.fillText(label, scaledX1 + 5, scaledY1 - 7)
      } else {
        const label = 'Unknown'
        console.log(`[FRONTEND] Drawing label: Unknown`)
        ctx.font = '16px Arial'
        const textWidth = ctx.measureText(label).width
        
        // Background for text
        ctx.fillRect(scaledX1, scaledY1 - 25, textWidth + 10, 25)
        ctx.fillStyle = '#ffffff'
        ctx.fillText(label, scaledX1 + 5, scaledY1 - 7)
      }
    })
    
    console.log('[FRONTEND] Finished drawing all bounding boxes')
  }

  const clearCanvas = () => {
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
  }

  const stopRecognition = () => {
    setRecognizing(false)
    if (recognitionIntervalRef.current) {
      clearInterval(recognitionIntervalRef.current)
    }
    clearCanvas()
  }

  const handleCameraChange = (e) => {
    const cameraId = parseInt(e.target.value)
    const camera = cameras.find((c) => c.id === cameraId)
    setSelectedCamera(camera)
    if (recognizing) {
      stopRecognition()
    }
    setRecognitionResults([])
  }

  if (loading) {
    return <div className="loading">Loading cameras...</div>
  }

  if (cameras.length === 0) {
    return (
      <div className="card">
        <div className="alert alert-info">
          No active cameras found. Please add and activate cameras first.
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Live Face Recognition</h1>
        <p className="page-subtitle">Real-time face detection and attendance marking</p>
      </div>

      <div className="card">
        <div className="camera-select">
          <label>Select Camera:</label>
          <select value={selectedCamera?.id || ''} onChange={handleCameraChange}>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.name} - {camera.location}
              </option>
            ))}
          </select>
        </div>

        <div className="recognition-container">
          <div className="video-section">
            <div className="video-container">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                width={640}
                height={480}
              />
              <canvas
                ref={canvasRef}
              />
              {recognizing && (
                <div className="recognition-overlay">
                  <div className="pulse-ring"></div>
                  <span>Recognizing...</span>
                </div>
              )}
            </div>

            <div className="recognition-controls">
              {!recognizing ? (
                <button onClick={startRecognition} className="btn btn-success btn-lg">
                  Start Recognition
                </button>
              ) : (
                <button onClick={stopRecognition} className="btn btn-danger btn-lg">
                  Stop Recognition
                </button>
              )}
            </div>
          </div>

          <div className="results-section">
            <h3>Recognition Results</h3>
            {recognitionResults.length > 0 ? (
              <div className="results-list">
                {recognitionResults.map((result, index) => (
                  <div key={index} className="result-item">
                    <div className="result-header">
                      <div className="avatar-small">
                        {result.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h4>{result.name}</h4>
                        <p className="roll-number">{result.roll_number}</p>
                      </div>
                    </div>
                    <div className="result-info">
                      <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
                      <div className="confidence-bar">
                        <div
                          className="confidence-fill"
                          style={{ width: `${result.confidence * 100}%` }}
                        ></div>
                      </div>
                      <p className="text-success">✓ Attendance Marked</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No faces recognized yet. Start recognition to begin.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default LiveRecognition
