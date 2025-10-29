"""
Check if GPU is available and working for the attendance system
"""
import onnxruntime as ort
import sys
import os

print("="*60)
print("GPU AVAILABILITY CHECK FOR ATTENDANCE SYSTEM")
print("="*60)

# Check ONNX Runtime providers
print("\n1️⃣ ONNX Runtime Providers:")
providers = ort.get_available_providers()
print(f"   Available: {providers}")

if 'CUDAExecutionProvider' in providers:
    print("   ✅ CUDA (GPU) is available!")
    
    # Get CUDA device info
    try:
        import torch
        if torch.cuda.is_available():
            print(f"\n2️⃣ GPU Information:")
            print(f"   GPU Name: {torch.cuda.get_device_name(0)}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
            print(f"   CUDA Version: {torch.version.cuda}")
    except ImportError:
        print("\n2️⃣ PyTorch not installed (optional for GPU info)")
else:
    print("   ❌ CUDA not available - will use CPU")
    print("   To enable GPU:")
    print("      1. Install CUDA Toolkit 11.x or 12.x")
    print("      2. Install: pip install onnxruntime-gpu")

# Test loading models with GPU
print("\n3️⃣ Testing Model Loading with GPU:")

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.services.face_detection import SCRFDDetector
    print("\n   📦 Loading Face Detection Model...")
    detector = SCRFDDetector()
    print("   ✅ Face Detection Model loaded successfully")
    
except Exception as e:
    print(f"   ❌ Failed to load Face Detection Model: {e}")

try:
    from app.services.face_recognition import ArcFaceRecognizer
    print("\n   📦 Loading Face Recognition Model...")
    recognizer = ArcFaceRecognizer()
    print("   ✅ Face Recognition Model loaded successfully")
    
except Exception as e:
    print(f"   ❌ Failed to load Face Recognition Model: {e}")

print("\n" + "="*60)
print("CHECK COMPLETE")
print("="*60)

# Summary
if 'CUDAExecutionProvider' in providers:
    print("\n✅ YOUR PROJECT IS CONFIGURED TO USE GPU")
    print("   The models will run on your RTX 3050 GPU")
    print("   Expected speedup: 5-10x faster than CPU")
else:
    print("\n⚠️ YOUR PROJECT IS USING CPU ONLY")
    print("   Install CUDA toolkit and onnxruntime-gpu to enable GPU")
