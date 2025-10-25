# Real-Time Face Recognition Attendance System

A comprehensive real-time face recognition and attendance system for colleges with multi-camera support, AI-powered face detection and recognition, and dual dashboards for students and administrators.

## 🚀 Features

### Core Functionality
- **Real-time Face Recognition**: Uses SCRFD for detection and ArcFace for recognition
- **Multi-Camera Support**: Monitor and process multiple CCTV cameras simultaneously
- **Vector Database**: FAISS for efficient face embedding storage and retrieval
- **Persistent Storage**: PostgreSQL for student details and attendance records
- **RESTful API**: FastAPI backend with comprehensive endpoints

### Student Dashboard
- View attendance percentage and statistics
- Check present/absent status for the day
- See detailed attendance history with timestamps
- View which camera detected them
- Display recognition confidence scores

### Admin Dashboard
- **Dashboard Overview**: 
  - Total students count
  - Students present today
  - Attendance percentage
  - Model statistics
  
- **Student Management**:
  - Add new students via frontend
  - Capture training video through webcam
  - Edit student details
  - Delete students (removes from both DB and vector DB)
  - View all student records with search
  
- **Camera Management**:
  - Add new cameras with IP addresses
  - Edit camera configurations (FPS, resolution, location)
  - Activate/deactivate cameras
  - Delete cameras
  
- **Live Recognition**:
  - Switch between cameras in real-time
  - View live recognition results
  - Automatic attendance marking
  - Display confidence scores
  
- **Attendance Management**:
  - View attendance records by date
  - Search and filter records
  - Export to CSV
  - Delete incorrect records

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py      # API router
│   │       └── endpoints/  # API endpoints
│   │           ├── students.py
│   │           ├── attendance.py
│   │           ├── cameras.py
│   │           ├── recognition.py
│   │           └── training.py
│   ├── core/
│   │   ├── config.py       # Configuration settings
│   │   └── database.py     # Database connection
│   ├── models/             # SQLAlchemy models
│   │   ├── student.py
│   │   ├── attendance.py
│   │   ├── camera.py
│   │   └── admin.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── student.py
│   │   ├── attendance.py
│   │   └── camera.py
│   └── services/           # Business logic
│       ├── face_detection.py    # SCRFD face detection
│       ├── face_recognition.py  # ArcFace recognition
│       ├── faiss_service.py     # FAISS vector DB
│       ├── video_service.py     # Video processing
│       └── training_service.py  # Model training
└── models/                 # ML models directory
    ├── scrfd_10g_bnkps.onnx
    ├── w600k_r50.onnx
    ├── faiss_index.bin
    └── face_embeddings.pkl
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── StudentsManagement.jsx
│   │   ├── AddStudentModal.jsx
│   │   ├── CamerasManagement.jsx
│   │   ├── LiveRecognition.jsx
│   │   ├── AttendanceManagement.jsx
│   │   └── Components.css
│   ├── pages/
│   │   ├── HomePage.jsx
│   │   ├── StudentDashboard.jsx
│   │   └── AdminDashboard.jsx
│   ├── services/
│   │   └── api.js          # API client
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## 📋 Prerequisites

### System Requirements
- Python 3.8 or higher
- Node.js 16 or higher
- PostgreSQL 12 or higher
- Conda (Anaconda/Miniconda)
- Webcam or IP cameras
- GPU (optional, but recommended for better performance)

### Conda Environment
You should already have a conda environment named `face` with the required packages installed.

## 🔧 Installation & Setup

### 1. Database Setup

Install and start PostgreSQL:

```powershell
# Create database
psql -U postgres
CREATE DATABASE attendance_db;
\q
```

### 2. Download Pre-trained Models

Download the following ONNX models and place them in the `backend/models/` directory:

**SCRFD Face Detection Model:**
- Model: `scrfd_10g_bnkps.onnx`
- Download from: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/tree/master/detection/scrfd)
- Direct link: [SCRFD Models](https://github.com/deepinsight/insightface/releases/tag/v0.7)

**ArcFace Recognition Model:**
- Model: `w600k_r50.onnx`
- Download from: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/tree/master/model_zoo)
- Recommended: MS1MV3-Arcface-R50

```powershell
# Create models directory
mkdir backend\models
# Place downloaded models in backend\models\
```

### 3. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Activate conda environment
conda activate face

# Create .env file from example
copy .env.example .env

# Edit .env file and update database credentials
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/attendance_db
```

### 4. Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend Server

```powershell
# Activate conda environment
conda activate face

# Navigate to backend
cd backend

# Run FastAPI server
python main.py
```

The backend API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Start Frontend Development Server

```powershell
# Navigate to frontend (in a new terminal)
cd frontend

# Start Vite dev server
npm run dev
```

The frontend will be available at: `http://localhost:3000`

## 📱 Usage Guide

### For Students

1. Open `http://localhost:3000`
2. Enter your roll number in the Student Portal
3. View your attendance statistics, today's status, and history

### For Administrators

1. Open `http://localhost:3000`
2. Enter admin password in Admin Portal (default: `admin123`)
3. Access the admin dashboard with all management features

#### Adding a New Student

1. Go to **Students** tab
2. Click **+ Add New Student**
3. Fill in student details
4. Click **Next: Capture Video**
5. Position face in camera and click **Start Capture**
6. System will capture 50 frames automatically
7. Click **Complete Registration** to train the model

#### Adding a Camera

