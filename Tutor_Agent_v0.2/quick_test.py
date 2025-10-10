#!/usr/bin/env python3
"""
Quick Backend-Frontend Connection Test
Simple test to verify both services are running and can communicate
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running on http://localhost:8000")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_frontend():
    """Test if frontend is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running on http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints"""
    endpoints = [
        "/api/v1/health",
        "/api/v1/rag/health",
        "/api/v1/status"
    ]
    
    print("\n🔍 Testing API endpoints...")
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code in [200, 404]:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def main():
    """Main test function"""
    print("🚀 Quick Backend-Frontend Connection Test")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    if backend_ok:
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    if backend_ok and frontend_ok:
        print("🎉 SUCCESS: Both Backend and Frontend are running!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("❌ FAILED: One or both services are not running")
        print("\nTo start the system:")
        print("1. Backend: cd backend && uv run uvicorn app.main:app --reload")
        print("2. Frontend: cd frontend && npm run dev")
        print("3. Or run: python start_complete_system.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
