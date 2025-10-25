import React, { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { studentsAPI, trainingAPI } from '../services/api'

function AddStudentModal({ student, onClose }) {
  const [formData, setFormData] = useState({
    roll_number: student?.roll_number || '',
    name: student?.name || '',
    email: student?.email || '',
    phone: student?.phone || '',
    department: student?.department || '',
    year: student?.year || 1,
    section: student?.section || '',
  })
  const [step, setStep] = useState(1) // 1: Details, 2: Training Choice, 3: Video Capture, 4: Photo Upload
  const [trainingMethod, setTrainingMethod] = useState(null) // 'video' or 'photos'
  const [capturing, setCapturing] = useState(false)
  const [capturedFrames, setCapturedFrames] = useState([])
  const [selectedPhotos, setSelectedPhotos] = useState([])
  const [loading, setLoading] = useState(false)
  const webcamRef = useRef(null)
  const captureIntervalRef = useRef(null)
  const fileInputRef = useRef(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  const handleNextStep = async () => {
    if (student) {
      // If editing existing student, just update details
      handleSubmit()
    } else {
      // For new student, go to training method selection
      setStep(2)
    }
  }

  const handleTrainingMethodSelect = (method) => {
    setTrainingMethod(method)
    if (method === 'video') {
      setStep(3)
    } else if (method === 'photos') {
      setStep(4)
    }
  }

  const handlePhotoSelect = (e) => {
    const files = Array.from(e.target.files)
    if (files.length > 0) {
      setSelectedPhotos(files)
    }
  }

  const handleSubmit = async () => {
    try {
      setLoading(true)

      if (student) {
        // Update existing student
        await studentsAPI.update(student.id, formData)
        alert('Student updated successfully')
        onClose(true)
      } else {
        // Create new student
        const response = await studentsAPI.create(formData)
        const newStudentId = response.data.id

        // Train based on selected method
        if (trainingMethod === 'video' && capturedFrames.length > 0) {
          const trainingData = {
            frames_base64: capturedFrames
          }

          try {
            await trainingAPI.trainStudentFrames(newStudentId, trainingData)
            alert('Student added and trained successfully with video!')
          } catch (err) {
            console.error('Training error:', err)
            alert('Student added but video training failed. Please train manually.')
          }
        } else if (trainingMethod === 'photos' && selectedPhotos.length > 0) {
          const formDataPhotos = new FormData()
          selectedPhotos.forEach((photo) => {
            formDataPhotos.append('photos', photo)
          })

          try {
            await trainingAPI.trainStudentPhotos(newStudentId, formDataPhotos)
            alert('Student added and trained successfully with photos!')
          } catch (err) {
            console.error('Training error:', err)
            alert('Student added but photo training failed. Please train manually.')
          }
        } else {
          alert('Student added successfully. Please train face recognition.')
        }

        onClose(true)
      }
    } catch (err) {
      console.error('Error saving student:', err)
      alert('Error saving student: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const startCapture = () => {
    setCapturing(true)
    setCapturedFrames([])

    let frameCount = 0
    const maxFrames = 50

    captureIntervalRef.current = setInterval(() => {
      if (frameCount >= maxFrames) {
        stopCapture()
        return
      }

      const imageSrc = webcamRef.current?.getScreenshot()
      if (imageSrc) {
        setCapturedFrames((prev) => [...prev, imageSrc.split(',')[1]]) // Remove data:image/jpeg;base64, prefix
        frameCount++
      }
    }, 200) // Capture every 200ms
  }

  const stopCapture = () => {
    setCapturing(false)
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current)
    }
  }

  const handleSkipVideo = () => {
    handleSubmit()
  }

  return (
    <div className="modal-overlay">
      <div className="modal modal-large">
        <div className="modal-header">
          <h2 className="modal-title">
            {student ? 'Edit Student' : 'Add New Student'}
          </h2>
          <button className="close-btn" onClick={() => onClose(false)}>
            ×
          </button>
        </div>

        {step === 1 && (
          <div className="modal-body">
            <div className="form-group">
              <label>Roll Number *</label>
              <input
                type="text"
                name="roll_number"
                value={formData.roll_number}
                onChange={handleInputChange}
                required
                disabled={!!student}
              />
            </div>

            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label>Department</label>
              <input
                type="text"
                name="department"
                value={formData.department}
                onChange={handleInputChange}
              />
            </div>

            <div className="grid grid-2">
              <div className="form-group">
                <label>Year</label>
                <select name="year" value={formData.year} onChange={handleInputChange}>
                  <option value={1}>1st Year</option>
                  <option value={2}>2nd Year</option>
                  <option value={3}>3rd Year</option>
                  <option value={4}>4th Year</option>
                </select>
              </div>

              <div className="form-group">
                <label>Section</label>
                <input
                  type="text"
                  name="section"
                  value={formData.section}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="modal-actions">
              <button
                onClick={() => onClose(false)}
                className="btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleNextStep}
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? 'Saving...' : student ? 'Update' : 'Next: Training'}
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="modal-body">
            <div className="training-method-selection">
              <h3>Select Training Method</h3>
              <p>Choose how you want to train the face recognition system:</p>

              <div className="training-methods">
                <div 
                  className="training-method-card"
                  onClick={() => handleTrainingMethodSelect('video')}
                >
                  <div className="method-icon">📹</div>
                  <h4>Live Video Capture</h4>
                  <p>Capture live video frames from your webcam</p>
                  <ul>
                    <li>✓ Quick and easy</li>
                    <li>✓ Multiple angles automatically</li>
                    <li>✓ 50 frames captured</li>
                  </ul>
                  <button className="btn btn-primary">Use Video</button>
                </div>

                <div 
                  className="training-method-card"
                  onClick={() => handleTrainingMethodSelect('photos')}
                >
                  <div className="method-icon">📷</div>
                  <h4>Upload Photos</h4>
                  <p>Upload existing photos from your device</p>
                  <ul>
                    <li>✓ Use existing photos</li>
                    <li>✓ Multiple photos supported</li>
                    <li>✓ Higher quality</li>
                  </ul>
                  <button className="btn btn-success">Upload Photos</button>
                </div>
              </div>

              <div className="modal-actions">
                <button
                  onClick={() => setStep(1)}
                  className="btn btn-secondary"
                >
                  Back
                </button>
                <button
                  onClick={() => handleSubmit()}
                  className="btn btn-secondary"
                >
                  Skip Training
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="modal-body">
            <div className="video-capture-container">
              <h3>Capture Training Video</h3>
              <p>Position your face in the camera and click "Start Capture". Keep your face visible and move slightly to capture different angles.</p>

              <div className="video-container">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  width={640}
                  height={480}
                />
              </div>

              <div className="capture-info">
                <p>Captured Frames: {capturedFrames.length} / 50</p>
                {capturing && <p className="text-success">Capturing...</p>}
              </div>

              <div className="modal-actions">
                <button
                  onClick={() => setStep(2)}
                  className="btn btn-secondary"
                  disabled={loading || capturing}
                >
                  Back
                </button>
                <button
                  onClick={handleSkipVideo}
                  className="btn btn-secondary"
                  disabled={loading || capturing}
                >
                  Skip Video
                </button>
                {!capturing ? (
                  <button
                    onClick={startCapture}
                    className="btn btn-success"
                    disabled={loading}
                  >
                    Start Capture
                  </button>
                ) : (
                  <button
                    onClick={stopCapture}
                    className="btn btn-danger"
                  >
                    Stop Capture
                  </button>
                )}
                {capturedFrames.length > 0 && !capturing && (
                  <button
                    onClick={handleSubmit}
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? 'Processing...' : 'Complete Registration'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="modal-body">
            <div className="photo-upload-container">
              <h3>Upload Training Photos</h3>
              <p>Upload multiple photos of the student from different angles. Minimum 5 photos recommended.</p>

              <div className="upload-section">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handlePhotoSelect}
                  accept="image/*"
                  multiple
                  style={{ display: 'none' }}
                />
                
                <button 
                  className="btn btn-primary btn-upload"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                >
                  📁 Select Photos
                </button>

                {selectedPhotos.length > 0 && (
                  <div className="selected-photos-info">
                    <p className="text-success">✓ {selectedPhotos.length} photo(s) selected</p>
                    <div className="photo-preview-grid">
                      {selectedPhotos.slice(0, 6).map((photo, index) => (
                        <div key={index} className="photo-preview">
                          <img 
                            src={URL.createObjectURL(photo)} 
                            alt={`Preview ${index + 1}`}
                          />
                        </div>
                      ))}
                      {selectedPhotos.length > 6 && (
                        <div className="photo-preview more-photos">
                          +{selectedPhotos.length - 6} more
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="upload-tips">
                <h4>Tips for best results:</h4>
                <ul>
                  <li>📸 Upload at least 5-10 photos</li>
                  <li>👤 Include different angles and expressions</li>
                  <li>💡 Ensure good lighting</li>
                  <li>📏 Face should be clearly visible</li>
                  <li>🚫 Avoid blurry or low-quality images</li>
                </ul>
              </div>

              <div className="modal-actions">
                <button
                  onClick={() => setStep(2)}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Back
                </button>
                <button
                  onClick={() => handleSubmit()}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Skip Photos
                </button>
                {selectedPhotos.length > 0 && (
                  <button
                    onClick={handleSubmit}
                    className="btn btn-success"
                    disabled={loading}
                  >
                    {loading ? 'Uploading & Training...' : `Upload ${selectedPhotos.length} Photo(s) & Train`}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AddStudentModal
