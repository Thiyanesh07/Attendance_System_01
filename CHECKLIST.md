# Setup Checklist ✅

Follow this checklist step-by-step to get your system running.

## Phase 1: Prerequisites ✅

- [x] Conda environment `face` exists
- [x] All packages from requirements.txt are installed
- [x] PostgreSQL is installed and running
- [x] Node.js 16+ is installed (tested with v22.21.0)
- [x] GPU support configured (NVIDIA RTX 3050 6GB with CUDA)
- [x] Internet access to download models available

**Commands to verify:**
```powershell
conda activate face
python --version          # Should show Python 3.10.0
node --version           # Should show v22.21.0
psql --version           # Should show PostgreSQL 15.14
python backend/check_gpu.py  # Should show GPU enabled
```

### ✅ Verified Environment Status

- **Conda environment**: `face` (activated)
- **Python**: 3.10.0
- **Node.js**: v22.21.0
- **PostgreSQL**: 15.14
- **GPU**: NVIDIA GeForce RTX 3050 6GB
- **CUDA**: 12.6 (with CUDA 11.8 libraries via conda)
- **cuDNN**: Installed via conda-forge
- **ONNX Runtime GPU**: 1.19.2 with CUDAExecutionProvider
- **GPU Status**: ✅ Fully operational and enabled

---

## Phase 1.5: GPU Setup (Optional - For Better Performance) 🚀

- [x] NVIDIA GPU available (RTX 3050 6GB)
- [x] CUDA Toolkit installed (12.6)
- [x] ONNX Runtime GPU installed (1.19.2)
- [x] cuDNN installed via conda
- [x] GPU detection verified
- [x] Models loading on GPU successfully

**Commands to setup:**
```powershell
conda activate face

# Install ONNX Runtime GPU
pip install onnxruntime-gpu==1.19.2

# Install cuDNN via conda
conda install -c conda-forge cudnn

# Verify GPU is working
cd backend
python check_gpu.py
```

**Success indicators:**
```
✅ CUDA (GPU) is available!
✅ GPU acceleration ENABLED (CUDA)
GPU Name: NVIDIA GeForce RTX 3050 6GB Laptop GPU
Expected speedup: 5-10x faster than CPU
```

**Note**: If you don't have an NVIDIA GPU, the system will automatically use CPU. GPU is optional but provides 5-10x performance improvement.

---

## Phase 2: Database Setup (5 minutes) 🗄️

- [ ] PostgreSQL service is running
- [ ] Created database named `attendance_db`
- [ ] Can connect to database

**Commands:**
```powershell
psql -U postgres
CREATE DATABASE attendance_db;
\q
```

**Verify:**
```powershell
psql -U postgres -l | findstr attendance_db
```

---

## Phase 3: Download Models (10 minutes) 🤖

- [ ] Created `backend/models/` directory
- [ ] Downloaded `scrfd_10g_bnkps.onnx`
- [ ] Downloaded `w600k_r50.onnx`
- [ ] Both files are in `backend/models/`

**See:** MODEL_DOWNLOAD.md for download instructions

**Verify:**
```powershell
dir backend\models\scrfd_10g_bnkps.onnx
dir backend\models\w600k_r50.onnx
```

---

## Phase 4: Backend Configuration (5 minutes) ⚙️

- [ ] Copied `.env.example` to `.env`
- [ ] Updated `DATABASE_URL` with correct password
- [ ] Model paths are correct in `.env`
- [ ] Settings are appropriate

**Commands:**
```powershell
cd backend
copy .env.example .env
notepad .env
```

**Update these lines in .env:**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/attendance_db
SCRFD_MODEL_PATH=models/scrfd_10g_bnkps.onnx
ARCFACE_MODEL_PATH=models/w600k_r50.onnx
```

---

## Phase 5: Initialize Database (2 minutes) 💾

- [ ] Activated conda environment
- [ ] Ran database initialization script
- [ ] All tables created successfully

**Commands:**
```powershell
conda activate face
cd backend
python scripts\init_db.py
```

**Success message should show:**
```
✓ Database tables created successfully!
Created tables:
  - students
  - attendance
  - cameras
  - admins
