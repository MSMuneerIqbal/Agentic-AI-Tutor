#!/usr/bin/env python3
"""
Simple Startup Script for Tutor GPT System
Starts backend and frontend without complex dependency checking
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("=" * 80)
    print("🚀 TUTOR GPT - AI LEARNING PLATFORM")
    print("=" * 80)
    print("🎯 Starting Complete System")
    print("🔧 Backend: FastAPI + AI Agents + RAG + Tavily")
    print("🎨 Frontend: Next.js + React + Tailwind CSS")
    print("🤖 AI Models: 4 Gemini API Keys with Automatic Failover")
    print("=" * 80)

def start_backend():
    """Start the backend server."""
    print("\n🚀 Starting Backend Server...")
    
    backend_dir = Path(".")
    os.chdir(backend_dir)
    
    # Start uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    try:
        print("   ✅ Backend server starting on http://localhost:8000")
        print("   📚 API Docs will be available at http://localhost:8000/docs")
        
        # Start the process
        process = subprocess.Popen(cmd, shell=True)
        return process
        
    except Exception as e:
        print(f"   ❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server."""
    print("\n🎨 Starting Frontend Server...")
    
    frontend_dir = Path("../frontend")
    if not frontend_dir.exists():
        print("   ❌ Frontend directory not found")
        return None
    
    os.chdir(frontend_dir)
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("   📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm.cmd", "install"], check=True, shell=True)
            print("   ✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return None
    
    # Start Next.js development server
    try:
        print("   ✅ Frontend server starting on http://localhost:3000")
        
        # Start the process
        process = subprocess.Popen(["npm.cmd", "run", "dev"], shell=True)
        return process
        
    except Exception as e:
        print(f"   ❌ Failed to start frontend: {e}")
        return None

def monitor_process(process, name, color="🟢"):
    """Monitor a process and print its output."""
    if not process:
        return
    
    print(f"\n{color} {name} is running...")
    try:
        process.wait()
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping {name}...")
        process.terminate()

def show_system_info():
    """Show system information and URLs."""
    print("\n" + "=" * 80)
    print("🎉 SYSTEM STARTING!")
    print("=" * 80)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/healthz")
    print("=" * 80)
    print("🤖 AI Agents Available:")
    print("   • Tutor Agent - Personalized lessons")
    print("   • Planning Agent - Study plan creation")
    print("   • Assessment Agent - VARK learning style assessment")
    print("   • Quiz Agent - Knowledge testing")
    print("   • Orchestrator Agent - Flow management")
    print("   • Feedback Agent - System monitoring")
    print("=" * 80)
    print("🔑 Gemini API Keys: 4 keys configured with automatic failover")
    print("🧠 Models: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-2.0-flash, gemini-2.5-flash")
    print("=" * 80)
    print("📝 Press Ctrl+C to stop all services")
    print("=" * 80)

def main():
    """Main startup function."""
    print_banner()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server.")
        return False
    
    # Wait a moment for backend to start
    print("\n⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend server.")
        backend_process.terminate()
        return False
    
    # Show system information
    show_system_info()
    
    # Start monitoring threads
    backend_thread = threading.Thread(
        target=monitor_process, 
        args=(backend_process, "BACKEND", "🟢")
    )
    frontend_thread = threading.Thread(
        target=monitor_process, 
        args=(frontend_process, "FRONTEND", "🔵")
    )
    
    backend_thread.daemon = True
    frontend_thread.daemon = True
    
    backend_thread.start()
    frontend_thread.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
    
    finally:
        # Clean up processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Startup failed with error: {e}")
        import traceback
        traceback.print_exc()
