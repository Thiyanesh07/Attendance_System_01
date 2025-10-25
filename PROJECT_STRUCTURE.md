# Project Structure

```
New Face/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Application entry point
│   ├── .env                          # Environment variables (create from .env.example)
│   ├── .env.example                  # Environment variables template
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   │
│   │   ├── api/                      # API Layer
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── api.py            # Main API router
│   │   │       └── endpoints/        # API endpoints
│   │   │           ├── __init__.py
│   │   │           ├── students.py   # Student CRUD operations
│   │   │           ├── attendance.py # Attendance management
│   │   │           ├── cameras.py    # Camera management
│   │   │           ├── recognition.py# Face recognition endpoints
│   │   │           └── training.py   # Model training endpoints
│   │   │
│   │   ├── core/                     # Core configurations
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # App configuration & settings
│   │   │   └── database.py           # Database connection setup
│   │   │
│   │   ├── models/                   # SQLAlchemy ORM Models
│   │   │   ├── __init__.py
│   │   │   ├── student.py            # Student database model
│   │   │   ├── attendance.py         # Attendance database model
│   │   │   ├── camera.py             # Camera database model
│   │   │   └── admin.py              # Admin database model
│   │   │
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── student.py            # Student request/response schemas
│   │   │   ├── attendance.py         # Attendance schemas
│   │   │   └── camera.py             # Camera schemas
│   │   │
│   │   └── services/                 # Business Logic Layer
│   │       ├── __init__.py
│   │       ├── face_detection.py     # SCRFD face detection service
│   │       ├── face_recognition.py   # ArcFace face recognition service
│   │       ├── faiss_service.py      # FAISS vector database service
│   │       ├── video_service.py      # Video capture & processing
│   │       └── training_service.py   # Model training & management
│   │
│   ├── models/                       # ML Models & Data (create this)
│   │   ├── scrfd_10g_bnkps.onnx     # SCRFD face detection model
│   │   ├── w600k_r50.onnx           # ArcFace recognition model
│   │   ├── faiss_index.bin          # FAISS index (generated)
│   │   ├── face_embeddings.pkl      # Face embeddings metadata (generated)
│   │   └── face_recognition_model.pkl # Exported model (optional)
│   │
│   └── uploads/                      # File uploads (auto-created)
│       └── students/                 # Student photos
│
├── frontend/                         # React Frontend
│   ├── index.html                    # HTML entry point
│   ├── vite.config.js               # Vite configuration
│   ├── package.json                  # NPM dependencies
│   │
│   ├── src/
│   │   ├── main.jsx                  # React entry point
│   │   ├── App.jsx                   # Main App component with routing
│   │   ├── App.css                   # App-level styles
│   │   ├── index.css                 # Global styles
│   │   │
│   │   ├── pages/                    # Page Components
│   │   │   ├── HomePage.jsx          # Landing page with login
│   │   │   ├── HomePage.css
│   │   │   ├── StudentDashboard.jsx  # Student dashboard
│   │   │   ├── StudentDashboard.css
│   │   │   ├── AdminDashboard.jsx    # Admin dashboard
│   │   │   └── AdminDashboard.css
│   │   │
│   │   ├── components/               # Reusable Components
│   │   │   ├── StudentsManagement.jsx    # Student management component
│   │   │   ├── AddStudentModal.jsx       # Add/Edit student modal
│   │   │   ├── CamerasManagement.jsx     # Camera management component
│   │   │   ├── LiveRecognition.jsx       # Live face recognition
│   │   │   ├── AttendanceManagement.jsx  # Attendance records view
│   │   │   └── Components.css            # Component styles
│   │   │
│   │   └── services/                 # API Service Layer
│   │       └── api.js                # Axios API client
│   │
│   └── node_modules/                 # NPM packages (auto-generated)
│
├── requirements.txt                  # Python dependencies
├── README.md                         # Main documentation
├── QUICKSTART.md                     # Quick start guide
├── MODEL_DOWNLOAD.md                 # Model download instructions
└── PROJECT_STRUCTURE.md              # This file
```

## Directory Descriptions

### Backend Structure

#### `/backend/app/api/`
Contains all API endpoints organized by feature:
- **students.py**: CRUD operations for student records
- **attendance.py**: Attendance marking and retrieval
- **cameras.py**: Camera management endpoints
- **recognition.py**: Real-time face recognition
- **training.py**: Model training and management