```

---

## Phase 6: Frontend Setup (5 minutes) 🎨

- [ ] Navigated to frontend directory
- [ ] Ran `npm install`
- [ ] All dependencies installed successfully
- [ ] No error messages

**Commands:**
```powershell
cd frontend
npm install
```

---

## Phase 7: Start Backend (2 minutes) 🚀

- [ ] Activated conda environment
- [ ] Started FastAPI server
- [ ] Server running on port 8000
- [ ] No error messages in terminal
- [ ] GPU acceleration confirmed in logs (if GPU available)

**Commands:**
```powershell
conda activate face
cd backend
python main.py
```

**You should see:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If GPU is enabled, you'll also see:**
```
✅ GPU acceleration ENABLED (CUDA)
SCRFD Detector initialized with input size: 640x640
✅ GPU acceleration ENABLED (CUDA)
ArcFace Recognizer initialized with input size: 112x112
```

**Test in browser:** http://localhost:8000/health

---

## Phase 8: Start Frontend (2 minutes) 🎨

- [ ] Opened new terminal
- [ ] Started Vite dev server
- [ ] Server running on port 3000
- [ ] No error messages

**Commands:**
```powershell
cd frontend
npm run dev
```

**You should see:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

**Test in browser:** http://localhost:3000

---

## Phase 9: First Login Test (2 minutes) 🔐

- [ ] Opened http://localhost:3000 in browser
- [ ] Can see homepage with two login cards
- [ ] Clicked "Admin Portal"
- [ ] Entered password: `admin123`
- [ ] Successfully logged into admin dashboard
- [ ] Can see Dashboard, Students, Cameras, etc. tabs

---

## Phase 10: Add Test Camera (2 minutes) 📹

- [ ] In Admin Dashboard, clicked "Cameras" tab
- [ ] Clicked "+ Add New Camera"
- [ ] Filled in:
  - Name: "Test Webcam"
  - IP Address: "0"
  - Location: "Testing"
- [ ] Successfully added camera
- [ ] Camera appears in list with "Active" status

---

## Phase 11: Add Test Student (5 minutes) 👤

- [ ] Clicked "Students" tab
- [ ] Clicked "+ Add New Student"
- [ ] Filled in student details:
  - Roll Number: "TEST001"
  - Name: "Test Student"
  - Email: "test@test.com"
  - Department: "Computer Science"
  - Year: 1
  - Section: "A"
- [ ] Clicked "Next: Capture Video"
- [ ] Allowed browser camera access
- [ ] Positioned face in camera
- [ ] Clicked "Start Capture"
- [ ] Waited for 50 frames to be captured
- [ ] Clicked "Complete Registration"
- [ ] Saw success message
- [ ] Student appears in students list

---

## Phase 12: Test Face Recognition (3 minutes) 🤖

- [ ] Clicked "Live Recognition" tab
- [ ] Selected "Test Webcam" from dropdown
- [ ] Clicked "Start Recognition"
- [ ] Showed face to camera
- [ ] System detected and recognized face
- [ ] Student name appeared in results
- [ ] Confidence score displayed
- [ ] "Attendance Marked" message shown

### Using DroidCam (Phone as Camera)

You can use your Android phone as the webcam via DroidCam:

1) On Windows: Install the DroidCam Client (Dev47Apps) and drivers; on Android: install the DroidCam app.
2) Connect phone and PC (Wi‑Fi or USB). Follow the client instructions until you see the phone feed in the Windows client.
3) Refresh the web app page and go to Live Recognition.
4) In the "Select Video Input" dropdown, choose the DroidCam device (it usually shows as "DroidCam Source" or similar).
5) Start recognition.

Note: If you prefer using the IP URL, add the DroidCam HTTP MJPEG URL (e.g., `http://<PHONE_IP>:4747/video`) in Cameras, but the current Live Recognition captures from the browser webcam. The camera dropdown only tags attendance to that camera ID; video is taken from the selected Video Input.

---

## Phase 13: Verify Attendance (2 minutes) ✅

- [ ] Clicked "Attendance" tab
- [ ] Selected today's date
- [ ] Can see attendance record for test student
- [ ] Shows correct time
- [ ] Shows camera name
- [ ] Shows confidence score

