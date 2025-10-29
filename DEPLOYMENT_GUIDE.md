# Quick Start & Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.8+ with conda
- Node.js 16+
- PostgreSQL 12+
- Downloaded models (SCRFD & ArcFace)

### 1. Start Backend
```powershell
# Activate environment
conda activate face

# Navigate to backend
cd backend

# Start server
uvicorn main:app --reload
```

Backend runs at: http://localhost:8000

### 2. Start Frontend
```powershell
# In a new terminal
cd frontend

# Start dev server
npm run dev
```

Frontend runs at: http://localhost:5173

### 3. Access System
- Open browser: http://localhost:5173
- Click **"Admin Login"**
- Start adding cameras and students!

---

## 📦 Production Deployment

### Backend Deployment

**Option 1: Using Gunicorn (Linux)**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

**Option 2: Using Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 3: Using systemd (Linux)**
```ini
[Unit]
Description=Face Recognition API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/conda/envs/face/bin"
ExecStart=/path/to/conda/envs/face/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Frontend Deployment

**Build for production:**
```powershell
cd frontend
npm run build
```

Output in `frontend/dist/`

**Deploy options:**
1. **Nginx**: Serve static files from `dist/`
2. **Apache**: Configure DocumentRoot to `dist/`
3. **CDN**: Upload to S3/CloudFront
4. **Node.js**: `npm run preview` or use serve package

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` in backend directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/attendance_db
FACE_DETECTION_THRESHOLD=0.3
FACE_RECOGNITION_THRESHOLD=0.55
FAISS_INDEX_TYPE=COSINE
```

### Frontend API URL

Update in `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = 'https://your-domain.com/api/v1'  // Production
// const API_BASE_URL = 'http://localhost:8000/api/v1'  // Development
```

---

## 📊 System Requirements

### Minimum (1-2 cameras, 50 students)
- CPU: 4 cores
- RAM: 8 GB
- Storage: 20 GB
- Network: 10 Mbps

### Recommended (4-8 cameras, 500 students)
- CPU: 8 cores
- RAM: 16 GB
- Storage: 50 GB SSD
- Network: 100 Mbps

### High Performance (10+ cameras, 1000+ students)
- CPU: 16 cores (or GPU)
- RAM: 32 GB
- Storage: 100 GB SSD
- Network: 1 Gbps

---

## 🔒 Security Checklist

### Before Deployment:
- [ ] Change database password
- [ ] Enable PostgreSQL SSL
- [ ] Add API authentication (JWT)
- [ ] Use HTTPS for frontend
- [ ] Secure camera credentials
- [ ] Set up firewall rules
- [ ] Enable CORS properly
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Configure backups

---

## 🧪 Testing Checklist

### Before Going Live:
- [ ] Test with all cameras
- [ ] Train at least 10 students
- [ ] Verify attendance marking
- [ ] Test different lighting conditions
- [ ] Check recognition accuracy
- [ ] Test grid and single camera views
- [ ] Verify database operations
- [ ] Test on target network
- [ ] Load test with multiple cameras
- [ ] Verify backup and restore

---

## 📈 Performance Optimization

### If System is Slow:

**1. Reduce Camera Load:**
```python
# backend/app/core/config.py
DEFAULT_CAMERA_FPS = 15  # Reduce from 30
FRAME_WIDTH = 640  # Reduce from 1280
FRAME_HEIGHT = 480  # Reduce from 720
```

**2. Enable GPU (if available):**
```python
# backend/app/services/face_detection.py
# Change providers to:
providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
```

**3. Optimize Database:**
```sql
-- Add indexes
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_camera ON attendance(camera_id);
```

**4. Use Connection Pooling:**
```python
# backend/app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## 🐛 Debugging

### Enable Verbose Logging:

**Backend:**
```python
# backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```javascript
// frontend/src/services/api.js
api.interceptors.request.use(config => {
  console.log('Request:', config)
  return config
})
```

### Common Issues:

**ONNX Model Not Found:**
```powershell
# Download models
cd backend/models
# Download from InsightFace model zoo
```

**Database Connection Failed:**
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Test connection
psql -U postgres -d attendance_db
```

**Camera Not Opening:**
```python
# Test camera access
import cv2
cap = cv2.VideoCapture(0)
print(cap.isOpened())
cap.release()
```

---

## 🔄 Update & Maintenance

### Regular Maintenance:
1. **Weekly**: Check system logs, verify accuracy
2. **Monthly**: Database backup, model export
3. **Quarterly**: Retrain students with new photos
4. **Yearly**: System audit, security review

### Update Procedure:
```powershell
# Backend
cd backend
git pull
pip install -r requirements.txt --upgrade
# Restart service

# Frontend
cd frontend
git pull
npm install
npm run build
# Deploy new build
```

---

## 📞 Support Contacts

### Issues & Bug Reports:
- GitHub Issues: [repository]/issues
- Email: support@yourdomain.com

### Documentation:
- Admin Guide: `ADMIN_GUIDE.md`
- API Docs: http://localhost:8000/docs
- Camera Setup: `CAMERA_SETUP_GUIDE.md`

---

## 🎯 Quick Commands Reference

```powershell
# Start development
conda activate face
cd backend && uvicorn main:app --reload
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Database backup
pg_dump attendance_db > backup_$(date +%Y%m%d).sql

# Model export
curl -X POST http://localhost:8000/api/v1/training/export-model

# Check system status
curl http://localhost:8000/api/v1/recognition/stats

# View logs
tail -f logs/app.log  # If configured
```

---

**Deployment Version**: 2.0.0
**Last Updated**: October 29, 2025
**Status**: Production Ready ✅
