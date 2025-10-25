# Setup Commands - Face Recognition Attendance System

## Complete Setup Process

### 1. Prerequisites Check
```powershell
# Check Python version
python --version
# Should be 3.8 or higher

# Check Node.js version
node --version
# Should be 16 or higher

# Check conda
conda --version

# Check PostgreSQL
psql --version
```

### 2. Database Setup
```powershell
# Create database
psql -U postgres
```
```sql
CREATE DATABASE attendance_db;
\q
```

### 3. Backend Setup
```powershell
# Navigate to backend
cd "C:\Users\Thiya\OneDrive\Documents\New Face\backend"

# Activate conda environment
conda activate face

# Verify packages (should already be installed)
pip list | findstr "fastapi sqlalchemy opencv"

# Create .env file
copy .env.example .env

# Edit .env and update DATABASE_URL
notepad .env
# Update: DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/attendance_db

# Create models directory
mkdir models

# Download models (see MODEL_DOWNLOAD.md)
# Place scrfd_10g_bnkps.onnx and w600k_r50.onnx in models/

# Initialize database tables
python scripts\init_db.py

# Start backend server
python main.py
```

### 4. Frontend Setup (New Terminal)
```powershell
# Navigate to frontend
cd "C:\Users\Thiya\OneDrive\Documents\New Face\frontend"

# Install dependencies
npm install

# Start development server
npm run dev
```

## Running the Application

### Start Backend
```powershell
conda activate face
cd backend
python main.py
```
Backend runs on: http://localhost:8000

### Start Frontend
```powershell
cd frontend
npm run dev
```
Frontend runs on: http://localhost:3000

## Testing the Setup

### 1. Test Backend API
```powershell
# In browser, open:
http://localhost:8000/docs

# Or use curl:
curl http://localhost:8000/health
```

### 2. Test Database Connection
```powershell
conda activate face
cd backend
python -c "from app.core.database import engine; print('Database connected!' if engine else 'Failed')"
```

### 3. Test Model Loading
```powershell
conda activate face
cd backend
python -c "from app.services.face_detection import get_detector; d = get_detector(); print('SCRFD loaded!')"
python -c "from app.services.face_recognition import get_recognizer; r = get_recognizer(); print('ArcFace loaded!')"
```

## First Time Usage Commands

### As Admin - Add Test Student
```powershell
# 1. Open browser: http://localhost:3000
# 2. Click "Admin Portal"
# 3. Password: admin123
# 4. Follow UI to add student
```

### Using API Directly
```powershell
# Add student via API
curl -X POST "http://localhost:8000/api/v1/students" ^
  -H "Content-Type: application/json" ^
  -d "{\"roll_number\":\"TEST001\",\"name\":\"Test Student\",\"email\":\"test@test.com\",\"department\":\"CS\",\"year\":1,\"section\":\"A\"}"

# Get all students
curl http://localhost:8000/api/v1/students

# Get attendance stats
curl http://localhost:8000/api/v1/attendance/stats
```

## Maintenance Commands

### Update Dependencies
```powershell
# Backend
conda activate face
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

### Database Operations
```powershell
# Backup database
pg_dump -U postgres attendance_db > backup.sql

# Restore database
psql -U postgres attendance_db < backup.sql

# Reset database (CAUTION: Deletes all data!)
psql -U postgres
DROP DATABASE attendance_db;
CREATE DATABASE attendance_db;
\q

# Reinitialize tables
python scripts\init_db.py
```

### Clear Model Data
```powershell
# Remove FAISS index and embeddings (will need to retrain all students)
cd backend\models
del faiss_index.bin
del face_embeddings.pkl
```

### View Logs
```powershell
# Backend logs are in terminal
# For detailed logging, add to main.py:
# import logging
# logging.basicConfig(level=logging.DEBUG)
```

## Stopping the Application

### Stop Backend
Press `Ctrl + C` in backend terminal

### Stop Frontend
Press `Ctrl + C` in frontend terminal

### Stop PostgreSQL (if needed)
```powershell
# Windows Services
services.msc
# Find PostgreSQL service and stop it
```

## Production Deployment Commands

### Build Frontend
```powershell
cd frontend
npm run build
# Output in frontend/dist/
```

### Run Backend with Production Settings
```powershell
conda activate face
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using PM2 (Process Manager)
```powershell
# Install PM2
npm install -g pm2

# Start backend with PM2
pm2 start "python main.py" --name face-backend

# Start frontend (after build, with serve)
npm install -g serve
pm2 start "serve -s dist -l 3000" --name face-frontend

# View status
pm2 status

# View logs
pm2 logs

# Stop all
pm2 stop all
```

## Troubleshooting Commands

### Check Port Usage
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process by PID
taskkill /F /PID <PID>
```

### Check PostgreSQL Status
```powershell
# Check if PostgreSQL is running
sc query postgresql-x64-14
# (version number may vary)

# Start PostgreSQL service
net start postgresql-x64-14
```

### Reinstall Frontend Dependencies
```powershell
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
```

### Reset Python Environment
```powershell
# Deactivate and reactivate
conda deactivate
conda activate face

# Reinstall packages
pip install -r requirements.txt --force-reinstall
```

## Development Workflow

### Daily Startup
```powershell
# Terminal 1 - Backend
conda activate face
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Making Changes

**Backend changes:**
- FastAPI auto-reloads on file changes
- No restart needed (unless changing .env)

**Frontend changes:**
- Vite HMR updates instantly
- No restart needed

**Database schema changes:**
```powershell
# 1. Update model in app/models/
# 2. Drop and recreate database OR use migrations
# 3. Reinitialize:
python scripts\init_db.py
```

## Useful Aliases (Optional)

Add to PowerShell profile:
```powershell
# Edit profile
notepad $PROFILE

# Add these aliases:
function Start-FaceBackend {
    conda activate face
    cd "C:\Users\Thiya\OneDrive\Documents\New Face\backend"
    python main.py
}

function Start-FaceFrontend {
    cd "C:\Users\Thiya\OneDrive\Documents\New Face\frontend"
    npm run dev
}

# Save and reload
. $PROFILE

# Now you can use:
Start-FaceBackend
Start-FaceFrontend
```

---

**Quick Reference:**
- Backend: `conda activate face && cd backend && python main.py`
- Frontend: `cd frontend && npm run dev`
- API Docs: http://localhost:8000/docs
- Application: http://localhost:3000
- Admin Password: `admin123`
