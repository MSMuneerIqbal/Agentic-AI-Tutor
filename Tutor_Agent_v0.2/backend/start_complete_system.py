#!/usr/bin/env python3
"""
Complete System Startup Script
Starts both backend and frontend with monitoring and health checks
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def print_banner():
    """Print startup banner."""
    print("=" * 80)
    print("🚀 TUTOR GPT - AI LEARNING PLATFORM")
    print("=" * 80)
    print("🎯 Starting Complete System with Multiple Gemini API Keys")
    print("🔧 Backend: FastAPI + AI Agents + RAG + Tavily")
    print("🎨 Frontend: Next.js + React + Tailwind CSS")
    print("🤖 AI Models: Gemini 2.0 Flash, 1.5 Flash, 1.5 Pro")
    print("=" * 80)

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📋 Checking Dependencies...")
    
    # Check Python packages
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 
        'redis', 'pinecone-client', 'google-generativeai',
        'httpx', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Run: uv sync")
        return False
    
    # Check Node.js and npm
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Node.js {result.stdout.strip()}")
        else:
            print("   ❌ Node.js - NOT FOUND")
            return False
    except FileNotFoundError:
        print("   ❌ Node.js - NOT FOUND")
        return False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ npm {result.stdout.strip()}")
        else:
            print("   ❌ npm - NOT FOUND")
            return False
    except FileNotFoundError:
        print("   ❌ npm - NOT FOUND")
        return False
    
    print("   ✅ All dependencies found!")
    return True

def check_environment():
    """Check environment configuration."""
    print("\n🔧 Checking Environment Configuration...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file found")
    else:
        print("   ⚠️  .env file not found - using defaults")
    
    # Check API keys
    from app.core.config import get_settings
    try:
        settings = get_settings()
        print(f"   ✅ Settings loaded successfully")
        
        # Check Gemini API keys
        from app.core.gemini_manager import get_gemini_manager
        manager = get_gemini_manager()
        print(f"   ✅ Gemini Manager: {len(manager.api_keys)} API keys configured")
        print(f"   ✅ Available Models: {', '.join(manager.models)}")
        
    except Exception as e:
        print(f"   ❌ Settings error: {e}")
        return False
    
    return True

async def test_gemini_apis():
    """Test Gemini API connectivity."""
    print("\n🧠 Testing Gemini API Connectivity...")
    
    try:
        from app.core.gemini_manager import get_gemini_manager
        
        manager = get_gemini_manager()
        
        # Test content generation
        print("   Testing content generation...")
        response = await manager.generate_content_with_failover("Hello, this is a test.")
        
        if response:
            print("   ✅ Content generation working")
        else:
            print("   ❌ Content generation failed")
            return False
        
        # Test embedding generation
        print("   Testing embedding generation...")
        embedding = await manager.generate_embedding_with_failover("Test embedding")
        
        if embedding:
            print("   ✅ Embedding generation working")
        else:
            print("   ❌ Embedding generation failed")
            return False
        
        # Show usage report
        report = manager.get_usage_report()
        print(f"   ✅ Active API Keys: {report['available_keys']}/{report['total_keys']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Gemini API test failed: {e}")
        return False

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
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("   ✅ Backend server starting on http://localhost:8000")
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
    
    # Install dependencies if needed
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("   📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True)
            print("   ✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return None
    
    # Start Next.js development server
    cmd = ["npm", "run", "dev"]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("   ✅ Frontend server starting on http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"   ❌ Failed to start frontend: {e}")
        return None

def monitor_process(process, name, color="🟢"):
    """Monitor a process and print its output."""
    if not process:
        return
    
    print(f"\n{color} {name} Output:")
    print("-" * 50)
    
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.strip()}")
    except Exception as e:
        print(f"Error monitoring {name}: {e}")

def wait_for_services():
    """Wait for services to be ready."""
    print("\n⏳ Waiting for services to be ready...")
    
    import requests
    import time
    
    # Wait for backend
    backend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/healthz", timeout=2)
            if response.status_code == 200:
                backend_ready = True
                print("   ✅ Backend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not backend_ready:
        print("   ⚠️  Backend not ready after 30 seconds")
    
    # Wait for frontend
    frontend_ready = False
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:3000", timeout=2)
            if response.status_code == 200:
                frontend_ready = True
                print("   ✅ Frontend is ready")
                break
        except:
            pass
        time.sleep(1)
    
    if not frontend_ready:
        print("   ⚠️  Frontend not ready after 30 seconds")
    
    return backend_ready and frontend_ready

def show_system_info():
    """Show system information and URLs."""
    print("\n" + "=" * 80)
    print("🎉 SYSTEM READY!")
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
    print("🧠 Models: gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro")
    print("=" * 80)
    print("📝 Press Ctrl+C to stop all services")
    print("=" * 80)

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print("\n\n🛑 Shutting down services...")
    sys.exit(0)

async def main():
    """Main startup function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        return False
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please check your configuration.")
        return False
    
    # Test Gemini APIs
    if not await test_gemini_apis():
        print("\n❌ Gemini API test failed. Please check your API keys.")
        return False
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend server.")
        return False
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n❌ Failed to start frontend server.")
        backend_process.terminate()
        return False
    
    # Wait for services to be ready
    services_ready = wait_for_services()
    
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
    asyncio.run(main())
