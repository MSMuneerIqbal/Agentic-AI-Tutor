#!/usr/bin/env python3
"""
Complete System Startup Script
Starts both Backend and Frontend together for Tutor GPT
"""

import subprocess
import time
import os
import sys
import signal
import threading
from pathlib import Path

class SystemStarter:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting Backend Server...")
        backend_dir = Path("backend")
        
        if not backend_dir.exists():
            print("❌ Backend directory not found!")
            return False
        
        try:
            # Start backend with uvicorn
            self.backend_process = subprocess.Popen(
                ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor backend output
            def monitor_backend():
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[BACKEND] {line.strip()}")
                    else:
                        break
            
            backend_thread = threading.Thread(target=monitor_backend)
            backend_thread.daemon = True
            backend_thread.start()
            
            # Wait for backend to start
            time.sleep(5)
            
            if self.backend_process.poll() is None:
                print("✅ Backend server started successfully!")
                return True
            else:
                print("❌ Backend server failed to start!")
                return False
                
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        print("🎨 Starting Frontend Server...")
        frontend_dir = Path("frontend")
        
        if not frontend_dir.exists():
            print("❌ Frontend directory not found!")
            return False
        
        try:
            # Check if node_modules exists, if not install dependencies
            if not (frontend_dir / "node_modules").exists():
                print("📦 Installing frontend dependencies...")
                install_process = subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True
                )
                
                if install_process.returncode != 0:
                    print(f"❌ Failed to install frontend dependencies: {install_process.stderr}")
                    return False
                print("✅ Frontend dependencies installed!")
            
            # Start frontend with npm dev
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitor frontend output
            def monitor_frontend():
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[FRONTEND] {line.strip()}")
                    else:
                        break
            
            frontend_thread = threading.Thread(target=monitor_frontend)
            frontend_thread.daemon = True
            frontend_thread.start()
            
            # Wait for frontend to start
            time.sleep(10)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend server started successfully!")
                return True
            else:
                print("❌ Frontend server failed to start!")
                return False
                
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking system dependencies...")
        
        # Check Python and uv
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python not found!")
            return False
        
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            print(f"✅ uv: {result.stdout.strip()}")
        except:
            print("❌ uv not found! Please install uv package manager.")
            return False
        
        # Check Node.js and npm
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except:
            print("❌ Node.js not found!")
            return False
        
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            print(f"✅ npm: {result.stdout.strip()}")
        except:
            print("❌ npm not found!")
            return False
        
        return True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down system...")
        self.running = False
        self.shutdown()
        sys.exit(0)
    
    def shutdown(self):
        """Shutdown both servers"""
        if self.backend_process:
            print("🛑 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("🛑 Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ System shutdown complete!")
    
    def run(self):
        """Run the complete system"""
        print("🎯 Tutor GPT - Complete System Startup")
        print("=" * 50)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Missing dependencies. Please install required tools.")
            return False
        
        print("\n🚀 Starting Tutor GPT System...")
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend. Exiting.")
            self.shutdown()
            return False
        
        print("\n" + "=" * 50)
        print("🎉 TUTOR GPT SYSTEM IS RUNNING!")
        print("=" * 50)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🔌 WebSocket: ws://localhost:8000/ws")
        print("=" * 50)
        print("Press Ctrl+C to stop the system")
        print("=" * 50)
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
                
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly!")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly!")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown()
        
        return True

def main():
    """Main function"""
    starter = SystemStarter()
    success = starter.run()
    
    if success:
        print("✅ System started successfully!")
        sys.exit(0)
    else:
        print("❌ System startup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
