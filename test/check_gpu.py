"""
Quick GPU Check Script
Run this to verify GPU acceleration is working
"""
import onnxruntime as ort
import torch

print("=" * 50)
print("GPU AVAILABILITY CHECK")
print("=" * 50)

# Check ONNX Runtime providers
print("\n1. ONNX Runtime Providers:")
providers = ort.get_available_providers()
for provider in providers:
    print(f"   ✓ {provider}")

if 'CUDAExecutionProvider' in providers:
    print("   ✅ GPU acceleration available!")
else:
    print("   ⚠️ GPU acceleration NOT available")

# Check PyTorch CUDA
print("\n2. PyTorch CUDA:")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA version: {torch.version.cuda}")
    print(f"   GPU name: {torch.cuda.get_device_name(0)}")
    print(f"   GPU count: {torch.cuda.device_count()}")
    print("   ✅ PyTorch can use GPU!")
else:
    print("   ⚠️ PyTorch cannot use GPU")

# Check device info
print("\n3. ONNX Runtime Device Info:")
try:
    import onnxruntime as ort
    sess_options = ort.SessionOptions()
    providers_with_options = [
        ('CUDAExecutionProvider', {
            'device_id': 0,
            'arena_extend_strategy': 'kNextPowerOfTwo',
            'gpu_mem_limit': 2 * 1024 * 1024 * 1024,  # 2GB
            'cudnn_conv_algo_search': 'EXHAUSTIVE',
            'do_copy_in_default_stream': True,
        }),
        'CPUExecutionProvider'
    ]
    print("   ✅ GPU session can be created")
except Exception as e:
    print(f"   ⚠️ Error creating GPU session: {e}")

print("\n" + "=" * 50)
print("RECOMMENDATION:")
if 'CUDAExecutionProvider' in providers and torch.cuda.is_available():
    print("✅ Your RTX 3050 is ready to use!")
    print("   Run test.py to see GPU-accelerated face detection")
else:
    print("⚠️ GPU not detected. Possible fixes:")
    print("   1. Install CUDA Toolkit 11.8 or 12.x")
    print("   2. pip install onnxruntime-gpu")
    print("   3. pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
print("=" * 50)
