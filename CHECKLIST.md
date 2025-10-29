# Setup Checklist ✅

Follow this checklist step-by-step to get your system running.

## Phase 1: Prerequisites ✅

- [ ] Conda environment `face` exists
- [ ] All packages from requirements.txt are installed
- [ ] PostgreSQL is installed and running
- [ ] Node.js 16+ is installed
 - [x] Conda environment `face` exists
 - [ ] All packages from requirements.txt are installed
 - [x] PostgreSQL is installed and running
 - [x] Node.js 16+ is installed (tested with v22.21.0)
- [ ] You have internet access to download models

**Commands to verify:**
```powershell
conda activate face
python --version
node --version
psql --version
```

### Observed environment (from user session)

- Conda environment activated: `face` (via `conda activate face`)
- Python: Python 3.10.0
- Node: v22.21.0
- psql: PostgreSQL 15.14 (psql client)

When the user connected to `psql` they saw a console warning about differing Windows console code pages (see Troubleshooting below).

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

**System Status:** [ ] Development ✅ | [ ] Production Ready 🚀

**Last Updated:** $(Get-Date -Format "yyyy-MM-dd")

---

**Congratulations on completing the setup! 🎊**