#### `/backend/app/core/`
Core application configuration:
- **config.py**: Centralized settings using Pydantic
- **database.py**: SQLAlchemy engine and session management

#### `/backend/app/models/`
Database models using SQLAlchemy ORM:
- **student.py**: Student information table
- **attendance.py**: Attendance records table
- **camera.py**: Camera configurations table
- **admin.py**: Admin users table

#### `/backend/app/schemas/`
Pydantic schemas for request/response validation:
- Input validation
- Output serialization
- Type checking

#### `/backend/app/services/`
Business logic and AI services:
- **face_detection.py**: SCRFD integration for face detection
- **face_recognition.py**: ArcFace integration for face recognition
- **faiss_service.py**: Vector database operations
- **video_service.py**: Video capture and frame extraction
- **training_service.py**: Model training orchestration

### Frontend Structure

#### `/frontend/src/pages/`
Main page components:
- **HomePage**: Landing page with login portals
- **StudentDashboard**: Student attendance view
- **AdminDashboard**: Admin control panel

#### `/frontend/src/components/`
Reusable UI components:
- **StudentsManagement**: Student list and management
- **AddStudentModal**: Student form with video capture
- **CamerasManagement**: Camera configuration
- **LiveRecognition**: Real-time face recognition UI
- **AttendanceManagement**: Attendance records table

#### `/frontend/src/services/`
API communication layer:
- **api.js**: Axios instance with all API endpoints

## Data Flow

### Student Registration Flow
```
Frontend (AddStudentModal)
    ↓ (Student details + video frames)
API (students.py + training.py)
    ↓ (Save to database + process frames)
Services (training_service.py)
    ↓ (Extract faces + generate embeddings)
FAISS (faiss_service.py)
    ↓ (Store embeddings)
Database (PostgreSQL)
    ↓ (Store student details)
```

### Face Recognition Flow
```
Camera/Webcam
    ↓ (Video frames)
Frontend (LiveRecognition)
    ↓ (Base64 encoded frames)
API (recognition.py)
    ↓ (Decode frames)
Services (face_detection.py)
    ↓ (Detect faces)
Services (face_recognition.py)
    ↓ (Generate embeddings)
FAISS (faiss_service.py)
    ↓ (Search similar embeddings)
Database (attendance.py)
    ↓ (Mark attendance)
Frontend
    ↓ (Display results)
```

## File Naming Conventions

- **Python files**: `snake_case.py`
- **React components**: `PascalCase.jsx`
- **CSS files**: `PascalCase.css` (matching component)
- **Config files**: `lowercase.config.js`
- **Documentation**: `UPPERCASE.md`

## Key Technologies by Directory

### Backend
- **FastAPI**: Modern web framework
- **SQLAlchemy**: ORM for database
- **Pydantic**: Data validation
- **ONNX Runtime**: Model inference
- **OpenCV**: Image processing
- **FAISS**: Vector similarity search
- **PostgreSQL**: Database

### Frontend
- **React 18**: UI library
- **React Router**: Navigation
- **Vite**: Build tool
- **Axios**: HTTP client
- **react-webcam**: Camera access
- **date-fns**: Date formatting

## Environment Files

### Backend `.env`
```env
DATABASE_URL=postgresql://...
SCRFD_MODEL_PATH=models/scrfd_10g_bnkps.onnx
ARCFACE_MODEL_PATH=models/w600k_r50.onnx
FACE_DETECTION_THRESHOLD=0.5
FACE_RECOGNITION_THRESHOLD=0.4
```

### Frontend
Configuration in `vite.config.js`:
```javascript
server: {
  port: 3000,
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## Generated Files & Directories

These are created automatically at runtime:

- `backend/models/faiss_index.bin` - FAISS index file
- `backend/models/face_embeddings.pkl` - Embeddings metadata
- `backend/uploads/` - Uploaded files
- `frontend/node_modules/` - NPM dependencies
- `frontend/dist/` - Production build (after `npm run build`)

## Development vs Production

### Development
- Backend: `python main.py` (with auto-reload)
- Frontend: `npm run dev` (with HMR)
- API docs available at `/docs`

### Production
- Backend: Use `uvicorn` with production settings
- Frontend: Build with `npm run build`, serve with nginx/apache
- Disable debug mode, enable HTTPS, add authentication

---

This structure provides clear separation of concerns, making the codebase maintainable and scalable!
