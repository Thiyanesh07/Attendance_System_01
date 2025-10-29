import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Students API
export const studentsAPI = {
  getAll: (params) => api.get('/students', { params }),
  getById: (id) => api.get(`/students/${id}`),
  getByRoll: (rollNumber) => api.get(`/students/roll/${rollNumber}`),
  create: (data) => api.post('/students', data),
  update: (id, data) => api.put(`/students/${id}`, data),
  delete: (id) => api.delete(`/students/${id}`),
  getAttendance: (id, params) => api.get(`/students/${id}/attendance`, { params }),
}

// Attendance API
export const attendanceAPI = {
  getAll: (params) => api.get('/attendance', { params }),
  getStats: (params) => api.get('/attendance/stats', { params }),
  getToday: () => api.get('/attendance/today'),
  mark: (data) => api.post('/attendance', data),
  delete: (id) => api.delete(`/attendance/${id}`),
}

// Cameras API
export const camerasAPI = {
  getAll: (params) => api.get('/cameras', { params }),
  getById: (id) => api.get(`/cameras/${id}`),
  create: (data) => api.post('/cameras', data),
  update: (id, data) => api.put(`/cameras/${id}`, data),
  delete: (id) => api.delete(`/cameras/${id}`),
  toggle: (id) => api.post(`/cameras/${id}/toggle`),
  testConnection: (data) => api.post('/cameras/test-connection', data),
  snapshot: (id, params) => api.get(`/cameras/${id}/snapshot`, { params, responseType: 'blob' }),
  startBg: (id, params) => api.post(`/cameras/${id}/start-bg`, null, { params }),
  stopBg: (id) => api.post(`/cameras/${id}/stop-bg`),
  status: (id) => api.get(`/cameras/${id}/status`),
  startAllBg: (params) => api.post('/cameras/start-all-bg', null, { params }),
  stopAllBg: () => api.post('/cameras/stop-all-bg'),
  allBgStatus: () => api.get('/cameras/bg-status'),
}

// Recognition API
export const recognitionAPI = {
  recognizeFrame: (data) => api.post('/recognition/recognize-frame', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  recognizeFile: (data) => api.post('/recognition/recognize-file', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getStats: () => api.get('/recognition/stats'),
}

// Training API
export const trainingAPI = {
  trainStudent: (studentId, data) => api.post(`/training/train-student/${studentId}`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  trainStudentFrames: (studentId, data) => api.post(`/training/train-student-frames/${studentId}`, data),
  trainStudentPhotos: (studentId, data) => api.post(`/training/train-student-photos/${studentId}`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  removeStudent: (studentId) => api.delete(`/training/remove-student/${studentId}`),
  getModelStats: () => api.get('/training/model-stats'),
  exportModel: () => api.post('/training/export-model'),
  saveModel: () => api.post('/training/save-model'),
}

export default api
