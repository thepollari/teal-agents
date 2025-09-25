import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

try:
    import keras
    print(f"Keras version: {keras.__version__}")
    
    version_parts = keras.__version__.split('.')
    major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
    
    if major > 3 or (major == 3 and minor > 11) or (major == 3 and minor == 11 and patch >= 0):
        print("✅ CVE-2025-9906 FIXED: Keras version includes security patch")
    else:
        print("❌ CVE-2025-9906 VULNERABLE: Keras version needs update")
        
except ImportError as e:
    print(f"❌ Keras not installed: {e}")
except Exception as e:
    print(f"❌ Error checking Keras: {e}")