---

## Phase 14: Test Student Dashboard (2 minutes) 🎓

- [ ] Logged out of admin dashboard
- [ ] Returned to homepage
- [ ] Clicked "Student Portal"
- [ ] Entered roll number: "TEST001"
- [ ] Successfully logged in
- [ ] Can see:
  - Student name and details
  - Today's status (Present)
  - Attendance percentage
  - Attendance history

---

## Phase 15: Verification Complete! 🎉

Congratulations! If all checkboxes are checked, your system is fully functional!

### What You've Achieved:

✅ **Backend:**
- FastAPI server running
- Database connected
- Models loaded
- GPU acceleration enabled (5-10x faster)
- All services working

✅ **Frontend:**
- React app running
- Admin dashboard functional
- Student dashboard functional
- All features working

✅ **Face Recognition:**
- Detection working
- Recognition working
- Training working
- Attendance marking working

---

## Next Steps

Now that everything is working:

1. **Add Real Students:**
   - Register all students with proper details
   - Capture good quality training videos
   - Ensure 50+ frames per student

2. **Add Real Cameras:**
   - Configure your CCTV camera RTSP URLs
   - Test each camera individually
   - Activate only working cameras

3. **Customize Settings:**
   - Adjust recognition thresholds in `.env`
   - Modify admin password in `HomePage.jsx`
   - Configure camera FPS and resolution

4. **Test Thoroughly:**
   - Test with different students
   - Test with different lighting conditions
   - Test from different camera angles
   - Verify attendance accuracy

5. **Monitor Performance:**
   - Check recognition accuracy
   - Monitor system resources
   - Review attendance reports
   - Adjust settings as needed

---

## Troubleshooting

If any checkbox failed, see the relevant section in README.md:

- **GPU issues:** README.md > Troubleshooting > GPU Not Working
  - Run `python backend/check_gpu.py` to diagnose
  - Ensure ONNX Runtime GPU 1.19.2 is installed
  - Verify cuDNN is installed via conda
  - System will automatically fall back to CPU if GPU unavailable
- **Database issues:** README.md > Database Setup
- **Model issues:** MODEL_DOWNLOAD.md
- **Camera issues:** README.md > Troubleshooting > Camera Not Working
- **Recognition issues:** README.md > Troubleshooting > Low Recognition Accuracy

- **Windows psql code page warning:**

  If you see the message:

  > WARNING: Console code page (437) differs from Windows code page (1252)

  Run in PowerShell before starting `psql` to set the console code page to Windows-1252:

  ```powershell
  chcp 1252
  psql -U postgres
  ```

  Alternatively, to force UTF-8 for the session you can set:

  ```powershell
  $env:PGCLIENTENCODING = 'UTF8'
  psql -U postgres
  ```

---

## Daily Operation Checklist

Use this for daily startup:

### Morning Startup:
- [ ] Start PostgreSQL (if not running)
- [ ] Open Terminal 1: Start backend
- [ ] Open Terminal 2: Start frontend
- [ ] Open browser: Test http://localhost:3000
- [ ] Verify all cameras are active

### Throughout the Day:
- [ ] Monitor live recognition
- [ ] Check attendance records
- [ ] Handle any recognition errors
- [ ] Add new students if needed

### End of Day:
- [ ] Export attendance to CSV
- [ ] Review attendance statistics
- [ ] Backup database (weekly)
- [ ] Check system logs for errors

---

## Support Resources

- 📖 **Full Documentation:** README.md
- 🚀 **Quick Setup:** QUICKSTART.md
- 🤖 **Model Setup:** MODEL_DOWNLOAD.md
- 💻 **Commands:** COMMANDS.md
- 📁 **Structure:** PROJECT_STRUCTURE.md
- 📋 **Summary:** SUMMARY.md

---

**System Status:** [x] Development ✅ | [ ] Production Ready 🚀

**GPU Status:** [x] Enabled with NVIDIA RTX 3050 6GB 🚀

**Last Updated:** October 29, 2025

---

**Congratulations on completing the setup! 🎊**
