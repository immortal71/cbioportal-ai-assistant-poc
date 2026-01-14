"""
Simple Test Runner - Starts server and runs all tests automatically
Just run: python run_all_tests.py
"""

import subprocess
import time
import sys
import signal
import httpx
from pathlib import Path

print("=" * 80)
print("🧪 COMPREHENSIVE TEST RUNNER")
print("=" * 80)

# Change to project directory
project_dir = Path(__file__).parent
print(f"\n📁 Project directory: {project_dir}")

# Kill any existing server on port 8000
print("\n🔪 Cleaning up any existing servers on port 8000...")
try:
    if sys.platform == "win32":
        subprocess.run("for /f \"tokens=5\" %a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %a", 
                      shell=True, capture_output=True, timeout=5)
    time.sleep(2)
except:
    pass

# Start the backend server
print("\n🚀 Starting backend server...")
server_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000"],
    cwd=project_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
)

# Wait for server to be ready
print("⏳ Waiting for server to start", end="", flush=True)
max_attempts = 20
for i in range(max_attempts):
    try:
        response = httpx.get("http://localhost:8000/health", timeout=1.0)
        if response.status_code == 200:
            print(" ✅")
            break
    except:
        pass
    print(".", end="", flush=True)
    time.sleep(0.5)
else:
    print(" ❌")
    print("\n❌ Server failed to start. Exiting...")
    server_process.kill()
    sys.exit(1)

print("✅ Server is ready!\n")

# Run the comprehensive tests
print("=" * 80)
print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
print("=" * 80 + "\n")

try:
    result = subprocess.run(
        [sys.executable, "test_comprehensive_llm.py"],
        cwd=project_dir
    )
    test_exit_code = result.returncode
except KeyboardInterrupt:
    print("\n\n⚠️  Tests interrupted by user")
    test_exit_code = 1

# Clean up - stop the server
print("\n\n🛑 Stopping backend server...")
try:
    if sys.platform == "win32":
        server_process.send_signal(signal.CTRL_BREAK_EVENT)
        time.sleep(1)
        server_process.kill()
    else:
        server_process.terminate()
        server_process.wait(timeout=5)
except:
    try:
        server_process.kill()
    except:
        pass

print("✅ Server stopped")

# Summary
print("\n" + "=" * 80)
if test_exit_code == 0:
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("📄 Check TEST_RESULTS.md for detailed results")
else:
    print("⚠️  Tests completed with some issues")
print("=" * 80)

sys.exit(test_exit_code)