1. Go to **Cameras** tab
2. Click **+ Add New Camera**
3. Enter camera details:
   - Name: e.g., "Entrance Camera"
   - IP Address: e.g., `rtsp://192.168.1.100:554` or `0` for default webcam
   - Location: e.g., "Main Building Entrance"
4. Click **Add Camera**

#### Live Recognition

1. Go to **Live Recognition** tab
2. Select a camera from the dropdown
3. Click **Start Recognition**
4. System will detect and recognize faces automatically
5. Attendance is marked in real-time

#### Managing Attendance

1. Go to **Attendance** tab
2. Select date to view records
3. Search for specific students
4. Export to CSV for reports
5. Delete incorrect records if needed

## 🔌 API Endpoints

### Students
- `GET /api/v1/students` - Get all students
- `GET /api/v1/students/{id}` - Get student by ID
- `GET /api/v1/students/roll/{roll_number}` - Get student by roll number
- `POST /api/v1/students` - Create new student
- `PUT /api/v1/students/{id}` - Update student
- `DELETE /api/v1/students/{id}` - Delete student

### Attendance
- `GET /api/v1/attendance` - Get attendance records
- `GET /api/v1/attendance/stats` - Get attendance statistics
- `GET /api/v1/attendance/today` - Get today's attendance
- `POST /api/v1/attendance` - Mark attendance
- `DELETE /api/v1/attendance/{id}` - Delete record

### Cameras
- `GET /api/v1/cameras` - Get all cameras
- `POST /api/v1/cameras` - Create new camera
- `PUT /api/v1/cameras/{id}` - Update camera
- `DELETE /api/v1/cameras/{id}` - Delete camera
- `POST /api/v1/cameras/{id}/toggle` - Toggle camera status

### Recognition
- `POST /api/v1/recognition/recognize-frame` - Recognize faces in frame
- `POST /api/v1/recognition/recognize-file` - Recognize faces in uploaded image
- `GET /api/v1/recognition/stats` - Get recognition statistics

### Training
- `POST /api/v1/training/train-student/{id}` - Train with video file
- `POST /api/v1/training/train-student-frames/{id}` - Train with frames
- `DELETE /api/v1/training/remove-student/{id}` - Remove training data
- `GET /api/v1/training/model-stats` - Get model statistics
- `POST /api/v1/training/export-model` - Export model as pickle
- `POST /api/v1/training/save-model` - Save current model

## 🎨 Customization

### Change Admin Password

Edit `frontend/src/pages/HomePage.jsx`:
```javascript
if (adminPassword === 'admin123') {  // Change 'admin123' to your password
```

### Adjust Recognition Settings

Edit `backend/.env`:
```env
FACE_DETECTION_THRESHOLD=0.5      # Lower = more detections
FACE_RECOGNITION_THRESHOLD=0.4    # Lower = stricter matching
FRAMES_PER_STUDENT=50              # Number of training frames
```

### Camera Settings

Edit `backend/.env`:
```env
DEFAULT_CAMERA_FPS=30
FRAME_WIDTH=640
FRAME_HEIGHT=480
```

## 🐛 Troubleshooting

### Model Not Found Error
- Ensure ONNX models are downloaded to `backend/models/`
- Check file names match exactly: `scrfd_10g_bnkps.onnx` and `w600k_r50.onnx`

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database `attendance_db` exists

### Camera Not Working
- Check camera permissions in browser
- For IP cameras, verify RTSP URL is correct
- Test camera separately before using in app

### Low Recognition Accuracy
- Ensure good lighting conditions
- Capture more training frames (50+)
- Use multiple angles during training
- Adjust `FACE_RECOGNITION_THRESHOLD` in `.env`

### Import Errors
- Activate conda environment: `conda activate face`
- Verify all packages in `requirements.txt` are installed

## 📊 Model Information

### SCRFD (Face Detection)
- Architecture: Sample and Computation Redistribution
- Purpose: Fast and accurate face detection
- Input: RGB image
- Output: Face bounding boxes and landmarks

### ArcFace (Face Recognition)
- Architecture: ResNet-50 with ArcFace loss
- Purpose: Face embedding generation
- Embedding Dimension: 512
- Similarity Metric: Cosine similarity (L2 distance)

### FAISS (Vector Database)
- Index Type: IndexFlatL2
- Purpose: Fast similarity search
- Supports: Add, search, and delete operations

## 🔒 Security Considerations

**For Production Deployment:**

1. **Authentication**: Implement proper JWT-based authentication
2. **Password Hashing**: Use bcrypt for admin passwords
3. **CORS**: Restrict allowed origins in FastAPI
4. **HTTPS**: Use SSL certificates for production
5. **Database**: Use environment variables for credentials
6. **Rate Limiting**: Add API rate limiting
7. **Input Validation**: Validate all user inputs

## 📝 License

This project is for educational purposes. Ensure you have proper permissions for face recognition deployment in your institution.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 👥 Credits

- **SCRFD**: [InsightFace](https://github.com/deepinsight/insightface)
- **ArcFace**: [InsightFace](https://github.com/deepinsight/insightface)
- **FAISS**: [Facebook Research](https://github.com/facebookresearch/faiss)

## 📧 Support

For issues or questions, please check the troubleshooting section or raise an issue on the repository.

---

**Built with ❤️ using FastAPI, React, SCRFD, ArcFace, FAISS, and PostgreSQL**
